import { mockConversations, getMessagesForConversation } from '@/data/mockData';
import type { Conversation, Message } from '@/data/mockData';

/**
 * Conversations API client.
 * Currently wraps mock data behind async functions.
 * When backend M1-BE-04 is ready, swap to real apiClient calls.
 */
export const conversationsApi = {
  /** Get all conversations for current user */
  getConversations: async (): Promise<Conversation[]> => {
    // TODO: Replace with apiClient.get('/conversations')
    await simulateDelay(300);
    return mockConversations;
  },

  /** Get messages for a specific conversation */
  getMessages: async (conversationId: string): Promise<Message[]> => {
    // TODO: Replace with apiClient.get(`/conversations/${conversationId}/messages`)
    await simulateDelay(200);
    return getMessagesForConversation(conversationId);
  },

  /** Send a message in a conversation */
  sendMessage: async (conversationId: string, content: string): Promise<Message> => {
    // TODO: Replace with apiClient.post(`/conversations/${conversationId}/messages`, { content })
    await simulateDelay(100);
    const message: Message = {
      id: `msg-${Date.now()}`,
      conversationId,
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isSent: true,
      type: 'user',
    };
    return message;
  },

  /** Create a new conversation with a contact */
  createConversation: async (contactName: string): Promise<Conversation> => {
    // TODO: Replace with apiClient.post('/conversations', { contact_id })
    await simulateDelay(200);
    const conversation: Conversation = {
      id: `conv-${Date.now()}`,
      name: contactName,
      lastMessage: '',
      timestamp: 'Just now',
      unread: 0,
      online: false,
    };
    return conversation;
  },
};

/** Simulate network delay for mock data */
function simulateDelay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
