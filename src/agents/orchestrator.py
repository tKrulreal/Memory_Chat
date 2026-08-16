"""
AI Copilot Agent (Simplified for Phase 4)
Thay thế hoàn toàn LangGraph phức tạp bằng luồng xử lý Agent đơn giản, an toàn.
"""

import json
import logging
import uuid
from enum import StrEnum

from src.gateways.llm import LLMGateway
from src.services.vector_store import VectorStoreService

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
Nhiệm vụ: Trả lời câu hỏi của người dùng và giúp họ tìm kiếm thông tin về bạn bè, liên hệ, hoặc nội dung chat cũ.
Bạn có quyền truy cập vào các tools để tra cứu bộ nhớ của người dùng.
Không bịa đặt thông tin. Nếu không tìm thấy thông tin từ công cụ, hãy báo cho người dùng biết.
Trả lời bằng tiếng Việt, ngắn gọn, thân thiện, và trực tiếp vào câu hỏi.

QUAN TRỌNG: Nếu người dùng yêu cầu TÌM KIẾM NGƯỜI DÙNG/LIÊN HỆ và bạn tìm thấy thông tin qua tool `semantic_search`, BẠN PHẢI trả về một thẻ contact card cho mỗi người tìm thấy bằng cú pháp XML sau:
<card name="Tên người liên hệ" email="Email liên hệ" conversation_id="UUID của conversation">Tóm tắt mô tả ngắn gọn lý do phù hợp hoặc thông tin liên quan</card>

Ví dụ: 
<card name="Nguyễn Văn A" email="nguyenvana@example.com" conversation_id="123e4567-e89b-12d3-a456-426614174000">Là bạn cấp 2, hiện đang làm việc tại Technopark trong lĩnh vực robot.</card>
Bạn có thể trả về nhiều thẻ <card> nếu tìm thấy nhiều người. Các nội dung chat thông thường thì cứ trả lời bình thường.
"""

def _classify_intent(query: str, llm: LLMGateway) -> Intent:
    query_lower = query.lower().strip()
    
    keyword_rules = [
        (["tìm", "tìm kiếm", "search", "ai là", "ai làm"], Intent.SEARCH),
        (["gợi ý trả lời", "tôi nên nhắn gì", "trả lời thế nào", "nhắn gì"], Intent.REPLY_SUGGEST),
        (["có gì mới", "ưu tiên", "follow-up", "nhắc nhở"], Intent.RECOMMENDATION),
        (["gợi ý tag", "nhãn gì", "gắn nhãn", "thêm tag"], Intent.TAG_SUGGEST),
        (["kết nối", "giới thiệu", "tương tự"], Intent.CONNECTION),
        (["chào", "cảm ơn", "hello", "hi", "bye"], Intent.CHITCHAT),
    ]

    for keywords, intent in keyword_rules:
        if any(kw in query_lower for kw in keywords):
            return intent

    return Intent.MEMORY

async def run_copilot(
    query: str,
    user_id: str | None = None,
    contact_id: str | None = None,
    conversation_id: str | None = None,
) -> dict:
    """
    Copilot Agent using LangChain Tool Calling:
    1. Bind tools to LLM
    2. Invoke LLM
    3. If tool called, execute tool and invoke LLM again for final answer.
    """
    if not user_id:
        return {
            "response": "Thiếu user_id để thực hiện Copilot.",
            "intent": "ERROR",
            "is_valid": False,
        }

    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    
    llm_gateway = LLMGateway()
    chat_model = llm_gateway.llm

    @tool
    def semantic_search(search_query: str, scope: str = "all_chats", limit: int = 5) -> str:
        """
        Tìm kiếm thông tin từ trí nhớ của tất cả các đoạn chat.
        Trả về kết quả bao gồm tên người, ID đoạn chat, độ liên quan và giải thích chi tiết.
        
        Args:
            search_query: Câu hỏi hoặc từ khóa muốn tìm kiếm (ví dụ: "ai làm về robot?")
            scope: "current_chat" để tìm trong chat hiện tại, "all_chats" để tìm trong toàn bộ. (Mặc định all_chats)
            limit: Số kết quả tối đa
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
                # We format it nicely so the LLM easily understands it
                out.append(
                    f"Kết quả {i}:\n"
                    f"- Tên: {r.name}\n"
                    f"- Email: {r.email}\n"
                    f"- Conversation ID: {r.conversation_id}\n"
                    f"- Độ phù hợp (0-100): {r.score}\n"
                    f"- Giải thích: {r.explanation}\n"
                )
                
            return "\n".join(out)
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return "Đã xảy ra lỗi khi tìm kiếm."

    @tool
    def xem_tin_nhan_gan_day(limit: int = 10) -> str:
        """Lấy danh sách tin nhắn gần nhất trong đoạn chat hiện tại. Dùng khi muốn tóm tắt chat hoặc lấy ngữ cảnh."""
        if not conversation_id:
            return "Bạn không ở trong một cuộc hội thoại nào."
        from src.agents.tools.memory_tools import get_recent_messages
        return get_recent_messages.invoke({"user_id": user_id, "conversation_id": conversation_id, "limit": limit})

    @tool
    def xem_thong_tin_nguoi_dang_chat() -> str:
        """Lấy thông tin chi tiết (memory, insights, nghề nghiệp, sở thích) của người đang nhắn tin cùng."""
        if not conversation_id and not contact_id:
            return "Không xác định được cuộc trò chuyện hiện tại."
        
        from src.api.deps import SessionLocal
        from src.models.chat import Conversation
        from src.models.ai import AssistantMemory
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
                        AssistantMemory.conversation_id == conv.id
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
                    
                    return f"Thông tin về {name}:\n- Chuyên môn: {profession}\n- Công ty: {company}\n- Địa điểm: {location}\n- Kỹ năng: {', '.join(skills) if skills else 'Chưa có'}\n- Quan tâm: {', '.join(interests) if interests else 'Chưa có'}\n- Tóm tắt AI: {summary}"
            
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
    def goi_y_cau_tra_loi(tone: str = "friendly") -> str:
        """Gợi ý câu trả lời cho tin nhắn mới nhất trong đoạn chat. Tone: 'friendly', 'professional', 'casual'."""
        if not conversation_id and not contact_id:
            return "Không xác định được cuộc trò chuyện."
            
        from src.api.deps import SessionLocal
        from src.models.chat import Conversation, Message
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


    tools = [semantic_search, xem_tin_nhan_gan_day, xem_thong_tin_nguoi_dang_chat, goi_y_cau_tra_loi]
    llm_with_tools = chat_model.bind_tools(tools)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query)
    ]

    tools_used = []
    try:
        response = llm_with_tools.invoke(messages)
        
        if response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tools_used.append(tool_name)
                
                # Execute the correct tool
                if tool_name == "semantic_search":
                    tool_result = semantic_search.invoke(tool_call["args"])
                elif tool_name == "xem_tin_nhan_gan_day":
                    tool_result = xem_tin_nhan_gan_day.invoke(tool_call["args"])
                elif tool_name == "xem_thong_tin_nguoi_dang_chat":
                    tool_result = xem_thong_tin_nguoi_dang_chat.invoke(tool_call["args"])
                elif tool_name == "goi_y_cau_tra_loi":
                    tool_result = goi_y_cau_tra_loi.invoke(tool_call["args"])
                else:
                    tool_result = "Tool không tồn tại."
                    
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))
            
            # Call LLM again to formulate final answer
            final_response = llm_with_tools.invoke(messages)
            response_content = final_response.content
        else:
            response_content = response.content

        intent_val = _classify_intent(query, llm_gateway).value if not tools_used else "SEARCH"

        return {
            "response": response_content,
            "intent": intent_val,
            "tools_used": tools_used,
            "is_valid": True,
        }

    except Exception as e:
        logger.error(f"LLM tool calling failed: {e}")
        return {
            "response": "Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau.",
            "intent": "ERROR",
            "is_valid": False,
        }
