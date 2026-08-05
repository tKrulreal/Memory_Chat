import { useEffect, useRef } from 'react';
import { ChatHeader } from './ChatHeader';
import { ChatInput } from './ChatInput';
import { MessageBubble } from './MessageBubble';
import { Avatar } from '../common/Avatar';
import type { Conversation } from '@/data/mockData';
import { useWebSocket } from '@/hooks/useWebSocket';

interface ChatWindowProps {
  conversation: Conversation;
}

export function ChatWindow({ conversation }: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage } = useWebSocket(conversation.id);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (content: string) => {
    sendMessage(content);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background">
      <ChatHeader conversation={conversation} />

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 messenger-scrollbar">
        {/* Conversation start indicator */}
        <div className="flex flex-col items-center mb-8 pt-4">
          <Avatar name={conversation.name} size="lg" online={conversation.online} />
          <h4 className="text-lg font-bold text-text-primary mt-3">{conversation.name}</h4>
          <p className="text-xs text-text-tertiary mt-1">
            You're connected on MemoryChat
          </p>
        </div>

        {/* Messages */}
        {messages.map((msg, index) => {
          const next = messages[index + 1];
          const isLastInGroup = !next || next.isSent !== msg.isSent;

          return (
            <div key={msg.id} className="flex items-end gap-2">
              {/* Show avatar for received messages at end of group */}
              {!msg.isSent && isLastInGroup ? (
                <Avatar name={msg.senderName || conversation.name} size="sm" className="mb-5" />
              ) : !msg.isSent ? (
                <div className="w-8" /> // Spacer to align messages
              ) : null}
              <div className="flex-1">
                <MessageBubble message={msg} isLastInGroup={isLastInGroup} />
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  );
}
