import json
import logging
import os
from datetime import datetime
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.search.schemas import SearchResult
from src.gateways.llm import LLMGateway
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self):
        self.llm = LLMGateway()
        self.vector_store = VectorStoreService.get_instance()
        self.log_file = ".ai-log/search.jsonl"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _log_search(self, query: str, results: list[SearchResult]):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results": [r.model_dump() for r in results]
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write log: {e}")

    def _build_rerank_prompt(self, query: str, grouped_memories: dict[str, dict[str, Any]]) -> tuple[str, str]:
        system_prompt = (
            "Bạn là một trợ lý AI phân tích dữ liệu. Nhiệm vụ của bạn là đánh giá mức độ liên quan "
            "giữa câu truy vấn của người dùng và thông tin ghi nhớ (memories) của các liên hệ (contacts).\n"
            "Chỉ trả về JSON hợp lệ, không kèm theo bất kỳ văn bản nào khác. Output phải là một array "
            "các object JSON có định dạng:\n"
            "[\n"
            "  {\n"
            '    "conversation_id": "...",\n'
            '    "name": "...",\n'
            '    "email": "...",\n'
            '    "score": 85,\n'
            '    "explanation": "Lý do vì sao liên hệ này phù hợp"\n'
            "  }\n"
            "]\n"
            "Score từ 0 đến 100. Hãy đánh giá kỹ dựa trên ngữ nghĩa câu query so với thông tin memory."
        )

        # Prepare context data
        context_data = []
        for conv_id, data in grouped_memories.items():
            context_data.append({
                "conversation_id": conv_id,
                "name": data.get("name", "Unknown"),
                "email": data.get("email", ""),
                "memories": data["memories"]
            })

        user_prompt = f"Query: {query}\n\nDanh sách contacts và memories:\n{json.dumps(context_data, ensure_ascii=False, indent=2)}"

        return system_prompt, user_prompt

    def search(self, query: str, user_id: str, limit: int = 5) -> list[SearchResult]:
        # 1. Embed query
        try:
            query_embedding = self.llm.embed(query)
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return []

        # 2. Query vector store
        try:
            vector_results = self.vector_store.query(
                query_embedding=query_embedding,
                owner_user_id=user_id,
                conversation_id=None,
                top_k=10
            )
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []

        if not vector_results["ids"]:
            return []

        # 3. Group by conversation
        grouped = {}
        from src.api.deps import SessionLocal
        from src.models.chat import Conversation
        from src.models.user import User
        import uuid
        
        db = SessionLocal()
        try:
            for doc, meta in zip(vector_results["documents"], vector_results["metadatas"]):
                conv_id_str = meta.get("conversation_id")
                if not conv_id_str:
                    continue

                if conv_id_str not in grouped:
                    contact_name = "Unknown"
                    contact_email = ""
                    try:
                        conv = db.get(Conversation, uuid.UUID(conv_id_str))
                        if conv:
                            other_user_id = conv.user_b_id if str(conv.user_a_id) == str(user_id) else conv.user_a_id
                            other_user = db.get(User, other_user_id)
                            if other_user:
                                if other_user.full_name:
                                    contact_name = other_user.full_name
                                if other_user.email:
                                    contact_email = other_user.email
                    except Exception as e:
                        logger.error(f"Error fetching user name: {e}")

                    grouped[conv_id_str] = {
                        "name": contact_name,
                        "email": contact_email,
                        "memories": []
                    }
                grouped[conv_id_str]["memories"].append(doc)
        finally:
            db.close()

        if not grouped:
            return []

        # 4. Re-rank with LLM
        system_prompt, user_prompt = self._build_rerank_prompt(query, grouped)
        try:
            response_text = self.llm.chat(system_prompt=system_prompt, user_prompt=user_prompt)

            # Extract json if wrapped in ```json ... ```
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()

            parsed_results = json.loads(response_text)

            results = []
            for item in parsed_results:
                results.append(SearchResult(**item))

            # 5. Sort and limit
            results.sort(key=lambda x: x.score, reverse=True)
            final_results = results[:limit]
            self._log_search(query, final_results)
            return final_results

        except Exception as e:
            logger.error(f"Error in LLM re-ranking: {e}")
            # Fallback: return without re-ranking (score=0)
            fallback_results = []
            for conv_id, data in grouped.items():
                fallback_results.append(SearchResult(
                    conversation_id=conv_id,
                    name=data["name"],
                    email=data.get("email", ""),
                    score=0,
                    explanation="Lỗi khi re-rank"
                ))
            final_results = fallback_results[:limit]
            self._log_search(query, final_results)
            return final_results
