# MemoryChat Technical Specifications

> Documentação técnica completa do projeto MemoryChat

---

## 📚 Índice

| File | Descrição |
|-------|-----------|
| [SPEC.md](./SPEC.md) | Visão geral do projeto e especificações |
| [techstack.md](./techstack.md) | Stack de tecnologia e decisões de design |
| [architecture.md](./architecture.md) | Arquitetura do sistema (Alta e Baixa) |
| [database.md](./database.md) | Schema do banco de dados |
| [ai-agents.md](./ai-agents.md) | Arquitetura dos Agentes de IA |
| [api.md](./api.md) | Especificação das APIs REST e WebSocket |
| [frontend.md](./frontend.md) | Arquitetura Frontend e UX |
| [deployment.md](./deployment.md) | Infraestrutura e Deployment |

---

## 🎯 Visão Geral

**MemoryChat** é uma plataforma de mensagens com IA integrada que ajuda usuários a gerenciar e extrair valor de relacionamentos pessoais e profissionais através de dados de conversas.

O projeto é desenvolvido em 6 semanas (MVP) para o programa VinUni AI Thực Chiến.

### Core Features

- **Chat 1-1** com mensagens em tempo real
- **Contact Memory** - IA extrai conhecimento de conversas
- **Smart Search** - Busca semântica em linguagem natural
- **Context Recall** - Resumo instantâneo ao abrir chat
- **Recommendation** - Sugestões proativas de follow-up
- **AI Copilot** - Assistente contextual em cada conversa

### Design Principles

1. **AI First** - IA é o valor central do produto
2. **Human in the Loop** - Usuário sempre confirma ações da IA
3. **Privacy First** - Dados isolados por usuário
4. **Explainable Recommendation** - Cada sugestão tem razão
5. **Modular AI** - Agentes independentes e escaláveis

---

## 📁 Estrutura de Diretórios

```
docs/
├── general overview/   # Documentação original
│   ├── 01_Project_Overview.md
│   ├── 02_Product_Requirement_Document.md
│   └── ...
├── specs/              # Especificações técnicas (este diretório)
│   ├── README.md       # Este arquivo
│   ├── SPEC.md         # Especificações gerais
│   ├── techstack.md    # Stack de tecnologia
│   ├── architecture.md # Arquitetura do sistema
│   ├── database.md     # Schema do banco
│   ├── ai-agents.md    # Arquitetura de IA
│   ├── api.md          # Especificação de APIs
│   ├── frontend.md     # Arquitetura Frontend
│   └── deployment.md   # Infraestrutura
└── plan/               # Planos de sprint
```

---

## 🔄 Migração de Código

### Status Atual do MVP

| Componente | Status | Localização |
|------------|--------|-------------|
| FastAPI Backend | ✅ Skeleton | `src/main.py` |
| LangGraph Agent | ✅ Skeleton | `src/agents/graph.py` |
| LLM Gateway | ✅ Skeleton | `src/services/llm.py` |
| SQLite DB | ✅ Configurado | `./data/app.db` |
| ChromaDB | ✅ Configurado | `./data/chroma` |
| Docker | ✅ Configurado | `Dockerfile`, `docker-compose.yml` |
| Frontend React | ⬜ Pendente | `frontend/` (criação futura) |
| Auth (JWT) | ⬜ Pendente | - |
| PostgreSQL | ⬜ Pós-MVP | - |
| Neo4j | ⬜ Pós-MVP | - |

---

## 📅 Roadmap

| Sprint | Semana | Objetivo |
|--------|--------|----------|
| 1 | Week 1 | Foundation & Backend Skeleton |
| 2 | Week 2 | Chat System |
| 3 | Week 3 | AI Memory |
| 4 | Week 4 | Search + Recommendation |
| 5 | Week 5 | AI Copilot + Frontend |
| 6 | Week 6 | Testing + Demo |

---

## 👥 Equipe

| Membro | Função |
|--------|--------|
| Member 1 | Project Lead, AI Architecture, Backend |
| Member 2 | Frontend (React), UI/UX |
| Member 3 | Backend, Database, Auth, Realtime |
| Member 4 | AI Engineer, Embedding, Vector DB |

---

## 📞 Suporte

Para dúvidas sobre especificações, consulte:

- [SPEC.md](./SPEC.md) - Visão geral do projeto
- [techstack.md](./techstack.md) - Decisões de tecnologia
- [architecture.md](./architecture.md) - Arquitetura detalhada
- `src/` - Código fonte implementado

---

*Última atualização: 2026-08-13*
