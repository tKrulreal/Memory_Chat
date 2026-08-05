import { useState, useRef, type KeyboardEvent } from 'react';

interface ChatInputProps {
  onSendMessage: (content: string) => void;
}

export function ChatInput({ onSendMessage }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = message.trim();
    if (!trimmed) return;
    onSendMessage(trimmed);
    setMessage('');
    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px';
    }
  };

  const hasContent = message.trim().length > 0;

  return (
    <div className="px-4 py-3 border-t border-divider bg-background">
      <div className="flex items-end gap-2">
        {/* Attachment buttons */}
        <div className="flex items-center gap-1 pb-1.5">
          {/* Plus / More */}
          <button className="w-8 h-8 rounded-full hover:bg-secondary flex items-center justify-center transition-colors text-messenger-blue" title="More options">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
          </button>
          
          {/* Image */}
          <button className="w-8 h-8 rounded-full hover:bg-secondary flex items-center justify-center transition-colors text-messenger-blue" title="Attach image">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25a2.25 2.25 0 00-2.25-2.25H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
            </svg>
          </button>

          {/* GIF */}
          <button className="w-8 h-8 rounded-full hover:bg-secondary flex items-center justify-center transition-colors text-messenger-blue font-bold text-xs" title="Send GIF">
            GIF
          </button>
        </div>

        {/* Message input */}
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder="Aa"
            rows={1}
            className="w-full px-4 py-2.5 rounded-[20px] bg-chat-input text-text-primary placeholder:text-text-tertiary text-sm resize-none focus:outline-none focus:ring-1 focus:ring-messenger-blue/30 transition-all overflow-hidden"
            style={{ maxHeight: '120px' }}
          />
          {/* Emoji button inside input */}
          <button className="absolute right-3 bottom-2.5 text-messenger-blue hover:scale-110 transition-transform" title="Emoji">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z" />
            </svg>
          </button>
        </div>

        {/* Send / Like button */}
        <div className="pb-1.5">
          {hasContent ? (
            <button
              onClick={handleSend}
              className="w-9 h-9 rounded-full messenger-gradient flex items-center justify-center text-white transition-all active:scale-90"
              title="Send"
            >
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            </button>
          ) : (
            <button className="w-9 h-9 rounded-full hover:bg-secondary flex items-center justify-center transition-colors text-messenger-blue" title="Send like">
              <svg width="22" height="22" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
