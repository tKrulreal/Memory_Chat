import { ContactContext } from '@/data/mockData';

interface ContextCardProps {
  context: ContactContext | null;
}

export function ContextCard({ context }: ContextCardProps) {
  if (!context) {
    return (
      <div className="hidden xl:flex w-80 border-l border-border bg-background p-6 flex-col h-full items-center justify-center text-center">
        <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
          <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" className="text-text-tertiary">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="font-bold text-text-primary mb-2">No Context Available</h3>
        <p className="text-sm text-text-secondary">Select a conversation to view AI-extracted memory context.</p>
      </div>
    );
  }

  return (
    <div className="hidden xl:flex w-80 border-l border-border bg-background p-6 flex-col h-full overflow-y-auto slide-in-right">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-messenger-purple to-messenger-blue flex items-center justify-center shadow-md">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="white" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h3 className="font-bold text-lg text-text-primary leading-tight">AI Context</h3>
          <p className="text-xs text-text-tertiary">For {context.contactName}</p>
        </div>
      </div>
      
      <div className="space-y-6">
        <div>
          <h4 className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-2">Summary</h4>
          <p className="text-sm text-text-secondary leading-relaxed bg-secondary/50 p-3 rounded-xl border border-border">
            {context.summary}
          </p>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-2">Key Topics</h4>
          <div className="flex flex-wrap gap-2">
            {context.keyTopics.map(topic => (
              <span key={topic} className="px-3 py-1 rounded-full bg-messenger-blue/10 text-messenger-blue text-xs font-medium border border-messenger-blue/20">
                {topic}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-2">Recent Insights</h4>
          <ul className="space-y-3">
            {context.recentInsights.map((insight, idx) => (
              <li key={idx} className="flex gap-3 text-sm text-text-secondary bg-secondary/30 p-3 rounded-xl">
                <span className="text-messenger-purple flex-shrink-0">💡</span>
                <span className="leading-tight">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="pt-4 border-t border-border">
          <div className="flex justify-between items-center">
            <span className="text-sm text-text-tertiary font-medium">Relationship Score</span>
            <div className="flex items-center gap-2">
              <div className="w-16 h-2 bg-secondary rounded-full overflow-hidden">
                <div 
                  className="h-full bg-emerald-500 rounded-full" 
                  style={{ width: `${context.relationshipScore}%` }} 
                />
              </div>
              <span className="font-bold text-emerald-500 text-sm">{context.relationshipScore}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
