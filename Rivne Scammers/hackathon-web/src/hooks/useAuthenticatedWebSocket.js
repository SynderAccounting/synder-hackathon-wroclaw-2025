import { useCallback, useEffect, useRef, useState } from 'react';
import { toast } from 'react-toastify';

import { useAuth } from './useAuth';

const buildWsUrl = (token) => {
  const base = (import.meta.env.VITE_WS_URL || 'ws://localhost:8000').replace(/\/$/, '');
  const url = `${base}/ws/dashboard?token=${encodeURIComponent(token)}`;
  return url;
};

const showNotificationForEvent = (event) => {
  switch (event.type) {
    case 'connection_established':
      break;
    case 'order_created':
      toast.info(`🛒 New Order #${event.data?.order_number ?? ''}`.trim(), {
        autoClose: 5000,
        onClick: () => {
          if (event.data?.id) {
            window.location.href = `/orders/${event.data.id}`;
          }
        },
      });
      break;
    case 'order_updated':
      toast.info(
        `📦 Order #${event.data?.order_number ?? ''} updated: ${event.data?.status ?? ''}`.trim(),
        { autoClose: 4000 },
      );
      break;
    case 'inventory_low':
      toast.warning(
        `⚠️ Low Stock: ${event.data?.product_name ?? ''} (${event.data?.available_quantity ?? ''} left)`,
        { autoClose: 7000 },
      );
      break;
    case 'inventory_updated':
      break;
    case 'recommendation_new':
      toast.success('💡 New recommendation available', { autoClose: 5000 });
      break;
    case 'warning':
      toast.warn(event.message ?? 'Real-time updates unavailable');
      break;
    default:
      break;
  }
};

export const useAuthenticatedWebSocket = (onMessage, authContext, options = {}) => {
  const { enabled = true } = options;
  const auth = authContext ?? useAuth();
  const { isAuthenticated, token } = auth;

  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    if (!enabled || !isAuthenticated || !token) {
      return;
    }

    const wsUrl = buildWsUrl(token);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      reconnectAttempts.current = 0;
      toast.success('Connected to real-time updates', { autoClose: 2000 });
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
        showNotificationForEvent(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message', error);
      }
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      if (!enabled || !isAuthenticated) {
        return;
      }
      if (reconnectAttempts.current >= 5) {
        toast.error('Failed to reconnect to real-time updates');
        return;
      }
      const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 10000);
      reconnectAttempts.current += 1;
      reconnectTimeout.current = setTimeout(connect, delay);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error', error);
      toast.error('Connection error. Retrying...');
    };
  }, [enabled, isAuthenticated, onMessage, token]);

  const sendMessage = useCallback((data) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    if (enabled && isAuthenticated && token) {
      connect();
    }

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect, enabled, isAuthenticated, token]);

  useEffect(() => {
    if (!enabled || !isConnected) {
      return;
    }
    const interval = setInterval(() => {
      sendMessage({ type: 'ping' });
    }, 30000);
    return () => clearInterval(interval);
  }, [isConnected, sendMessage]);

  return {
    isConnected,
    sendMessage,
  };
};
