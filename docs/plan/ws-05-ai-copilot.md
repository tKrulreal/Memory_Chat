# WS-05 — AI Copilot

> **Mục tiêu:** Hoàn thiện Assistant Orchestrator (LangGraph), AI Copilot endpoint, Tagging Agent, Connection Agent.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-05 (sau WS-04) |
| Độ phức tạp | 🔴 Cao |
| Phụ thuộc | WS-03 (AI Memory), WS-04 (Search & Recommendation) |
| Unblock | WS-06 (Frontend) |

> **Specification Reference:**
> - [AI Agents - Assistant Orchestrator](../specs/ai-agents.md#3-assistant-orchestrator)
> - [AI Agents - Tool Registry](../specs/ai-agents.md#10-tool-registry)
> - [AI Agents - Tagging Agent](../specs/ai-agents.md#7-tagging-agent)
> - [AI Agents - Connection Agent](../specs/ai-agents.md#8-connection-agent)
> - [API - Copilot Endpoints](../specs/api.md#9-copilot-api)

---

## Trạng thái hiện tại

- ✅ `src/agents/graph.py` skeleton (LangGraph `analyze` + `respond`).
- ✅ Memory Agent, Search Agent, Recommendation Agent (từ WS-03, WS-04).
- ✅ Assistant Orchestrator (`src/agents/orchestrator.py`).
- ✅ Tools layer (`src/agents/tools/`).
- ✅ Tagging Agent (`src/agents/tagging/agent.py`).
- ✅ Connection Agent (`src/agents/connection/agent.py`).
- ✅ Copilot API (`src/api/v1/copilot.py`).

---

## TASK-COP-01: Assistant Orchestrator (LangGraph) ✅

**Mô tả:** Refactor `src/agents/graph.py` thành Assistant Orchestrator hoàn chỉnh với nhiều node.

**Checklist:**
- [x] `src/agents/orchestrator.py` - Assistant Orchestrator hoàn chỉnh
- [x] `AgentState` TypedDict: `{ query, user_id, context, intent, tools_to_call, agent_response, final_response }`
- [x] Node `intent_detection` (rule-based + LLM: SEARCH/MEMORY/RECOMMENDATION/CHITCHAT/REPLY_SUGGEST/TAG_SUGGEST/CONNECTION)
- [x] Node `context_builder` (lấy Memory + recent messages)
- [x] Node `tool_selection` (chọn tool dựa trên intent)
- [x] Node `agent_execution` (gọi các Agent con)
- [x] Node `response_validator` (kiểm tra output hợp lệ)
- [x] Kết nối các node thành StateGraph
- [x] Fallback nếu LLM fail (graceful error)
- [x] ✅ FIX: Programmatic data leak detection
- [x] ✅ FIX: Prompt injection detection
- [x] Giữ endpoint `/api/v1/chat` hoạt động (backward compat)

**Commands:**
```bash
# Test Orchestrator
python -c "
from src.agents.graph import AssistantOrchestrator
orch = AssistantOrchestrator()
result = await orch.run(user_id=1, query='Người này là ai?')
print(result.final_response)
"
```

---

## TASK-COP-02: Tools layer (search, memory, recommendation) ✅

**Mô tả:** Tạo Tools layer — mỗi tool wrap một Agent con.

**Checklist:**
- [x] `src/agents/tools/` package
- [x] `search_contact(query, limit)` — gọi SearchAgent
- [x] `get_contact_memory(user_id, contact_id)` — lấy ContactMemory
- [x] `get_recent_messages(user_id, conversation_id, limit)` — lấy Message gần nhất
- [x] `recommend_reply(user_id, contact_id)` — gợi ý reply qua LLM
- [x] `get_recommendations(user_id, status, limit)` — lấy Recommendation pending
- [x] `get_contact_insights(user_id, contact_id)` — lấy Insight
- [x] Mỗi tool có docstring mô tả rõ
- [x] Helper functions trong `orchestrator.py` để load tools

**Commands:**
```bash
# Test tool
python -c "
from src.agents.tools import search_contact
result = await search_contact.ainvoke({'query': 'lập trình viên'})
print(result)
"
```

---

## TASK-COP-03: Tagging Agent + API ✅

**Mô tả:** Tagging Agent — đề xuất Tag mới cho Contact từ Memory.

**Checklist:**
- [x] `src/agents/tagging/agent.py` - TaggingAgent class
- [x] Method `suggest_tags(contact_id, db)` → đề xuất 3-5 tags
- [x] LLM với prompt: tags ngắn gọn, lowercase, no space
- [x] Method `approve_tags(db, contact_id, tag_names)` — user approve
- [x] Method `get_contact_tags(db, contact_id)` — lấy tags hiện tại
- [x] Endpoints trong `src/api/v1/contacts.py`:
  - `GET /contacts/{id}/tags` — lấy tags hiện tại
  - `GET /contacts/{id}/suggested-tags` — trả gợi ý
  - `POST /contacts/{id}/tags` — user approve
  - `DELETE /contacts/{id}/tags/{tag_name}` — xóa tag

**Commands:**
```bash
# Test Tagging Agent
python -c "
from src.agents.tagging import TaggingAgent
agent = TaggingAgent()
tags = await agent.suggest_tags(contact_id=1)
print(tags)
"

# Test API
curl http://localhost:8000/api/v1/contacts/1/suggested-tags \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-COP-04: Connection Agent + API ✅

**Mô tả:** Connection Agent — đề xuất kết nối giữa 2 Contact dựa trên Memory + Embedding.

**Checklist:**
- [x] `src/agents/connection/agent.py` - ConnectionAgent class
- [x] Method `find_connections(user_id, top_k=5)` → list[ConnectionPair]
- [x] Method `suggest_connections_for_contact(contact_id, top_k=3)` → list[ConnectionPair]
- [x] LLM reasoning cho top pairs (giải thích vì sao kết nối)
- [x] Endpoints trong `src/api/v1/connections.py`:
  - `GET /connections/suggested` — trả top 5 cặp Contact
  - `GET /connections/contact/{id}` — connections cho một contact cụ thể

**Commands:**
```bash
# Test Connection Agent
python -c "
from src.agents.connection import ConnectionAgent
agent = ConnectionAgent()
pairs = await agent.find_connections(contact_id=1)
for p in pairs:
    print(p.contact_a, '<->', p.contact_b, ':', p.reason)
"

# Test API
curl http://localhost:8000/api/v1/connections/suggested \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-COP-05: Copilot API + Share-to-Conversation ✅

**Mô tả:** REST API cho AI Copilot + Share-to-Conversation flow.

**Endpoints:**

```
POST /api/v1/copilot                      — Hỏi Copilot (gọi Assistant Orchestrator)
POST /api/v1/copilot/stream               — Streaming response
POST /api/v1/copilot/share                — Share AI response vào conversation input box
GET  /api/v1/copilot/intents              — Danh sách intents được hỗ trợ
```

**Checklist:**
- [x] `src/api/v1/copilot.py` router
- [x] Pydantic schemas: `CopilotRequest { query, context? }`, `CopilotResponse { response, sources, tools_used }`
- [x] Endpoint `POST /copilot` — gọi Assistant Orchestrator
- [x] Endpoint `POST /copilot/stream` — Streaming response
- [x] Endpoint `POST /copilot/share` — tạo draft message trong conversation
- [x] Endpoint `GET /copilot/intents` — danh sách intents
- [x] Emit event `OPEN_AI` khi user hỏi Copilot
- [x] Log prompt + response vào `.ai-log/copilot.jsonl`
- [x] Validation: output không leak Memory của Contact khác user (security checks)

**Commands:**
```bash
# Test Copilot API
curl -X POST http://localhost:8000/api/v1/copilot \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Người này là ai?","context":{"contact_id":1}}'

# Test Share to Conversation
curl -X POST http://localhost:8000/api/v1/copilot/share \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":1,"content":"Gợi ý reply..."}'
```

---

## Kết quả mong đợi sau WS-05

```
✅ LangGraph Orchestrator đầy đủ chạy được (5 node)
✅ Copilot trả lời đúng 5 câu hỏi mẫu
✅ Tagging Agent đề xuất đúng Tag cho 5 Contact mẫu
✅ Connection Agent đề xuất đúng cặp Contact liên quan
✅ Share to Conversation hoạt động
✅ Không leak Memory của Contact khác user
✅ Test E2E Copilot pass
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-COP-01: Assistant Orchestrator | ✅ Done | `src/agents/orchestrator.py` |
| TASK-COP-02: Tools layer | ✅ Done | `src/agents/tools/*.py` |
| TASK-COP-03: Tagging Agent | ✅ Done | `src/agents/tagging/agent.py` + contacts API |
| TASK-COP-04: Connection Agent | ✅ Done | `src/agents/connection/agent.py` + connections API |
| TASK-COP-05: Copilot API | ✅ Done | `src/api/v1/copilot.py` |
