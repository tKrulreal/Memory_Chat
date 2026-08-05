export function EmptyChat() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-background text-center p-8">
      {/* Messenger icon */}
      <div className="w-24 h-24 rounded-full bg-gradient-to-br from-messenger-blue/10 to-messenger-purple/10 flex items-center justify-center mb-6">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" className="text-messenger-blue">
          <path
            d="M12 2C6.477 2 2 6.145 2 11.243c0 2.908 1.434 5.503 3.683 7.2V22l3.3-1.815A11.3 11.3 0 0012 20.485c5.523 0 10-4.144 10-9.242S17.523 2 12 2z"
            fill="currentColor"
            opacity="0.2"
          />
          <path
            d="M13.228 13.991L10.58 11.2 5.5 14.05l5.57-5.91 2.648 2.792 5.08-2.85-5.57 5.909z"
            fill="currentColor"
          />
        </svg>
      </div>
      <h3 className="text-xl font-bold text-text-primary mb-2">
        Select a conversation
      </h3>
      <p className="text-sm text-text-secondary max-w-xs">
        Choose a chat from the sidebar to start messaging, or create a new conversation.
      </p>
    </div>
  );
}
