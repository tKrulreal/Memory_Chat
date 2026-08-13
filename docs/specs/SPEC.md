# SPEC.md — Project Specifications

## MemoryChat MVP v1.0

---

## 1. Project Overview

### 1.1 Project Name
**MemoryChat** — AI-native Messaging Platform with Long-term Relationship Memory

### 1.2 Project Type
AI Application (MVP for VinUni AI Thực Chiến Program)

### 1.3 Duration
6 Weeks

### 1.4 Core Value Proposition

MemoryChat transforma conversas em conhecimento estruturado:

```
Conversa → Memória → Busca Semântica → Recomendação → IA Copilot
```

### 1.5 Problem Statement

Pessoas com alta intensidade de comunicação enfrentam:
- Não lembrar quem é cada contato
- Não lembrar detalhes importantes sobre relacionamentos
- Perder oportunidades de follow-up
- Dificuldade em encontrar contatos específicos

### 1.6 Solution

IA que funciona como "Second Brain" para relacionamentos:
- AI extrai automaticamente conhecimento de conversas
- AI responde perguntas sobre contatos
- AI sugere ações proativas

---

## 2. Product Vision

Build an AI-native messaging platform that:
- **Remembers** every relationship
- **Understands** every conversation
- **Proactively assists** users in maintaining meaningful connections

---

## 3. Target Users

| Persona | Use Case |
|---------|----------|
| Sales | Gerenciar clientes, lembrar histórico |
| Founder | Networking, acompanhar parceiros |
| Freelancer | Múltiplos clientes, acompanhar projetos |
| Recruiter | Gerenciar candidatos, lembrar conversas |
| Business Dev | Expandir rede, timing de follow-up |

---

## 4. Core Features (MVP)

### 4.1 Authentication
| Feature | Description |
|---------|------------|
| Register | Email + Password |
| Login | JWT-based authentication |
| Logout | Token invalidation |

### 4.2 Chat System
| Feature | Description |
|---------|------------|
| Conversation List | Lista de conversas |
| Send Message | Mensagens 1-1 |
| Receive Message | Receber em tempo real |
| Read Status | Indicador de leitura |

### 4.3 Contact Management
| Feature | Description |
|---------|------------|
| Contact List | Lista de contatos |
| Contact Profile | Avatar, nome, info |
| Add Contact | Adicionar novo contato |
| Edit Contact | Editar informações |

### 4.4 AI Contact Memory
| Feature | Description |
|---------|------------|
| Summary | Resumo da relação |
| Company | Empresa onde trabalha |
| Profession | Profissão/cargo |
| Skills | Habilidades identificadas |
| Interest | Interesses mencionados |
| Timeline | Cronologia de eventos |
| Relationship Score | Score 0-100 |

### 4.5 Smart Search
| Feature | Description |
|---------|------------|
| Semantic Search | Busca por linguagem natural |
| "Pessoas que trabalham com AI" | Exemplo de query |
| Results | Lista com explicações |

### 4.6 Context Recall
| Feature | Description |
|---------|------------|
| Context Card | Card ao abrir chat |
| Quick Summary | Resumo rápido |
| Last Topic | Último assunto |
| Relationship Score | Score visível |

### 4.7 AI Recommendation
| Feature | Description |
|---------|------------|
| Follow-up | Sugestão de contato |
| Reply | Sugestão de resposta |
| Tag | Sugestão de tag |
| Connection | Sugestão de conexão |
| Priority | Contatos prioritários |

### 4.8 AI Copilot
| Feature | Description |
|---------|------------|
| 🤖 Button | Botão em cada conversa |
| Bottom Sheet | Painel de ações |
| Quick Actions | Resumo, perfil, busca |
| Share to Conversation | Compartilhar para input |

---

## 5. Non-Functional Requirements

### 5.1 Performance
| Metric | Target |
|--------|--------|
| API Response | < 300ms (sem LLM) |
| Search Latency | < 3 segundos |
| Context Recall | < 30 segundos |
| Memory Update | < 10 segundos |

### 5.2 Scalability
| Metric | Target |
|--------|--------|
| Concurrent Users | Mínimo 1.000 |

### 5.3 Security
| Requirement | Description |
|-------------|-------------|
| Data Isolation | Cada usuário acesso só seus dados |
| JWT Auth | Autenticação stateless |
| Input Validation | Pydantic models |
| Privacy | AI não compartilha dados |

---

## 6. Out of Scope (MVP)

### 6.1 Not Implemented
| Feature | Reason |
|---------|--------|
| Group Chat | Complexidade |
| Voice Call | Tempo |
| Video Call | Tempo |
| Story | Não alinhado |
| Sticker | Não alinhado |
| Auto-send Message | Violaria human-in-loop |
| Auto Actions | Violaria human-in-loop |

### 6.2 Future Phases
| Phase | Features |
|-------|----------|
| Phase 2 | Group Chat, Calendar, Gmail |
| Phase 3 | MCP Server, Multi-LLM |
| Phase 4 | Enterprise, Team Workspace |

---

## 7. User Stories

### 7.1 Authentication
```
Como novo usuário, quero criar uma conta
Para começar a usar o aplicativo
```

### 7.2 Chat
```
Como usuário, quero enviar e receber mensagens
Para comunicar com meus contatos
```

### 7.3 Contact Memory
```
Como usuário, quero que AI lembre informações
Para não precisar anotar manualmente
```

### 7.4 Context Recall
```
Como usuário, ao reabrir chat
Quero ver resumo instantâneo
Para não ler histórico completo
```

### 7.5 Smart Search
```
Como usuário, quero buscar por linguagem natural
Para encontrar pessoa sem lembrar nome
```

### 7.6 Recommendation
```
Como usuário, quero sugestões de follow-up
Para não perder oportunidades
```

### 7.7 AI Copilot
```
Como usuário, quero assistente na conversa
Para perguntar sobre contato sem sair
```

---

## 8. Acceptance Criteria

| # | Criteria |
|---|----------|
| 1 | Usuário pode fazer login/logout |
| 2 | Usuário pode enviar mensagem 1-1 |
| 3 | AI gera Contact Memory automaticamente |
| 4 | Context Card aparece ao abrir chat |
| 5 | Busca semântica funciona |
| 6 | AI sugere follow-up relevante |
| 7 | AI Copilot compartilha para conversa |
| 8 | Nenhuma ação automática sem confirmação |

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| Context Retrieval | < 30 segundos |
| Search Success Rate | > 90% |
| Summary Acceptance | > 80% |
| Search Usage | > 60% (2x/semana) |
| Recommendation CTR | > 50% |
| CSAT | ≥ 4/5 |

---

## 10. High-Level Architecture

```
                    MemoryChat
                          │
          ┌───────────────┼───────────────┐
          │                               │
   Messaging Layer               AI Intelligence Layer
          │                               │
    Conversation                  AI Copilot
          │                               │
          └───────────────┬───────────────┘
                          │
                 Assistant Orchestrator
                          │
        ┌──────────────┬──────────────┬──────────────┐
        │              │              │              │
  Memory Agent   Search Agent   Tagging Agent   Recommendation Agent
                          │
                 PostgreSQL + Neo4j + Qdrant
```

---

## 11. Design Principles

1. **AI First** — Cada feature projetada em torno da IA
2. **Human in the Loop** — IA sugere, usuário decide
3. **Privacy First** — Dados isolados por usuário
4. **Explainable** — Cada recomendação tem razão
5. **Modular** — Agentes independentes

---

## 12. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-13 | Initial MVP specifications |

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
