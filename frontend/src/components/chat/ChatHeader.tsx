import { Avatar } from '../common/Avatar';
import type { Conversation } from '@/data/mockData';

interface ChatHeaderProps {
  conversation: Conversation;
  showContext?: boolean;
  onToggleContext?: () => void;
}

export function ChatHeader({ conversation, showContext, onToggleContext }: ChatHeaderProps) {
  return (
    <div className="h-16 px-4 flex items-center justify-between border-b border-divider bg-background flex-shrink-0">
      {/* Left side — Avatar + Info */}
      <div className="flex items-center gap-3">
        <Avatar
          name={conversation.name}
          src={conversation.avatar}
          size="md"
          online={conversation.online}
        />
        <div>
          <h3 className="text-sm font-semibold text-text-primary leading-tight">
            {conversation.name}
          </h3>
          <p className="text-xs text-text-secondary">
            {conversation.online ? (
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-online rounded-full" />
                Active now
              </span>
            ) : (
              'Offline'
            )}
          </p>
        </div>
      </div>

      {/* Right side — Action buttons */}
      <div className="flex items-center gap-1">
        {/* Phone call */}
        <button className="w-9 h-9 rounded-full hover:bg-secondary flex items-center justify-center transition-colors text-messenger-blue" title="Audio call">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
          </svg>
        </button>

        {/* Video call */}
        <button className="w-9 h-9 rounded-full hover:bg-secondary flex items-center justify-center transition-colors text-messenger-blue" title="Video call">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9.75a2.25 2.25 0 002.25-2.25V7.5a2.25 2.25 0 00-2.25-2.25H4.5A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" />
          </svg>
        </button>

        {/* AI Context toggle */}
        <button
          onClick={onToggleContext}
          className={`w-9 h-9 rounded-full flex items-center justify-center transition-all ${
            showContext
              ? 'bg-[#EEF2FF] text-[#6366F1] dark:bg-[#312E81]/40 dark:text-[#A5B4FC]'
              : 'hover:bg-secondary text-messenger-blue'
          }`}
          title={showContext ? 'Hide AI context' : 'Show AI context'}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className={showContext ? '' : 'hidden'}>
            <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" fill="currentColor"/>
            <path d="M18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" fill="currentColor"/>
          </svg>
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5" className={showContext ? 'hidden' : ''}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
