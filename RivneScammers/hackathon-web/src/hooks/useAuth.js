import { useEffect, useState } from 'react';
import { getToken as readStoredToken, clearToken as removeStoredToken, setTokenCookie } from '../api/auth';

const decodeJwt = (token) => {
  try {
    if (!token) return null;
    const [, payload = ''] = token.split('.');
    if (!payload) return null;

    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(normalized.length + (4 - (normalized.length % 4 || 4)) % 4, '=');
    const decoded = atob(padded);
    return JSON.parse(decoded);
  } catch (error) {
    console.error('Failed to decode JWT payload', error);
    return null;
  }
};

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = typeof readStoredToken === 'function' ? readStoredToken() : null;

    if (!storedToken) {
      setLoading(false);
      return;
    }

    const payload = decodeJwt(storedToken);
    if (!payload) {
      if (typeof removeStoredToken === 'function') {
        removeStoredToken();
      }
      setLoading(false);
      return;
    }

    const expiresAt = payload.exp ? payload.exp * 1000 : null;
    if (expiresAt && expiresAt < Date.now()) {
      if (typeof removeStoredToken === 'function') {
        removeStoredToken();
      }
      setLoading(false);
      return;
    }

    setToken(storedToken);
    setIsAuthenticated(true);
    setUser({
      id: payload.sub || payload.user_id || payload.id,
      email: payload.email,
      name: payload.name || payload.username,
      roles: payload.roles,
    });
    setLoading(false);
  }, []);

  const applyToken = (nextToken) => {
    const payload = decodeJwt(nextToken);
    if (!payload) {
      return;
    }
    setToken(nextToken);
    setIsAuthenticated(true);
    setUser({
      id: payload.sub || payload.user_id || payload.id,
      email: payload.email,
      name: payload.name || payload.username,
      roles: payload.roles,
    });
  };

  const login = (nextToken, { remember = true } = {}) => {
    if (!nextToken) return;
    try {
      if (remember) {
        localStorage.setItem('auth_token', nextToken);
      } else {
        localStorage.removeItem('auth_token');
      }
      if (typeof setTokenCookie === 'function') {
        setTokenCookie(nextToken, remember);
      }
    } catch (error) {
      console.error('Failed to persist auth token', error);
    }
    applyToken(nextToken);
  };

  const logout = () => {
    if (typeof removeStoredToken === 'function') {
      removeStoredToken();
    }
    try {
      localStorage.removeItem('auth_token');
    } catch {
      // ignore storage errors
    }
    setToken(null);
    setIsAuthenticated(false);
    setUser(null);
  };

  return {
    isAuthenticated,
    user,
    token,
    loading,
    login,
    logout,
  };
};
