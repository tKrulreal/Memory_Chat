# FRONTEND.md — Frontend Architecture & UX

## MemoryChat MVP v1.0

---

## 1. Frontend Vision

### 1.1 Philosophy

> **"Chat First, AI Native"**

MemoryChat's frontend philosophy:
- Users come to chat — AI enhances but doesn't dominate
- AI works silently in the background
- Context is always available but not intrusive
- Human always makes the final decision

### 1.2 Design Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Invisible AI** | AI operates silently | Memory builds without user knowing |
| **Human First** | User always decides | AI suggests, user confirms |
| **Context Aware** | AI knows the conversation | No need to repeat context |
| **Minimal Interaction** | One action is enough | Tap AI → Get result |
| **VinUni Red Identity** | Brand consistency | Primary color #A1232A |

### 1.3 AI UX Guidelines

```
AI Suggestion
    │
    ├── User Reviews
    │
    ├── [Accept] → Copy to input → User sends
    │
    └── [Reject] → Dismiss → Learn from feedback
```

---

## 2. Design System

### 2.1 Color Palette

```css
/* VinUni Red Brand Colors */
:root {
  /* Primary - VinUni Red */
  --color-primary: #A1232A;
  --color-primary-light: #C73E4A;
  --color-primary-dark: #7A1A1F;
  --color-primary-bg: #FFD7DA;
  
  /* Neutrals */
  --color-secondary: #1B1B1F;
  --color-surface: #FFFFFF;
  --color-background: #FAFAFB;
  --color-muted: #6E6E73;
  --color-border: #E5E5E5;
  
  /* Semantic */
  --color-success: #34C759;
  --color-warning: #FF9500;
  --color-error: #FF3B30;
  --color-info: #007AFF;
  
  /* Text */
  --color-text-primary: #1B1B1F;
  --color-text-secondary: #6E6E73;
  --color-text-tertiary: #AEAEB2;
  --color-text-inverse: #FFFFFF;
}

/* Dark Mode */
[data-theme="dark"] {
  --color-surface: #1C1C1E;
  --color-background: #000000;
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #8E8E93;
  --color-border: #38383A;
}
```

### 2.2 Typography

```css
/* Font Family */
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-display: 'Inter Tight', 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}

/* Font Sizes */
:root {
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
}

/* Font Weights */
:root {
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}

/* Line Heights */
:root {
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### 2.3 Spacing

```css
:root {
  /* Spacing Scale (4px base) */
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;       /* 16px */
  --space-5: 1.25rem;    /* 20px */
  --space-6: 1.5rem;     /* 24px */
  --space-8: 2rem;       /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */
}
```

### 2.4 Border Radius

```css
:root {
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */
  --radius-2xl: 1.5rem;  /* 24px */
  --radius-full: 9999px;
}
```

### 2.5 Shadows

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  
  /* AI-specific */
  --shadow-ai: 0 4px 20px rgba(161, 35, 42, 0.15);
}
```

### 2.6 Animation

```css
:root {
  /* Duration */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 350ms;
  
  /* Easing */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Animation Classes */
.animate-fade-in {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

.animate-slide-up {
  animation: slideUp var(--duration-normal) var(--ease-out);
}

.animate-scale-in {
  animation: scaleIn var(--duration-fast) var(--ease-spring);
}
```

---

## 3. Component Library

### 3.1 Button

```tsx
// Variants
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

// Usage
<Button variant="primary" size="md" onClick={handleClick}>
  Send Message
</Button>

<Button variant="ghost" size="sm" leftIcon={<Icon />}>
  Cancel
</Button>
```

| Variant | Use Case |
|---------|----------|
| `primary` | Main actions (Send, Save) |
| `secondary` | Secondary actions |
| `ghost` | Tertiary actions, AI suggestions |
| `danger` | Destructive actions |

### 3.2 Input

```tsx
// Variants
type InputVariant = 'default' | 'error' | 'success';

// Usage
<Input
  placeholder="Search contacts..."
  value={searchQuery}
  onChange={setSearchQuery}
  leftIcon={<SearchIcon />}
  rightIcon={searchQuery && <ClearButton onClick={clear} />}
/>
```

### 3.3 Avatar

```tsx
<Avatar
  src={contact.avatar}
  name={contact.displayName}
  size="md"
  status="online" // online | offline | away
  showStatus
/>
```

### 3.4 Card

```tsx
<Card variant="elevated" padding="md">
  <Card.Header>
    <Avatar ... />
    <ContactInfo ... />
  </Card.Header>
  <Card.Body>
    <ContextCard ... />
  </Card.Body>
</Card>
```

### 3.5 Tag

```tsx
<Tag color="#A1232A" removable onRemove={handleRemove}>
  AI Engineer
</Tag>

<Tag color="#34C759">
  ✅ Confirmed
</Tag>
```

### 3.6 Badge

```tsx
<Badge variant="primary" count={5}>
  Messages
</Badge>

<Badge variant="success">
  Online
</Badge>
```

### 3.7 Bottom Sheet

```tsx
<BottomSheet
  isOpen={isOpen}
  onClose={handleClose}
  snapPoints={[0.5, 0.9]}
>
  <BottomSheet.Header>
    <AI icon />
    <Title>AI Copilot</Title>
  </BottomSheet.Header>
  <BottomSheet.Body>
    <AIActions ... />
  </BottomSheet.Body>
</BottomSheet>
```

### 3.8 Message Bubble

```tsx
<MessageBubble
  variant="sent" // sent | received
  content="Hello!"
  timestamp="10:30 AM"
  status="read" // sending | sent | delivered | read
  isAISuggestion={false}
/>
```

### 3.9 Context Card

```tsx
<ContextCard
  contact={contact}
  memory={memory}
  onExpand={handleExpand}
  onDismiss={handleDismiss}
>
  <ContextCard.Summary summary={memory.summary} />
  <ContextCard.Timeline events={memory.timeline} />
  <ContextCard.Tags tags={tags} />
  <ContextCard.Actions>
    <Action icon="refresh" onClick={refreshMemory} />
    <Action icon="edit" onClick={editMemory} />
  </ContextCard.Actions>
</ContextCard>
```

### 3.10 AI Copilot Panel

```tsx
<AICopilotPanel
  conversationId={conversationId}
  onShareToConversation={handleShare}
>
  <AIActions>
    <Action
      icon="summary"
      label="Summarize"
      onClick={getSummary}
    />
    <Action
      icon="reply"
      label="Suggest Reply"
      onClick={getReply}
    />
    <Action
      icon="profile"
      label="View Profile"
      onClick={viewProfile}
    />
    <Action
      icon="search"
      label="Search Memory"
      onClick={searchMemory}
    />
  </AIActions>
  
  <AIResponse
    content={response}
    isStreaming={isStreaming}
    suggestions={suggestions}
  />
</AICopilotPanel>
```

---

## 4. Screen Layouts

### 4.1 Mobile Layout (Primary)

```
┌─────────────────────────────────┐
│  ←  An Nguyen          ⋮  📞  │  ← Header
├─────────────────────────────────┤
│  ┌─────────────────────────┐   │
│  │   CONTEXT CARD (toggle)  │   │  ← Context Card
│  │   [Summary] [Tags] [✓]  │   │
│  └─────────────────────────┘   │
├─────────────────────────────────┤
│                                 │
│    ┌─────────────────────┐     │
│    │  Hello! How are you? │     │  ← Sent Message
│    │              10:30 ✓✓│     │
│    └─────────────────────┘     │
│                                 │
│    ┌─────────────────────────┐ │
│    │ I'm doing great!        │ │  ← Received Message
│    │ 10:31                  │ │
│    └─────────────────────────┘ │
│                                 │
│                                 │
├─────────────────────────────────┤
│  ┌─────────────────────────────┐│
│  │ Type a message...       📎 │││  ← Input Area
│  └─────────────────────────────┘│
│  ┌─────────────────────────────┐│
│  │   🤖  AI   │    ➤ Send    │││  ← Action Bar
│  └─────────────────────────────┘│
├─────────────────────────────────┤
│  💬  👥  🔍  💡  🤖          │  ← Bottom Nav
└─────────────────────────────────┘
```

### 4.2 Web Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  MemoryChat                                    🔔  👤  ⚙️       │
├────────────┬────────────────────────────────────────────────────┤
│            │  ┌─────────────────────────────────────────────┐  │
│  💬 Chats  │  │  ←  An Nguyen                      ⋮  📞  │  │
│  👥 Contacts│  ├─────────────────────────────────────────────┤  │
│  🔍 Search │  │  ┌─────────────────────────┐               │  │
│  💡 Ideas  │  │  │   CONTEXT CARD         │               │  │
│            │  │  │   [Summary] [Tags]     │               │  │
│  ────────  │  │  │   Relationship: 85%    │               │  │
│  💬 Today  │  │  └─────────────────────────┘               │  │
│  • An      │  │                                             │  │
│  • Minh    │  │  ┌─────────────────────┐                   │  │
│  💬 Earlier│  │  │  Hello!            │                   │  │
│  • Chi     │  │  │            10:30 ✓✓│                   │  │
│            │  │  └─────────────────────┘                   │  │
│            │  │                                             │  │
│            │  │  ┌─────────────────────────┐               │  │
│            │  │  │  I'm doing great!      │               │  │
│            │  │  └─────────────────────────┘               │  │
│            │  │                                             │  │
│            │  ├─────────────────────────────────────────────┤  │
│            │  │  ┌─────────────────────────────┐  ┌────┐  │  │
│            │  │  │  Type a message...      📎  │  │Send│  │  │
│            │  │  └─────────────────────────────┘  └────┘  │  │
│            │  │  🤖 AI Copilot                               │  │
│            │  └─────────────────────────────────────────────┘  │
└────────────┴────────────────────────────────────────────────────┘
         240px                      flex-1
```

### 4.3 AI Copilot Bottom Sheet

```
┌─────────────────────────────────┐
│            ───────              │  ← Drag Handle
│                                 │
│     🤖  AI Copilot              │  ← Header
│     An Nguyen                   │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────────┐│
│  │  💬 Summarize              ││  ← Quick Actions
│  ├─────────────────────────────┤│
│  │  👤 View Profile           ││
│  ├─────────────────────────────┤│
│  │  ✍️  Suggest Reply         ││
│  ├─────────────────────────────┤│
│  │  🔍 Search Memory          ││
│  ├─────────────────────────────┤│
│  │  📌 Add Tag               ││
│  ├─────────────────────────────┤│
│  │  🔔 Follow-up              ││
│  ├─────────────────────────────┤│
│  │  🤝 Suggest Connection     ││
│  └─────────────────────────────┘│
│                                 │
├─────────────────────────────────┤
│  Ask AI:                        │
│  ┌─────────────────────────────┐│
│  │ Ask anything about An...    ││  ← AI Input
│  └─────────────────────────────┘│
│                                 │
│  [Loading response...]          │  ← AI Response
│                                 │
│  ┌─────────────────────────────┐│
│  │ Copy to input    │  Close   ││  ← Actions
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

---

## 5. Page Specifications

### 5.1 Chat List Page

**Route:** `/` (Home)

**Components:**
- Search bar (sticky)
- Conversation list with preview
- Pull to refresh (mobile)
- Infinite scroll (web)

**Data displayed:**
- Contact avatar + name
- Last message preview (truncated)
- Timestamp
- Unread count badge

### 5.2 Chat Screen

**Route:** `/chat/:conversationId`

**Components:**
- Header with contact info
- Context Card (collapsible)
- Message list (virtualized)
- Input area
- AI Copilot button

**Features:**
- Real-time message updates (WebSocket)
- Typing indicator
- Read receipts
- Context card auto-refresh

### 5.3 Contact List Page

**Route:** `/contacts`

**Components:**
- Search/filter bar
- Contact cards with memory preview
- Sort options (name, recent, score)

**Data displayed:**
- Avatar + name
- Company/profession
- Relationship score
- Tags

### 5.4 Contact Profile Page

**Route:** `/contacts/:contactId`

**Components:**
- Avatar header
- Memory card
- Timeline
- Tags section
- Conversation history
- Actions (message, edit, delete)

### 5.5 Search Page

**Route:** `/search`

**Components:**
- Search input (auto-focus)
- Recent searches
- Results list
- Explanation panel

**Features:**
- Real-time suggestions
- Natural language processing
- Result highlighting

### 5.6 Recommendations Page

**Route:** `/recommendations`

**Components:**
- Filter tabs (All, Follow-up, Tags, Connections)
- Recommendation cards
- Accept/Reject buttons
- Empty state

### 5.7 AI Copilot Page

**Route:** `/copilot/:conversationId` (or bottom sheet)

**Components:**
- Conversation context
- Quick actions grid
- Chat input
- Response display
- Share to conversation

---

## 6. State Management

### 6.1 Store Architecture (Zustand)

```tsx
// stores/authStore.ts
interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

// stores/chatStore.ts
interface ChatState {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  messages: Map<string, Message[]>;
  
  sendMessage: (conversationId: string, content: string) => Promise<void>;
  loadMessages: (conversationId: string, page: number) => Promise<void>;
}

// stores/memoryStore.ts
interface MemoryState {
  memories: Map<string, ContactMemory>;
  loading: Map<string, boolean>;
  
  getMemory: (contactId: string) => Promise<ContactMemory>;
  refreshMemory: (contactId: string) => Promise<void>;
}

// stores/uiStore.ts
interface UIState {
  theme: 'light' | 'dark' | 'system';
  isCopilotOpen: boolean;
  isContextCardExpanded: boolean;
  
  toggleCopilot: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}
```

### 6.2 Data Fetching (TanStack Query)

```tsx
// hooks/useContacts.ts
export function useContacts(params: ContactQueryParams) {
  return useQuery({
    queryKey: ['contacts', params],
    queryFn: () => api.contacts.list(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// hooks/useConversation.ts
export function useConversation(conversationId: string) {
  return useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => api.conversations.get(conversationId),
    enabled: !!conversationId,
  });
}

// hooks/useMessages.ts
export function useMessages(conversationId: string, page: number) {
  return useInfiniteQuery({
    queryKey: ['messages', conversationId, page],
    queryFn: ({ pageParam }) => api.messages.list(conversationId, { page: pageParam }),
    getNextPageParam: (lastPage) => lastPage.pagination.nextPage,
  });
}
```

---

## 7. API Integration

### 7.1 API Client

```tsx
// services/api.ts
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,
});

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      try {
        await useAuthStore.getState().refreshToken();
        // Retry original request
        return api(error.config);
      } catch {
        // Refresh failed, logout
        useAuthStore.getState().logout();
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 7.2 API Endpoints

```tsx
// services/endpoints.ts
export const contacts = {
  list: (params: ContactQueryParams) => 
    api.get<ContactListResponse>('/contacts', { params }),
  get: (id: string) => 
    api.get<ContactResponse>(`/contacts/${id}`),
  create: (data: CreateContactInput) => 
    api.post<ContactResponse>('/contacts', data),
  update: (id: string, data: UpdateContactInput) => 
    api.put<ContactResponse>(`/contacts/${id}`, data),
  delete: (id: string) => 
    api.delete(`/contacts/${id}`),
};

export const messages = {
  list: (conversationId: string, params: MessageQueryParams) =>
    api.get<MessageListResponse>(`/conversations/${conversationId}/messages`, { params }),
  send: (conversationId: string, data: SendMessageInput) =>
    api.post<MessageResponse>(`/conversations/${conversationId}/messages`, data),
};

export const copilot = {
  chat: (data: CopilotInput) =>
    api.post<CopilotResponse>('/copilot', data),
  chatStream: (data: CopilotInput) =>
    api.post('/copilot', data, { responseType: 'stream' }),
};

export const search = {
  query: (data: SearchInput) =>
    api.post<SearchResponse>('/search', data),
  history: (params: PaginationParams) =>
    api.get<SearchHistoryResponse>('/search/history', { params }),
};
```

---

## 8. WebSocket Integration

### 8.1 WebSocket Client

```tsx
// hooks/useWebSocket.ts
export function useWebSocket() {
  const { accessToken } = useAuthStore();
  const [ws, setWs] = useState<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  
  useEffect(() => {
    if (!accessToken) return;
    
    const connect = () => {
      const socket = new WebSocket(`${WS_URL}?token=${accessToken}`);
      
      socket.onopen = () => {
        reconnectAttempts.current = 0;
      };
      
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
      };
      
      socket.onclose = () => {
        // Reconnect with exponential backoff
        const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000);
        reconnectAttempts.current++;
        setTimeout(connect, delay);
      };
      
      setWs(socket);
    };
    
    connect();
    
    return () => {
      ws?.close();
    };
  }, [accessToken]);
  
  return {
    send: (data: WSMessage) => ws?.send(JSON.stringify(data)),
    isConnected: ws?.readyState === WebSocket.OPEN,
  };
}
```

### 8.2 Message Handling

```tsx
// handlers/websocket.ts
const handlers: Record<string, (data: any) => void> = {
  'message': handleNewMessage,
  'typing': handleTyping,
  'online_status': handleOnlineStatus,
  'notification': handleNotification,
  'recommendation': handleRecommendation,
};

function handleMessage(data: { type: string; data: any }) {
  const handler = handlers[data.type];
  if (handler) {
    handler(data.data);
  }
}
```

---

## 9. Performance Optimization

### 9.1 Code Splitting

```tsx
// Lazy load pages
const ChatScreen = lazy(() => import('@/pages/Chat'));
const ContactProfile = lazy(() => import('@/pages/ContactProfile'));
const Recommendations = lazy(() => import('@/pages/Recommendations'));

// Lazy load heavy components
const AICopilotPanel = lazy(() => import('@/components/ai/CopilotPanel'));
const ContextCard = lazy(() => import('@/components/chat/ContextCard'));
```

### 9.2 Virtual List for Messages

```tsx
// For conversations with many messages
import { useVirtualizer } from '@tanstack/react-virtual';

function MessageList({ messages }: { messages: Message[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // Estimated message height
    overscan: 5,
  });
  
  return (
    <div ref={parentRef} className="h-full overflow-auto">
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((item) => (
          <MessageBubble key={item.key} message={messages[item.index]} />
        ))}
      </div>
    </div>
  );
}
```

### 9.3 Image Optimization

```tsx
// Use lazy loading for images
<img 
  src={avatarUrl} 
  alt={name}
  loading="lazy"
  decoding="async"
/>

// Use srcset for responsive images
<img
  src={avatarUrl}
  srcset={`${avatarUrl} 1x, ${avatarUrl2x} 2x`}
  alt={name}
/>
```

---

## 10. Accessibility

### 10.1 ARIA Labels

```tsx
<button
  aria-label="Send message"
  onClick={handleSend}
>
  <SendIcon />
</button>

<input
  aria-label="Search contacts"
  placeholder="Search..."
/>

<main role="main" aria-label="Chat messages">
  {/* Messages */}
</main>
```

### 10.2 Keyboard Navigation

```tsx
// Tab navigation
<Tab.Group>
  <Tab.List>
    <Tab>Chats</Tab>
    <Tab>Contacts</Tab>
  </Tab.List>
</Tab.Group>

// Keyboard shortcuts
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      closeModal();
    }
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openSearch();
    }
  };
  
  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, []);
```

### 10.3 Touch Targets

```css
/* Minimum touch target size */
button,
[role="button"],
a,
input[type="checkbox"],
input[type="radio"] {
  min-width: 44px;
  min-height: 44px;
}
```

---

## 11. Error Handling

### 11.1 Error Boundaries

```tsx
// ErrorBoundary.tsx
class ErrorBoundary extends Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          resetError={() => this.setState({ hasError: false })}
        />
      );
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <ChatScreen />
</ErrorBoundary>
```

### 11.2 Toast Notifications

```tsx
// hooks/useToast.ts
export function useToast() {
  return {
    success: (message: string) => toast.success(message),
    error: (message: string) => toast.error(message),
    info: (message: string) => toast.info(message),
  };
}

// Usage
const { error } = useToast();
try {
  await sendMessage();
} catch (e) {
  error('Failed to send message');
}
```

---

## 12. Testing

### 12.1 Component Tests

```tsx
// ChatInput.test.tsx
describe('ChatInput', () => {
  it('should send message when send button clicked', async () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    await userEvent.type(input, 'Hello!');
    
    const sendButton = screen.getByRole('button', { name: 'Send' });
    await userEvent.click(sendButton);
    
    expect(onSend).toHaveBeenCalledWith('Hello!');
  });
});
```

### 12.2 E2E Tests

```tsx
// e2e/chat.spec.ts
test('user can send and receive messages', async () => {
  await page.goto('/');
  
  // Login
  await page.click('[data-testid="login-button"]');
  
  // Go to chat
  await page.click('[data-testid="conversation-1"]');
  
  // Send message
  await page.fill('[data-testid="message-input"]', 'Hello!');
  await page.click('[data-testid="send-button"]');
  
  // Verify message appears
  await expect(page.locator('text=Hello!')).toBeVisible();
});
```

---

## 13. Folder Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── app/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   └── router.tsx
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Avatar/
│   │   │   ├── Card/
│   │   │   ├── Tag/
│   │   │   └── ...
│   │   ├── chat/
│   │   │   ├── ChatList/
│   │   │   ├── ChatWindow/
│   │   │   ├── MessageBubble/
│   │   │   ├── ContextCard/
│   │   │   └── InputArea/
│   │   ├── contact/
│   │   │   ├── ContactList/
│   │   │   ├── ContactCard/
│   │   │   └── ContactProfile/
│   │   ├── search/
│   │   │   ├── SearchBar/
│   │   │   └── SearchResults/
│   │   ├── recommendation/
│   │   │   ├── RecommendationList/
│   │   │   └── RecommendationCard/
│   │   └── ai/
│   │       ├── AICopilotPanel/
│   │       ├── AIActions/
│   │       └── AIResponse/
│   ├── pages/
│   │   ├── Chat/
│   │   ├── Contacts/
│   │   ├── Search/
│   │   ├── Recommendations/
│   │   ├── Settings/
│   │   └── Auth/
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   ├── useContacts.ts
│   │   ├── useMessages.ts
│   │   ├── useWebSocket.ts
│   │   └── useAI.ts
│   ├── stores/
│   │   ├── authStore.ts
│   │   ├── chatStore.ts
│   │   ├── contactStore.ts
│   │   ├── memoryStore.ts
│   │   └── uiStore.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── endpoints.ts
│   │   └── websocket.ts
│   ├── theme/
│   │   ├── index.ts
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── components.ts
│   ├── types/
│   │   ├── user.ts
│   │   ├── contact.ts
│   │   ├── message.ts
│   │   └── api.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── helpers.ts
│   └── __tests__/
│       ├── components/
│       ├── hooks/
│       └── pages/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
