import { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { ConversationList } from './ConversationList';
import { ChatWindow } from './ChatWindow';
import { EmptyChat } from './EmptyChat';
import { ContextCard } from './ContextCard';
import { conversationsApi } from '@/api/conversations';
import type { Conversation } from '@/data/mockData';
import { mockContactContexts } from '@/data/mockData';

export function ChatLayout() {
  const [activeTab, setActiveTab] = useState('chats');
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadConversations() {
      try {
        const data = await conversationsApi.getConversations();
        setConversations(data);
      } catch (error) {
        console.error("Failed to load conversations:", error);
      } finally {
        setLoading(false);
      }
    }
    loadConversations();
  }, []);

  const activeConversation = conversations.find((c) => c.id === activeConversationId);
  const activeContext = activeConversationId ? mockContactContexts[activeConversationId] || null : null;

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-background">
      {/* Left Icon Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Conversation List */}
      <ConversationList
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
      />

      {/* Chat Window or Empty State */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center text-text-tertiary">Loading conversations...</div>
      ) : activeConversation ? (
        <>
          <ChatWindow conversation={activeConversation} />
          <ContextCard context={activeContext} />
        </>
      ) : (
        <EmptyChat />
      )}
    </div>
  );
}
