# MemoryChat Frontend

Next.js web client for MemoryChat — Messenger-style layout with MemoryChat green theme and AI features.

## Stack

- Next.js 15 (App Router)
- React 19
- Tailwind CSS (design tokens in `app/globals.css`)
- Zustand (client state)
- TanStack Query (server state)
- httpOnly cookie auth via Next.js BFF routes

## Getting started

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Ensure the FastAPI backend runs on port 8000 with `CORS_ORIGINS` including `http://localhost:3000`.

## Project structure

```
frontend/
├── app/
│   ├── (app)/          # Authenticated shell routes
│   ├── (auth)/         # Login / register
│   ├── api/auth/       # BFF: sets httpOnly session cookie
│   └── globals.css     # Design tokens
├── components/
│   ├── layout/         # AppShell, NavSidebar, ChatList, ChatWindow, InfoPanel
│   ├── ai/             # Context bar, recommendations, copilot drawer
│   └── ui/             # Shared primitives
├── lib/
│   ├── api/            # Backend client
│   ├── auth/           # Session helpers
│   └── stores/         # Zustand slices
└── types/              # Shared DTO types
```

## Design tokens

CSS variables in `app/globals.css`:

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-app` | `#0a0a0a` | App background |
| `--accent-primary` | `#22c55e` | Primary actions, outgoing bubbles |
| `--accent-warning` | `#f97316` | Send reminder CTA |
| `--accent-ai` | `#fef3c7` | Recommendation card |

## Auth flow

1. Browser posts credentials to `/api/auth/login` (Next.js route).
2. Route forwards to FastAPI, receives JWT, stores it in httpOnly cookie.
3. Middleware protects `(app)` routes; `/api/auth/me` proxies current user.

## Next steps

See `docs/plan/frontend-plan.md` for the full task breakdown.
