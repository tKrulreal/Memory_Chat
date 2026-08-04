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

---

## Trạng thái hiện tại

- ✅ `src/agents/graph.py` skeleton (LangGraph `analyze` + `respond`).
- ✅ Memory Agent, Search Agent, Recommendation Agent (từ WS-03, WS-04).
- ⬜ Assistant Orchestrator chưa có (chỉ là single-node graph).
- ⬜ Tagging Agent, Connection Agent chưa có.
- ⬜ Copilot API chưa có.

---

## TASK-COP-01: Assistant Orchestrator (LangGraph) ⬜

**Mô tả:** Refactor `src/agents/graph.py` thành Assistant Orchestrator hoàn chỉnh với nhiều node.

**Checklist:**
- [ ] Refactor `src/agents/graph.py` thành Assistant Orchestrator
- [ ] Định nghĩa `AssistantState` TypedDict: `{ query, user_id, context, intent, tools_to_call, agent_response, final_response }`
- [ ] Thêm node `intent_detection` (rule-based MVP: SEARCH/MEMORY/RECOMMENDATION/CHITCHAT)
- [ ] Thêm node `context_builder` (lấy Memory + recent messages)
- [ ] Thêm node `tool_selection` (chọn tool dựa trên intent)
- [ ] Thêm node `agent_execution` (gọi các Agent con)
- [ ] Thêm node `response_validator` (kiểm tra output hợp lệ)
- [ ] Kết nối các node thành StateGraph
- [ ] Fallback nếu LLM fail (graceful error trả về "Xin lỗi, hệ thống đang bận")
- [ ] Giữ endpoint `/api/v1/chat` hoạt động (giữ skeleton `analyze` + `respond` cho backward compat)

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

## TASK-COP-02: Tools layer (search, memory, recommendation) ⬜

**Mô tả:** Tạo Tools layer — mỗi tool wrap một Agent con, dùng LangChain `@tool` decorator.

**Checklist:**
- [ ] Tạo `src/agents/tools/` package
- [ ] Tool `search_contact(query: str, limit=5)` — gọi SearchAgent
- [ ] Tool `get_contact_memory(contact_id: int)` — lấy ContactMemory
- [ ] Tool `get_recent_messages(conversation_id: int, limit=10)` — lấy Message gần nhất
- [ ] Tool `recommend_reply(contact_id: int)` — gợi ý reply qua LLM
- [ ] Tool `get_recommendations(limit=10)` — lấy Recommendation pending
- [ ] Tool `get_contact_insights(contact_id: int)` — lấy Insight
- [ ] Mỗi tool có docstring mô tả rõ (LLM dùng để chọn tool)
- [ ] Tool registry để Orchestrator dùng

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

## TASK-COP-03: Tagging Agent + API ⬜

**Mô tả:** Tagging Agent — đề xuất Tag mới cho Contact từ Memory.

**Checklist:**
- [ ] Tạo `src/agents/tagging/` package
- [ ] Tagging Agent: extract entities từ Memory → đề xuất Tag
- [ ] Method `suggest_tags(contact_id) -> list[str]`
- [ ] Dùng LLM với prompt: "Từ Memory sau, đề xuất 3-5 tag ngắn gọn (lowercase, no space)"
- [ ] Pydantic output validation: `tags: list[str]`
- [ ] Endpoint `GET /api/v1/contacts/{id}/suggested-tags` — trả gợi ý
- [ ] Endpoint `POST /api/v1/contacts/{id}/tags` — user approve (lưu vào ContactTag)
- [ ] Test với 5 Contact mẫu (tag đề xuất phù hợp)

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

## TASK-COP-04: Connection Agent + API ⬜

**Mô tả:** Connection Agent — đề xuất kết nối giữa 2 Contact dựa trên Memory + Embedding.

**Checklist:**
- [ ] Tạo `src/agents/connection/` package
- [ ] Connection Agent: candidate generation từ Memory + Embedding similarity
- [ ] Method `find_connections(contact_id, top_k=5) -> list[ConnectionPair]`
- [ ] LLM reasoning cho top pairs (giải thích vì sao kết nối)
- [ ] Endpoint `GET /api/v1/connections/suggested` — trả top 5 cặp Contact
- [ ] Endpoint `POST /api/v1/connections/{pair_id}/accept` — user confirm
- [ ] Test với 10 Contact mẫu (đề xuất đúng cặp liên quan)

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

## TASK-COP-05: Copilot API + Share-to-Conversation ⬜

**Mô tả:** REST API cho AI Copilot + Share-to-Conversation flow.

**Endpoints:**

```
POST /api/v1/copilot                      — Hỏi Copilot (gọi Assistant Orchestrator)
POST /api/v1/copilot/stream               — Streaming response (optional)
POST /api/v1/copilot/share                — Share AI response vào conversation input box
```

**Checklist:**
- [ ] Tạo `src/api/copilot.py` router
- [ ] Pydantic schemas: `CopilotRequest { query, context? }`, `CopilotResponse { response, sources, tools_used }`
- [ ] Endpoint `POST /api/v1/copilot` — gọi Assistant Orchestrator
- [ ] Lưu câu hỏi + response vào `EventLog` (event `OPEN_AI`)
- [ ] Log prompt + response vào `.ai-log/`
- [ ] Streaming response (optional, dùng `StreamingResponse`)
- [ ] Endpoint `POST /api/v1/copilot/share` — copy AI response vào `conversation_id` (tạo message draft)
- [ ] Test E2E Copilot với 5 câu hỏi mẫu:
  - "Người này là ai?" → trả Memory + Insight
  - "Tôi nên nhắn gì?" → trả Reply suggestion
  - "Tìm người thích X" → trả Search result
  - "Có Contact nào cần follow-up?" → trả Recommendation
  - "Gợi ý 3 tag cho contact này" → trả Tag suggestion
- [ ] Validation: output không leak Memory của Contact khác user

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
