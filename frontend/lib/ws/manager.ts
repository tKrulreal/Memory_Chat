import { useUIStore } from "../stores/ui-store";

type MessageHandler = (data: any) => void;

class WSManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private handlers: Set<MessageHandler> = new Set();
  private isIntentionalClose = false;
  
  public async connect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      return;
    }
    
    this.isIntentionalClose = false;
    useUIStore.getState().setConnectionState("reconnecting");

    try {
      // 1. Get ticket from BFF
      const res = await fetch("/api/auth/ws-ticket", { method: "POST" });
      if (!res.ok) {
        throw new Error("Failed to get WS ticket");
      }
      const { ticket } = await res.json();

      // 2. Connect to backend WS
      // Assuming backend runs on NEXT_PUBLIC_API_URL or localhost:8000
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = process.env.NEXT_PUBLIC_API_URL 
        ? new URL(process.env.NEXT_PUBLIC_API_URL).host 
        : "localhost:8000";
      const wsUrl = `${protocol}//${host}/ws/chat?ticket=${ticket}`;
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log("[WS] Connected");
        this.reconnectAttempts = 0;
        useUIStore.getState().setConnectionState("connected");
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "ping") {
            this.ws?.send(JSON.stringify({ type: "pong" }));
            return;
          }
          
          this.handlers.forEach(handler => handler(data));
        } catch (err) {
          console.error("[WS] Parse error", err);
        }
      };

      this.ws.onclose = () => {
        console.log("[WS] Disconnected");
        useUIStore.getState().setConnectionState("offline");
        
        if (!this.isIntentionalClose) {
          this.handleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error("[WS] Error", error);
      };
      
    } catch (err) {
      console.error("[WS] Connection setup failed", err);
      useUIStore.getState().setConnectionState("offline");
      this.handleReconnect();
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log("[WS] Max reconnect attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`[WS] Reconnecting in ${delay}ms...`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  public disconnect() {
    this.isIntentionalClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    useUIStore.getState().setConnectionState("offline");
  }

  public subscribe(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }
}

export const wsManager = new WSManager();
