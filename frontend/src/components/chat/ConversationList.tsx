import { useState, useMemo } from 'react';
import { SearchBar } from '../common/SearchBar';
import { ConversationItem } from './ConversationItem';
import type { Conversation } from '@/data/mockData';

interface ConversationListProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
}

export function ConversationList({
  conversations,
  activeConversationId,
  onSelectConversation,
}: ConversationListProps) {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search) return conversations;
    const q = search.toLowerCase();
    return conversations.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.lastMessage.toLowerCase().includes(q)
    );
  }, [conversations, search]);

  return (
    <div className="w-[340px] min-w-[280px] h-full flex flex-col border-r border-divider bg-sidebar-bg">
      {/* Header */}
      <div className="px-4 pt-5 pb-3">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-text-primary">Chats</h2>
          <div className="flex items-center gap-1">
            {/* New chat button */}
            <button className="w-9 h-9 rounded-full bg-secondary hover:bg-accent flex items-center justify-center transition-colors" title="New chat">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5" className="text-text-primary">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
              </svg>
            </button>
            {/* More options */}
            <button className="w-9 h-9 rounded-full bg-secondary hover:bg-accent flex items-center justify-center transition-colors" title="Options">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5" className="text-text-primary">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM12.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0zM18.75 12a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" />
              </svg>
            </button>
          </div>
        </div>
        <SearchBar value={search} onChange={setSearch} />
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-2 pb-2 messenger-scrollbar">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-text-tertiary">
            <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1" className="mb-3 opacity-50">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <p className="text-sm">No conversations found</p>
          </div>
        ) : (
          filtered.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              isActive={conversation.id === activeConversationId}
              onClick={() => onSelectConversation(conversation.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}
