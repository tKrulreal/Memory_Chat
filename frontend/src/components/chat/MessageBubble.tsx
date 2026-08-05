import type { Message } from '@/data/mockData';

interface MessageBubbleProps {
  message: Message;
  isLastInGroup: boolean;
}

export function MessageBubble({ message, isLastInGroup }: MessageBubbleProps) {
  const { content, timestamp, isSent, type } = message;
  const isAI = type === 'ai';

  if (isAI) {
    return (
      <div className={`flex justify-start message-animate ${isLastInGroup ? 'mb-3' : 'mb-0.5'}`}>
        <div className="max-w-[75%]">
          <div className="relative px-4 py-3 text-[13px] leading-[19px] rounded-2xl bg-gradient-to-br from-[#F0F4FF] to-[#EDE9FE] border border-[#C7D2FE]/40 text-[#1E293B] dark:from-[#1E1B4B]/40 dark:to-[#312E81]/30 dark:border-[#4338CA]/30 dark:text-[#C7D2FE]">
            {/* AI sparkle icon */}
            <div className="flex items-center gap-1.5 mb-1.5">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="text-[#6366F1] dark:text-[#A5B4FC]">
                <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" fill="currentColor"/>
                <path d="M18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" fill="currentColor"/>
              </svg>
              <span className="text-[11px] font-semibold text-[#6366F1] dark:text-[#A5B4FC] uppercase tracking-wider">
                AI Copilot
              </span>
            </div>
            {content}
          </div>
          {isLastInGroup && (
            <p className="text-[11px] text-text-tertiary mt-1 text-left px-1">
              {timestamp}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex message-animate ${isSent ? 'justify-end' : 'justify-start'} ${
        isLastInGroup ? 'mb-3' : 'mb-0.5'
      }`}
    >
      <div className="max-w-[65%] group">
        <div
          className={`px-3.5 py-2 text-[14px] leading-[20px] ${
            isSent
              ? 'bg-bubble-sent text-bubble-sent-text rounded-[18px] rounded-br-[4px]'
              : 'bg-bubble-received text-bubble-received-text rounded-[18px] rounded-bl-[4px]'
          }`}
        >
          {content}
        </div>
        
        {/* Timestamp — shows on hover for non-last messages, always visible for last */}
        {isLastInGroup && (
          <p className={`text-[11px] text-text-tertiary mt-1 ${isSent ? 'text-right' : 'text-left'} px-1`}>
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
}
