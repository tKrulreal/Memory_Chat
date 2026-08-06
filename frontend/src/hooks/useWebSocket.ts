import { useCallback, useEffect, useRef, useState } from 'react';

import { useAuthStore } from '@/stores/authStore';

interface Message {
  id: string;
  conversationId: string;
  content: string;
  isSent: boolean;
  timestamp: string;
  type: 'user' | 'contact' | 'ai';
}

interface WebSocketMessage {
  id: string;
  conversation_id: string;
  content: string;
  role: 'USER' | 'CONTACT' | 'AI';
  created_at: string;
}

export interface WebSocketHook {
  messages: Message[];
  sendMessage: (content: string) => void;
  isConnected: boolean;
}

const reconnectDelay = (attempt: number) => Math.min(1000 * 2 ** attempt, 10_000);

export function useWebSocket(conversationId: string | undefined): WebSocketHook {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const reconnectAttemptRef = useRef(0);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    setMessages([]);
    if (!conversationId || !token) {
      return;
    }

    let disposed = false;
    const connect = () => {
      const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const baseUrl = import.meta.env.VITE_WS_URL ?? `${scheme}://localhost:8000`;
      const socket = new WebSocket(`${baseUrl}/ws/chat/${conversationId}?token=${encodeURIComponent(token)}`);
      socketRef.current = socket;

      socket.onopen = () => {
        reconnectAttemptRef.current = 0;
        setIsConnected(true);
      };
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data) as WebSocketMessage | { type: string };
        if ('type' in payload && payload.type === 'ping') {
          socket.send(JSON.stringify({ type: 'pong' }));
          return;
        }
        if (!('conversation_id' in payload)) {
          return;
        }
        const message: Message = {
          id: payload.id,
          conversationId: payload.conversation_id,
          content: payload.content,
          isSent: payload.role === 'USER',
          timestamp: new Date(payload.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          type: payload.role.toLowerCase() as Message['type'],
        };
        setMessages((previous) => previous.some((item) => item.id === message.id) ? previous : [...previous, message]);
      };
      socket.onclose = () => {
        setIsConnected(false);
        if (!disposed) {
          reconnectTimerRef.current = window.setTimeout(connect, reconnectDelay(reconnectAttemptRef.current++));
        }
      };
    };

    connect();
    return () => {
      disposed = true;
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      socketRef.current?.close();
      socketRef.current = null;
      setIsConnected(false);
    };
  }, [conversationId, token]);

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN && content.trim()) {
      socketRef.current.send(JSON.stringify({ content }));
    }
  }, []);

  return { messages, sendMessage, isConnected };
}
