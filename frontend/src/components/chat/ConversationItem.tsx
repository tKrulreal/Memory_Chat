import { Avatar } from '../common/Avatar';
import type { Conversation } from '@/data/mockData';

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
}

export function ConversationItem({ conversation, isActive, onClick }: ConversationItemProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg conversation-item text-left ${
        isActive
          ? 'bg-conversation-active'
          : 'hover:bg-conversation-hover'
      }`}
    >
      <Avatar
        name={conversation.name}
        src={conversation.avatar}
        size="lg"
        online={conversation.online}
      />
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className={`text-sm font-semibold truncate ${
            conversation.unread > 0 ? 'text-text-primary' : 'text-text-primary'
          }`}>
            {conversation.name}
          </span>
          <span className={`text-xs flex-shrink-0 ml-2 ${
            conversation.unread > 0 ? 'text-messenger-blue font-semibold' : 'text-text-tertiary'
          }`}>
            {conversation.timestamp}
          </span>
        </div>
        
        <div className="flex items-center justify-between mt-0.5">
          <p className={`text-xs truncate ${
            conversation.unread > 0 ? 'text-text-primary font-medium' : 'text-text-secondary'
          }`}>
            {conversation.isTyping ? (
              <span className="flex items-center gap-1 text-messenger-blue">
                <span className="flex gap-0.5">
                  <span className="w-1 h-1 bg-messenger-blue rounded-full typing-dot" />
                  <span className="w-1 h-1 bg-messenger-blue rounded-full typing-dot" />
                  <span className="w-1 h-1 bg-messenger-blue rounded-full typing-dot" />
                </span>
                typing...
              </span>
            ) : (
              conversation.lastMessage
            )}
          </p>
          
          {conversation.unread > 0 && (
            <span className="flex-shrink-0 ml-2 w-5 h-5 bg-unread-badge rounded-full flex items-center justify-center text-white text-[10px] font-bold">
              {conversation.unread}
            </span>
          )}
        </div>
      </div>
    </button>
  );
}
