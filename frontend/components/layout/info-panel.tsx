"use client";

import { ChevronLeft, ChevronDown, Lightbulb, Phone, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AIRecommendationCard } from "@/components/ai/ai-recommendation-card";
import { useUIStore } from "@/lib/stores/ui-store";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { useQuery } from "@tanstack/react-query";
import { getConversations } from "@/lib/api/conversations";
import { cn } from "@/lib/utils";

export function InfoPanel() {
  const infoPanelOpen = useUIStore((s) => s.infoPanelOpen);
  const setInfoPanelOpen = useUIStore((s) => s.setInfoPanelOpen);

  return (
    <>
      {/* Desktop collapsible panel */}
      <aside
        aria-label="Contact information"
        className={cn(
          "hidden h-full shrink-0 flex-col border-l border-subtle bg-surface transition-[width,opacity] duration-200 xl:flex",
          infoPanelOpen ? "w-info-panel opacity-100" : "w-0 overflow-hidden opacity-0",
        )}
      >
        <PanelContent onClose={() => setInfoPanelOpen(false)} />
      </aside>

      {/* Tablet/mobile drawer overlay */}
      {infoPanelOpen && (
        <div className="fixed inset-0 z-40 xl:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/60"
            onClick={() => setInfoPanelOpen(false)}
            aria-label="Close info panel"
          />
          <aside aria-label="Contact information" className="absolute right-0 top-0 h-full w-info-panel max-w-[85vw] bg-surface shadow-xl">
            <PanelContent onClose={() => setInfoPanelOpen(false)} />
          </aside>
        </div>
      )}
    </>
  );
}

function PanelContent({ onClose }: { onClose: () => void }) {
  const user = useAuthStore((s) => s.user);
  const activeId = useConversationStore((s) => s.activeConversationId);
  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: !!user,
  });

  const activeConversation = conversations.find(c => c.id === activeId);
  const isUserA = user?.id === activeConversation?.user_a_id;
  const peerId = activeConversation 
    ? (isUserA ? activeConversation.user_b_id : activeConversation.user_a_id)
    : "NC";
  const peer = isUserA ? activeConversation?.user_b : activeConversation?.user_a;
  
  let peerName = activeConversation ? `User ${peerId.substring(0, 4)}` : "NC";
  let peerShort = activeConversation ? peerId.substring(0, 2).toUpperCase() : "NC";
  
  if (peer) {
    peerName = peer.full_name || peer.email.split('@')[0];
    peerShort = peer.email.substring(0, 2).toUpperCase();
  }

  const handleMessageClick = () => {
    document.getElementById("composer-input")?.focus();
    // Only close on mobile (xl:hidden handles mobile)
    if (window.innerWidth < 1280) {
      onClose();
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-subtle px-4 py-3">
        <h2 className="text-sm font-semibold">Contact info</h2>
        <button
          type="button"
          onClick={onClose}
          className="rounded-button p-1.5 text-secondary hover:bg-elevated hover:text-primary xl:hidden"
          aria-label="Close panel"
        >
          <X size={16} />
        </button>
      </div>

      <div className="scrollbar-thin flex-1 overflow-y-auto p-4 space-y-6">
        <div className="flex flex-col items-center text-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-blue-500/20 text-2xl font-semibold text-blue-300 uppercase">
            {peerShort}
          </div>
          <h3 className="mt-3 text-lg font-semibold">{peerName}</h3>
          <div className="flex items-center gap-1 mt-1">
            <span className="flex h-2 w-2 rounded-full bg-green-500"></span>
            <p className="text-sm text-secondary">Peer · Direct message</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <Button variant="primary" size="sm" onClick={handleMessageClick}>
            Message
          </Button>
          <Button variant="secondary" size="sm" disabled title="Coming soon">
            <Phone size={14} className="mr-1.5" />
            Call
          </Button>
        </div>

        <AIRecommendationCard />

        <details className="group rounded-button border border-subtle overflow-hidden">
          <summary className="cursor-pointer list-none flex items-center justify-between px-4 py-3 text-sm font-medium hover:bg-elevated transition-colors">
            <span>Channel info</span>
            <ChevronDown size={16} className="text-secondary transition-transform duration-200 group-open:-rotate-180" />
          </summary>
          <div className="border-t border-subtle bg-surface px-4 py-3 text-sm text-secondary">
            P2P conversation. AI context is private to your account.
          </div>
        </details>

        <details className="group rounded-button border border-subtle overflow-hidden">
          <summary className="cursor-pointer list-none flex items-center justify-between px-4 py-3 text-sm font-medium hover:bg-elevated transition-colors">
            <span>Media, files & links</span>
            <ChevronDown size={16} className="text-secondary transition-transform duration-200 group-open:-rotate-180" />
          </summary>
          <div className="border-t border-subtle bg-surface px-4 py-3 text-sm text-secondary">
            No shared media yet.
          </div>
        </details>

        <details className="group rounded-button border border-subtle overflow-hidden">
          <summary className="cursor-pointer list-none flex items-center justify-between px-4 py-3 text-sm font-medium hover:bg-elevated transition-colors">
            <div className="flex items-center gap-2">
              <Lightbulb size={14} />
              Privacy & support
            </div>
            <ChevronDown size={16} className="text-secondary transition-transform duration-200 group-open:-rotate-180" />
          </summary>
          <div className="border-t border-subtle bg-surface px-4 py-3 text-sm text-secondary">
            Report, block, or mute options will appear here.
          </div>
        </details>
      </div>

      <div className="border-t border-subtle p-3 xl:hidden">
        <Button variant="ghost" size="sm" className="w-full" onClick={onClose}>
          <ChevronLeft size={14} className="mr-1" />
          Back to chat
        </Button>
      </div>
    </div>
  );
}
