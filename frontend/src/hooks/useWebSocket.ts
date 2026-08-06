import { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';
import type { Message } from '@/data/mockData';
import { getMessagesForConversation } from '@/data/mockData';

export interface WebSocketHook {
  messages: Message[];
  sendMessage: (content: string) => void;
  isConnected: boolean;
}

export function useWebSocket(conversationId: string | undefined): WebSocketHook {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const token = useAuthStore((s) => s.token);

  // Load initial messages
  useEffect(() => {
    if (conversationId) {
      setMessages(getMessagesForConversation(conversationId));
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  // WebSocket connection logic (mocked for now)
  useEffect(() => {
    if (!conversationId || !token) {
      return;
    }

    // TODO: Implement actual WS connection when backend is ready
    // const wsUrl = `ws://localhost:8000/api/v1/ws/chat/${conversationId}?token=${token}`;
    // ws.current = new WebSocket(wsUrl);
    // ws.current.onopen = () => setIsConnected(true);
    // ws.current.onclose = () => setIsConnected(false);
    // ws.current.onmessage = (e) => { ... parse and setMessages ... }
    
    setIsConnected(true); // Mock connected state
    
    return () => {
      // ws.current?.close();
      setIsConnected(false);
    };
  }, [conversationId, token]);

  const sendMessage = useCallback((content: string) => {
    if (!conversationId) return;
    
    // Optimistic update
    const newMessage: Message = {
      id: `msg-${Date.now()}`,
      conversationId,
      content,
      isSent: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      type: 'user'
    };
    
    setMessages(prev => [...prev, newMessage]);

    // Simulate backend response
    setTimeout(() => {
      const replies = [
        "That's interesting! Tell me more 🤔",
        "Got it, thanks! 👍",
        "I'll check that out right away!",
        "Sounds good to me! 😊",
        "Let me think about that...",
      ];
      const replyMessage: Message = {
        id: `msg-reply-${Date.now()}`,
        conversationId,
        content: replies[Math.floor(Math.random() * replies.length)],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isSent: false,
        type: 'contact'
      };
      setMessages((prev) => [...prev, replyMessage]);
    }, 1000 + Math.random() * 2000);

  }, [conversationId]);

  return { messages, sendMessage, isConnected };
}
