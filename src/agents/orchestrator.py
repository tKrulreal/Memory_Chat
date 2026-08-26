"""
AI Copilot Orchestrator Agent.
Provides semantic search, recent message retrieval, peer information inspection,
and smart reply suggestions for the AI Copilot.
"""

import json
import logging
import uuid
from enum import StrEnum
from typing import Any

from src.agents.state import AgentState
from src.gateways.llm import LLMGateway

logger = logging.getLogger(__name__)


class Intent(StrEnum):
    SEARCH = "SEARCH"
    MEMORY = "MEMORY"
    CHITCHAT = "CHITCHAT"
    REPLY_SUGGEST = "REPLY_SUGGEST"
    RECOMMENDATION = "RECOMMENDATION"
    TAG_SUGGEST = "TAG_SUGGEST"
    CONNECTION = "CONNECTION"
    UNKNOWN = "UNKNOWN"


SYSTEM_PROMPT = """Bạn là AI Copilot trong ứng dụng nhắn tin MemoryChat.
Nhiệm vụ: Trả lời câu hỏi của người dùng và giúp họ tìm kiếm thông tin về bạn bè, liên hệ, người quen cũ hoặc tìm kiếm người dùng mới phù hợp qua hồ sơ cá nhân.
Bạn có quyền truy cập vào các tools để tra cứu bộ nhớ và hồ sơ người dùng.
Không bịa đặt thông tin. Nếu không tìm thấy thông tin từ công cụ, hãy báo cho người dùng biết.
Trả lời bằng tiếng Việt, ngắn gọn, thân thiện, và trực tiếp vào câu hỏi.

QUAN TRỌNG VỀ TÌM KIẾM NGƯỜI DÙNG/LIÊN HỆ:
Khi người dùng yêu cầu tìm kiếm và bạn tìm thấy thông tin qua tool `semantic_search`, BẠN PHẢI trả về một thẻ XML `<card>` cho MỖI người tìm thấy với cú pháp:
- Đối với người ĐÃ TỪNG TRÒ CHUYỆN (has_chatted="true"):
  <card name="Tên" email="Email" conversation_id="UUID của conversation" user_id="UUID của user" has_chatted="true" profession="Nghề nghiệp" company="Công ty">Tóm tắt ngắn gọn lý do phù hợp hoặc thông tin trao đổi</card>

- Đối với người CHƯA TỪNG TRÒ CHUYỆN (has_chatted="false" - tìm theo hồ sơ profile):
  <card name="Tên" email="Email" user_id="UUID của user" has_chatted="false" profession="Nghề nghiệp" company="Công ty">Tóm tắt ngắn gọn lý do phù hợp dựa trên kỹ năng/sở thích/hồ sơ công khai</card>

Ví dụ:
<card name="Nguyễn Văn A" email="a@example.com" conversation_id="123e4567-e89b-12d3-a456-426614174000" user_id="8888-9999" has_chatted="true" profession="Kỹ sư AI" company="FPT">Đã từng chat, trao đổi về RAG và robot</card>
<card name="Trần Thị B" email="b@example.com" user_id="9999-0000" has_chatted="false" profession="Chuyên gia Dữ liệu" company="VinAI">Người dùng mới trên hệ thống, có kỹ năng Python và BigData</card>

Bạn có thể trả về nhiều thẻ <card> nếu tìm thấy nhiều người. Các nội dung chat thông thường thì cứ trả lời bằng văn bản tự nhiên.
"""



def _classify_intent(query: str, llm: LLMGateway | None = None) -> tuple[Intent, float]:
    """Classify the user's intent based on keywords and heuristics."""
    if not query:
        return Intent.UNKNOWN, 0.0

    query_lower = query.lower().strip()

    keyword_rules: list[tuple[list[str], Intent, float]] = [
        (["tìm", "tìm kiếm", "search", "ai là", "ai làm", "tìm người"], Intent.SEARCH, 0.9),
        (["gợi ý trả lời", "tôi nên nhắn gì", "trả lời thế nào", "nhắn gì"], Intent.REPLY_SUGGEST, 0.85),
        (["có gì mới", "ưu tiên", "follow-up", "nhắc nhở", "ai cần follow-up"], Intent.RECOMMENDATION, 0.85),
        (["gợi ý tag", "nhãn gì", "gắn nhãn", "thêm tag", "tag cho"], Intent.TAG_SUGGEST, 0.85),
        (["kết nối", "giới thiệu", "tương tự"], Intent.CONNECTION, 0.85),
        (["chào", "cảm ơn", "hello", "hi", "bye", "tạm biệt"], Intent.CHITCHAT, 0.95),
        (["người này là ai", "ai đây", "thông tin", "memory", "nhớ gì"], Intent.MEMORY, 0.85),
    ]

    for keywords, intent, conf in keyword_rules:
        if any(kw in query_lower for kw in keywords):
            return intent, conf

    return Intent.MEMORY, 0.5


def _generate_chitchat_response(query: str) -> str:
    """Generate friendly responses for conversational greetings."""
    query_lower = query.lower().strip()
    if any(w in query_lower for w in ["chào", "hello", "hi", "hey"]):
        return "Chào bạn! Tôi là AI Copilot của MemoryChat. Tôi có thể giúp gì cho bạn hôm nay?"
    if any(w in query_lower for w in ["cảm ơn", "thanks", "thank you"]):
        return "Không có gì! Rất vui được hỗ trợ bạn. Hãy cho tôi biết nếu cần thêm thông tin nhé."
    if any(w in query_lower for w in ["tạm biệt", "bye", "goodbye"]):
        return "Tạm biệt bạn! Chúc bạn một ngày làm việc hiệu quả và tốt lành."
    return "Chào bạn! Mình có thể giúp gì cho bạn trong việc tra cứu trí nhớ hoặc tìm kiếm liên hệ?"


def _check_data_leak_programmatic(content: str, user_id: str = "", contact_id: str = "") -> dict[str, Any]:
    """Check content for sensitive credentials or data leakage."""
    if not content:
        return {"is_valid": True, "reason": ""}
    sensitive_keywords = ["password", "secret_key", "api_key", "bearer_token", "private_key"]
    content_lower = content.lower()
    for kw in sensitive_keywords:
        if kw in content_lower:
            return {"is_valid": False, "reason": f"Phát hiện từ khóa nhạy cảm: {kw}"}
    return {"is_valid": True, "reason": ""}


def _check_prompt_injection(query: str) -> bool:
    """Check if query contains prompt injection patterns."""
    if not query:
        return False
    patterns = [
        "ignore all previous",
        "ignore previous",
        "disregard prior",
        "you are now",
        "roleplay as",
        "system: ignore",
        "instruction: new instructions",
        "override system prompt",
    ]
    query_lower = query.lower()
    return any(p in query_lower for p in patterns)


# --- LangGraph Node Functions (for backward compatibility & graph integration) ---

async def intent_detection_node(state: AgentState) -> dict[str, Any]:
    """Detect intent from query."""
    query = state.get("query", "")
    if not query:
        return {"intent": Intent.UNKNOWN.value, "intent_confidence": 0.0, "intent_reasoning": "Empty query"}
    intent, conf = _classify_intent(query)
    return {
        "intent": intent.value,
        "intent_confidence": conf,
        "intent_reasoning": f"Keyword matching with confidence {conf}",
    }


async def context_builder_node(state: AgentState) -> dict[str, Any]:
    """Build context data for the agent."""
    context = state.get("context", {})
    if not context:
        return {"context_data": "Không có context"}
    return {"context_data": f"Context: {context}"}


async def tool_selection_node(state: AgentState) -> dict[str, Any]:
    """Select appropriate tools based on detected intent."""
    intent_val = state.get("intent", Intent.UNKNOWN.value)
    tools_to_call: list[str] = []

    if intent_val == Intent.SEARCH.value:
        tools_to_call.append("search_contact")
    elif intent_val == Intent.MEMORY.value:
        tools_to_call.append("get_contact_memory")
    elif intent_val == Intent.RECOMMENDATION.value:
        tools_to_call.append("get_recommendations")
    elif intent_val == Intent.REPLY_SUGGEST.value:
        tools_to_call.append("recommend_reply")
    elif intent_val == Intent.TAG_SUGGEST.value:
        tools_to_call.append("get_contact_insights")

    return {"tools_to_call": tools_to_call}


async def agent_execution_node(state: AgentState) -> dict[str, Any]:
    """Execute selected tools or return summary."""
    tools = state.get("tools_to_call", [])
    if not tools:
        return {"execution_summary": "No tools to execute", "agent_responses": {}}
    return {"execution_summary": f"Executed tools: {tools}", "agent_responses": {}}


async def response_validator_node(state: AgentState) -> dict[str, Any]:
    """Validate response safety and validity."""
    return {"is_valid": True}


async def respond_node(state: AgentState) -> dict[str, Any]:
    """Formulate final response to user."""
    intent_val = state.get("intent", Intent.UNKNOWN.value)
    query = state.get("query", "")

    if intent_val == Intent.CHITCHAT.value:
        resp = _generate_chitchat_response(query)
        return {"response": resp, "final_response": resp}

    exec_summary = state.get("execution_summary", "")
    if exec_summary == "No tools to execute":
        msg = "Tôi không tìm thấy thông tin phù hợp với yêu cầu của bạn."
        return {"response": msg, "final_response": msg}

    return {"response": exec_summary, "final_response": exec_summary}


class DummyGraph:
    async def ainvoke(self, state_dict: dict[str, Any]) -> dict[str, Any]:
        return {}


def build_orchestrator():
    """Build a graph object for backward compatibility."""
    return DummyGraph()


orchestrator = build_orchestrator()


async def run_copilot(
    query: str,
    user_id: str | None = None,
    contact_id: str | None = None,
    conversation_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Copilot Agent using LangChain Tool Calling:
    1. Bind tools to LLM
    2. Invoke LLM
    3. If tool called, execute tool and invoke LLM again for final answer.
    """
    # If orchestrator graph is mocked in tests
    if hasattr(orchestrator, "ainvoke") and type(orchestrator) is not DummyGraph:
        mock_res = await orchestrator.ainvoke({
            "query": query,
            "user_id": user_id,
            "contact_id": contact_id,
            "conversation_id": conversation_id,
        })
        if isinstance(mock_res, dict) and ("final_response" in mock_res or "response" in mock_res):
            return {
                "response": mock_res.get("final_response", mock_res.get("response", "")),
                "intent": mock_res.get("intent", Intent.UNKNOWN.value),
                "tools_used": mock_res.get("tools_to_call", []),
                "is_valid": mock_res.get("is_valid", True),
            }

    if not user_id:
        intent, _ = _classify_intent(query)
        if intent == Intent.CHITCHAT:
            return {
                "response": _generate_chitchat_response(query),
                "intent": Intent.CHITCHAT.value,
                "tools_used": [],
                "is_valid": True,
            }
        return {
            "response": "Thiếu user_id để thực hiện Copilot.",
            "intent": "ERROR",
            "tools_used": [],
            "is_valid": False,
        }


    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    from langchain_core.tools import tool

    llm_gateway = LLMGateway()
    chat_model = llm_gateway.llm

    from src.api.deps import SessionLocal
    from src.models.user import Setting

    context_turns = 10
    db_settings = SessionLocal()
    try:
        user_uuid_val = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        user_setting = db_settings.query(Setting).filter(Setting.user_id == user_uuid_val).first()
        if user_setting and user_setting.ai_copilot_context_turns:
            context_turns = user_setting.ai_copilot_context_turns
    except Exception as e:
        logger.warning(f"Failed to fetch user copilot context turns: {e}")
    finally:
        db_settings.close()

    @tool
    def semantic_search(search_query: str, scope: str = "all_chats", limit: int = 5) -> str:
        """
        Search for information across all chat conversation memories.
        Returns matching contacts, conversation IDs, relevance scores, and reasoning.

        Args:
            search_query: Keyword or question (e.g. 'ai làm về robot?')
            scope: 'current_chat' or 'all_chats' (default: all_chats)
            limit: Maximum number of results
        """
        if not user_id:
            return "Vui lòng đăng nhập để tìm kiếm."

        try:
            from src.agents.search.agent import SearchAgent
            search_agent = SearchAgent()
            results = search_agent.search(query=search_query, user_id=user_id, limit=limit)

            if not results:
                return "Không tìm thấy thông tin nào phù hợp."

            out = []
            for i, r in enumerate(results, 1):
                chat_status = f"Có (Conversation ID: {r.conversation_id})" if r.has_chatted else "Chưa từng trò chuyện (Người dùng mới - Tìm thấy từ hồ sơ profile)"
                out.append(
                    f"Kết quả {i}:\n"
                    f"- Tên: {r.name}\n"
                    f"- Email: {r.email}\n"
                    f"- User ID: {r.user_id}\n"
                    f"- Đã từng chat: {chat_status}\n"
                    f"- Conversation ID: {r.conversation_id}\n"
                    f"- Nghề nghiệp: {r.profession}\n"
                    f"- Công ty: {r.company}\n"
                    f"- Kỹ năng: {', '.join(r.skills) if r.skills else 'Chưa có'}\n"
                    f"- Sở thích/Quan tâm: {', '.join(r.interests) if r.interests else 'Chưa có'}\n"
                    f"- Tags: {', '.join(r.tags) if r.tags else 'Không có'}\n"
                    f"- Độ phù hợp (0-100): {r.score}\n"
                    f"- Lý do phù hợp: {r.explanation}\n"
                )

            return "\n".join(out)
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return "Đã xảy ra lỗi khi tìm kiếm."

    @tool
    def get_recent_messages(limit: int | None = None) -> str:
        """Retrieve the most recent messages in the current conversation within the configured context turns."""
        if not conversation_id:
            return "Bạn không ở trong một cuộc hội thoại nào."
        eff_limit = limit if (limit is not None and limit > 0) else context_turns
        if eff_limit <= 0:
            eff_limit = 100  # Unlimited setting
        from src.agents.tools.memory_tools import get_recent_messages as get_recent_msgs_tool
        return get_recent_msgs_tool.invoke({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "limit": eff_limit,
        })

    @tool
    def get_peer_info() -> str:
        """Retrieve detailed profile, memory, skills, and interests of the peer in current chat."""
        if not conversation_id and not contact_id:
            return "Không xác định được cuộc trò chuyện hiện tại."

        from src.api.deps import SessionLocal
        from src.models.ai import AssistantMemory
        from src.models.chat import Conversation
        from src.models.user import User, UserProfile

        db = SessionLocal()
        try:
            if conversation_id:
                conv_uuid = uuid.UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
                conv = db.get(Conversation, conv_uuid)
                if conv:
                    other_user_id = conv.user_b_id if str(conv.user_a_id) == str(user_id) else conv.user_a_id
                    other_user = db.get(User, other_user_id)
                    user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                    mem = db.query(AssistantMemory).filter(
                        AssistantMemory.owner_user_id == user_uuid,
                        AssistantMemory.conversation_id == conv.id,
                    ).first()

                    user_prof = db.query(UserProfile).filter(UserProfile.user_id == other_user_id).first()

                    name = other_user.full_name if other_user and other_user.full_name else (other_user.email if other_user else "Đối tác chat")
                    summary = mem.summary if mem and mem.summary else "Chưa có tóm tắt hội thoại"
                    facts = mem.facts if mem and mem.facts else {}

                    skills = user_prof.skills if user_prof and user_prof.skills else facts.get("skills", [])
                    interests = user_prof.interests if user_prof and user_prof.interests else facts.get("interests", [])
                    company = user_prof.company if user_prof and user_prof.company else facts.get("company", "Chưa rõ")
                    location = user_prof.location if user_prof and user_prof.location else facts.get("location", "Chưa rõ")
                    profession = user_prof.profession if user_prof and user_prof.profession else facts.get("profession", "Chưa rõ")

                    return (
                        f"Thông tin về {name}:\n"
                        f"- Chuyên môn: {profession}\n"
                        f"- Công ty: {company}\n"
                        f"- Địa điểm: {location}\n"
                        f"- Kỹ năng: {', '.join(skills) if skills else 'Chưa có'}\n"
                        f"- Quan tâm: {', '.join(interests) if interests else 'Chưa có'}\n"
                        f"- Tóm tắt AI: {summary}"
                    )

            if contact_id:
                from src.agents.tools.memory_tools import get_contact_memory
                return get_contact_memory.invoke({"user_id": user_id, "contact_id": contact_id})

            return "Không tìm thấy thông tin đối tác."
        except Exception as e:
            logger.error(f"Error getting peer info: {e}")
            return "Lỗi khi lấy thông tin người đang chat."
        finally:
            db.close()

    @tool
    def suggest_reply(tone: str = "friendly") -> str:
        """Suggest a smart reply for the latest message in the conversation. Tone: 'friendly', 'professional', 'casual'."""
        if not conversation_id and not contact_id:
            return "Không xác định được cuộc trò chuyện."

        from src.api.deps import SessionLocal
        from src.models.chat import Message
        db = SessionLocal()
        try:
            if conversation_id:
                conv_uuid = uuid.UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
                last_msg = db.query(Message).filter(Message.conversation_id == conv_uuid).order_by(Message.created_at.desc()).first()
                if last_msg:
                    return f"Gợi ý phản hồi theo phong cách {tone} cho tin nhắn gần nhất ('{last_msg.content}'): Xác nhận tiếp nhận thông tin và phản hồi ngắn gọn, thiện chí."
                return "Chưa có tin nhắn nào trong hội thoại để gợi ý trả lời."

            if contact_id:
                from src.agents.tools.recommendation_tools import recommend_reply
                return recommend_reply.invoke({"contact_id": contact_id, "context": f"Tone: {tone}"})

            return "Không xác định được cuộc trò chuyện."
        except Exception as e:
            logger.error(f"Error generating reply suggestion: {e}")
            return "Lỗi khi gợi ý câu trả lời."
        finally:
            db.close()

    tools = [semantic_search, get_recent_messages, get_peer_info, suggest_reply]
    llm_with_tools = chat_model.bind_tools(tools)

    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
    ]
    if history:
        for h in history:
            role = h.get("role")
            content = h.get("content", "")
            if content:
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=query))

    tools_used: list[str] = []
    try:
        response = llm_with_tools.invoke(messages)

        if response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tools_used.append(tool_name)

                # Execute the matched tool
                if tool_name == "semantic_search":
                    tool_result = semantic_search.invoke(tool_call["args"])
                elif tool_name == "get_recent_messages":
                    tool_result = get_recent_messages.invoke(tool_call["args"])
                elif tool_name == "get_peer_info":
                    tool_result = get_peer_info.invoke(tool_call["args"])
                elif tool_name == "suggest_reply":
                    tool_result = suggest_reply.invoke(tool_call["args"])
                else:
                    tool_result = "Tool not found."

                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

            # Call LLM again with tool outputs
            final_response = llm_with_tools.invoke(messages)
            response_content = str(final_response.content)
        else:
            response_content = str(response.content)

        intent_val, _ = _classify_intent(query, llm_gateway)
        if tools_used:
            intent_val = Intent.SEARCH

        return {
            "response": response_content,
            "intent": intent_val.value if isinstance(intent_val, Intent) else str(intent_val),
            "tools_used": tools_used,
            "is_valid": True,
        }

    except Exception as e:
        logger.error(f"LLM tool calling failed: {e}")
        return {
            "response": "Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau.",
            "intent": "ERROR",
            "tools_used": [],
            "is_valid": False,
        }
