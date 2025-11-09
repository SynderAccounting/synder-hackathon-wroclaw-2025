'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Trash2, Plus } from 'lucide-react';
import { MainLayout } from '@/components/layout/main-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useAuthStore } from '@/stores/auth-store';
import { ChatChart } from '@/components/chat/chat-chart';

interface PlotData {
  type: 'pie' | 'bar' | 'line' | 'horizontal_bar';
  data: Array<[string, number]>;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  isStreaming?: boolean;
  plotData?: PlotData;
  toolCalls?: Array<{
    tool_name: string;
    parameters: any;
    result?: string;
  }>;
}

interface ChatSession {
  id: string;
  title: string;
  updated_at: string;
  message_count?: number;
}

export default function ChatPage() {
  const { user } = useAuthStore();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const clientIdRef = useRef<string>(`client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Connect to WebSocket when session is selected
  useEffect(() => {
    if (currentSessionId && user) {
      connectWebSocket();
    }
    return () => {
      disconnectWebSocket();
    };
  }, [currentSessionId, user]);

  const loadSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/sessions', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setSessions(data);

        // If no current session and sessions exist, select the first one
        if (!currentSessionId && data.length > 0) {
          await selectSession(data[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          title: `Chat ${new Date().toLocaleString()}`,
        }),
      });

      if (response.ok) {
        const newSession = await response.json();
        setSessions((prev) => [newSession, ...prev]);
        await selectSession(newSession.id);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const selectSession = async (sessionId: string) => {
    try {
      // Load messages for the session
      const response = await fetch(`http://localhost:8000/api/v1/chat/sessions/${sessionId}`, {
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Loaded session data:', data);
        console.log('Messages:', data.messages);

        const loadedMessages: Message[] = data.messages.map((msg: any) => {
          console.log('Processing message:', msg);
          console.log('Message message_metadata:', msg.message_metadata);
          console.log('Plot data:', msg.message_metadata?.plot_data);

          return {
            id: msg.id,
            text: msg.content,
            sender: msg.role === 'user' ? 'user' : 'bot',
            timestamp: new Date(msg.created_at),
            plotData: msg.message_metadata?.plot_data || undefined,
          };
        });

        console.log('Final loaded messages:', loadedMessages);
        setMessages(loadedMessages);
        setCurrentSessionId(sessionId);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const deleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();

    if (!confirm('Are you sure you want to delete this chat session?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat/sessions/${sessionId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (response.ok) {
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));

        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          setMessages([]);
          disconnectWebSocket();
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(`ws://localhost:8000/api/v1/chat/ws/${clientIdRef.current}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    wsRef.current = ws;
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'bot_response_start':
        // Start a new bot message
        setMessages((prev) => [
          ...prev,
          {
            id: `temp-${Date.now()}`,
            text: '',
            sender: 'bot',
            timestamp: new Date(),
            isStreaming: true,
            toolCalls: [],
          },
        ]);
        break;

      case 'bot_token':
        // Append token to the last bot message
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage && lastMessage.sender === 'bot') {
            lastMessage.text += data.token;
          }
          return newMessages;
        });
        break;

      case 'bot_tool':
        // Add tool call to the last bot message
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage && lastMessage.sender === 'bot') {
            lastMessage.toolCalls = lastMessage.toolCalls || [];
            lastMessage.toolCalls.push({
              tool_name: data.tool_name,
              parameters: data.parameters,
            });
          }
          return newMessages;
        });
        break;

      case 'bot_tool_result':
        // Add result to the last tool call
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage && lastMessage.sender === 'bot' && lastMessage.toolCalls) {
            const lastTool = lastMessage.toolCalls[lastMessage.toolCalls.length - 1];
            if (lastTool && lastTool.tool_name === data.tool_name) {
              lastTool.result = data.result;
            }
          }
          return newMessages;
        });
        break;

      case 'bot_response_end':
        // Mark streaming complete
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage && lastMessage.sender === 'bot') {
            lastMessage.isStreaming = false;
            lastMessage.id = data.message_id || lastMessage.id;
          }
          return newMessages;
        });
        setIsLoading(false);
        // Reload sessions to update message count
        loadSessions();
        break;

      case 'plot_created':
        // Add a new message with plot data
        // Note: The data.error field seems misnamed - it actually contains the plot data
        const plotData: PlotData = {
          type: data.error?.type || 'pie',
          data: data.error?.data || [],
        };

        setMessages((prev) => [
          ...prev,
          {
            id: `plot-${Date.now()}`,
            text: '', // No text for plot-only messages
            sender: 'bot',
            timestamp: new Date(),
            plotData,
          },
        ]);
        break;

      case 'bot_error':
        console.error('Bot error:', data.error);
        setIsLoading(false);
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            text: `Error: ${data.error}`,
            sender: 'bot',
            timestamp: new Date(),
          },
        ]);
        break;

      case 'history_cleared':
        setMessages([]);
        break;
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !currentSessionId || !user) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Send message via WebSocket
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'user_message',
        session_id: currentSessionId,
        message: inputValue,
        user_id: user.id,
      }));
    } else {
      setIsLoading(false);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          text: 'Error: Not connected to chat server. Please try again.',
          sender: 'bot',
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="flex h-[calc(100vh-4rem)] gap-4">
          {/* Sidebar - Sessions List */}
          <div className="w-64 flex flex-col">
            <div className="mb-4">
              <Button
                onClick={createNewSession}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Chat
              </Button>
            </div>

            <Card className="flex-1 overflow-y-auto p-2">
              <div className="space-y-1">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => selectSession(session.id)}
                    className={`p-3 rounded-lg cursor-pointer flex items-center justify-between group ${
                      currentSessionId === session.id
                        ? 'bg-blue-100 dark:bg-blue-900'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 flex-shrink-0" />
                        <p className="text-sm font-medium truncate">
                          {session.title}
                        </p>
                      </div>
                      {session.message_count !== undefined && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 ml-6">
                          {session.message_count} messages
                        </p>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => deleteSession(session.id, e)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col">
            <div className="mb-4">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Chat Assistant
              </h1>
              <div className="flex items-center gap-2 mt-2">
                <p className="text-gray-600 dark:text-gray-400">
                  Ask questions about your retail data and get instant insights
                </p>
                <span
                  className={`px-2 py-1 rounded-full text-xs ${
                    isConnected
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}
                >
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>

            {currentSessionId ? (
              <Card className="flex-1 flex flex-col overflow-hidden">
                {/* Messages Container */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 && (
                    <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
                      <p>Start a conversation by sending a message below</p>
                    </div>
                  )}

                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.sender === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`${
                          message.plotData ? 'w-full max-w-4xl' : 'max-w-[70%]'
                        } rounded-lg ${
                          message.plotData && !message.text ? '' : 'px-4 py-2'
                        } ${
                          message.sender === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                        }`}
                      >
                        {message.text && (
                          <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                        )}

                        {/* Plot/Chart Display */}
                        {message.plotData && (
                          <ChatChart plotData={message.plotData} />
                        )}

                        {/* Tool Calls Display */}
                        {message.toolCalls && message.toolCalls.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {message.toolCalls
                              .filter((tool) => !tool.result || !tool.result.toLowerCase().startsWith('error'))
                              .map((tool, idx) => (
                                <div
                                  key={idx}
                                  className="text-xs bg-white/10 rounded p-2"
                                >
                                  <div className="font-semibold">🔧 {tool.tool_name}</div>
                                  {tool.result && (
                                    <div className="mt-1 opacity-75">
                                      Result: {tool.result.substring(0, 100)}
                                      {tool.result.length > 100 && '...'}
                                    </div>
                                  )}
                                </div>
                              ))
                            }
                          </div>
                        )}

                        <span
                          className={`text-xs mt-1 block ${
                            message.sender === 'user'
                              ? 'text-blue-100'
                              : 'text-gray-500 dark:text-gray-400'
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                    </div>
                  ))}

                  {/* Streaming Indicator */}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div
                            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                            style={{ animationDelay: '0.1s' }}
                          ></div>
                          <div
                            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                            style={{ animationDelay: '0.2s' }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                  <div className="flex space-x-2">
                    <Input
                      type="text"
                      placeholder="Type your message..."
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      disabled={!isConnected || isLoading}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputValue.trim() || !isConnected || isLoading}
                      className="px-4"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ) : (
              <Card className="flex-1 flex items-center justify-center">
                <div className="text-center text-gray-500 dark:text-gray-400">
                  <MessageSquare className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">No chat selected</p>
                  <p className="text-sm mt-2">Create a new chat or select an existing one</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
