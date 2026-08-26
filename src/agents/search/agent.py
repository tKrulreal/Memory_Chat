import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any

from src.agents.search.schemas import SearchResult
from src.api.deps import SessionLocal
from src.gateways.llm import LLMGateway
from src.models.ai import AssistantMemory
from src.models.chat import Conversation
from src.models.user import User, UserProfile
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class SearchAgent:
    def __init__(self, llm: LLMGateway | None = None):
        self.llm = llm or LLMGateway()
        self.vector_store = VectorStoreService.get_instance()
        self.log_file = ".ai-log/search.jsonl"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _log_search(self, query: str, results: list[SearchResult]):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results": [r.model_dump() for r in results],
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write log: {e}")

    def _build_rerank_prompt(self, query: str, candidate_pool: list[dict[str, Any]]) -> tuple[str, str]:
        system_prompt = (
            "Bạn là một trợ lý AI phân tích và tìm kiếm người liên hệ/người dùng phù hợp nhất trong hệ thống.\n"
            "Danh sách ứng viên bao gồm:\n"
            "1. Những người ĐÃ TỪNG CHAT (has_chatted=true, có conversation_id, có thông tin tóm tắt AI, lần gặp, tags, tin nhắn).\n"
            "2. Những người CHƯA TỪNG CHAT (has_chatted=false, chưa có conversation_id, tìm dựa theo thông tin hồ sơ profile như kỹ năng, sở thích, nghề nghiệp, công ty, bio).\n\n"
            "Nhiệm vụ: Đánh giá độ liên quan của từng người đối với câu truy vấn của người dùng (score từ 0 đến 100).\n"
            "Chỉ trả về JSON hợp lệ (mảng các JSON object), không kèm theo văn bản giải thích nào khác.\n"
            "Định dạng mỗi object:\n"
            "[\n"
            "  {\n"
            '    "conversation_id": "...",\n'
            '    "user_id": "...",\n'
            '    "has_chatted": true/false,\n'
            '    "name": "...",\n'
            '    "email": "...",\n'
            '    "profession": "...",\n'
            '    "company": "...",\n'
            '    "skills": ["..."],\n'
            '    "interests": ["..."],\n'
            '    "tags": ["..."],\n'
            '    "score": 85,\n'
            '    "explanation": "Giải thích ngắn gọn súc tích lý do người này phù hợp với truy vấn"\n'
            "  }\n"
            "]\n"
            "Sắp xếp theo score từ cao xuống thấp. Loại bỏ người có score < 20."
        )

        user_prompt = (
            f"Câu truy vấn tìm kiếm: {query}\n\n"
            f"Danh sách ứng viên cần đánh giá:\n"
            f"{json.dumps(candidate_pool, ensure_ascii=False, indent=2)}"
        )

        return system_prompt, user_prompt

    def search(self, query: str, user_id: str, limit: int = 5) -> list[SearchResult]:
        """
        Tìm kiếm đa nguồn:
        - Tìm trong các đoạn chat cũ (AI summary, last_met, interested_in, follow_up, tags, tin nhắn vector store).
        - Tìm trong toàn bộ hồ sơ người dùng chưa từng chat (skills, interests, profession, company, bio, looking_for).
        """
        if not user_id:
            return []

        db = SessionLocal()
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        candidate_pool: list[dict[str, Any]] = []

        try:
            # 1. Thu thập danh sách các cuộc trò chuyện hiện có (Người ĐÃ TỪNG CHAT)
            conversations = db.query(Conversation).filter(
                (Conversation.user_a_id == user_uuid) | (Conversation.user_b_id == user_uuid)
            ).all()

            chatted_user_ids: set[uuid.UUID] = set()

            # Lấy thêm kết quả từ Vector Store cho các đoạn chat cũ
            vector_docs_by_conv: dict[str, list[str]] = {}
            try:
                query_embedding = self.llm.embed(query)
                vector_results = self.vector_store.query(
                    query_embedding=query_embedding,
                    owner_user_id=str(user_uuid),
                    conversation_id=None,
                    top_k=10,
                )
                if vector_results and vector_results.get("documents"):
                    for doc, meta in zip(vector_results["documents"], vector_results["metadatas"]):
                        cid = meta.get("conversation_id")
                        if cid:
                            vector_docs_by_conv.setdefault(str(cid), []).append(doc)
            except Exception as e:
                logger.warning(f"Vector search failed or skipped: {e}")

            for conv in conversations:
                peer_id = conv.user_b_id if conv.user_a_id == user_uuid else conv.user_a_id
                chatted_user_ids.add(peer_id)

                peer_user = db.get(User, peer_id)
                peer_prof = db.query(UserProfile).filter(UserProfile.user_id == peer_id).first()
                mem = db.query(AssistantMemory).filter(
                    AssistantMemory.owner_user_id == user_uuid,
                    AssistantMemory.conversation_id == conv.id,
                ).first()

                facts = mem.facts if mem and mem.facts else {}
                tags = facts.get("tags", []) if isinstance(facts.get("tags"), list) else []
                interested_in = facts.get("interested_in", [])
                if isinstance(interested_in, dict):
                    interested_in = interested_in.get("interests", [])
                elif not isinstance(interested_in, list):
                    interested_in = []

                name = str(getattr(peer_user, "full_name", "") or getattr(peer_user, "email", "") or "Người liên hệ")
                email = str(getattr(peer_user, "email", "") or "")
                profession = str(getattr(peer_prof, "profession", "") or facts.get("profession", ""))
                company = str(getattr(peer_prof, "company", "") or facts.get("company", ""))
                raw_skills = getattr(peer_prof, "skills", None) or facts.get("skills", [])
                skills = [str(s) for s in raw_skills] if isinstance(raw_skills, (list, tuple)) else []
                raw_interests = getattr(peer_prof, "interests", None) or interested_in
                interests = [str(i) for i in raw_interests] if isinstance(raw_interests, (list, tuple)) else []
                summary = str(getattr(mem, "summary", "") or "")
                last_met = str(facts.get("last_met", "") or "")
                follow_up = str(facts.get("follow_up", "") or "")
                relevant_chat_msgs = [str(m) for m in vector_docs_by_conv.get(str(conv.id), [])]

                candidate_pool.append({
                    "conversation_id": str(conv.id),
                    "user_id": str(peer_id),
                    "has_chatted": True,
                    "name": name,
                    "email": email,
                    "profession": profession,
                    "company": company,
                    "skills": skills,
                    "interests": interests,
                    "tags": [str(t) for t in tags],
                    "last_met": last_met,
                    "ai_summary": summary,
                    "follow_up": follow_up,
                    "recent_chat_snippets": relevant_chat_msgs[:3],
                })

            # 2. Thu thập người dùng khác trong hệ thống CHƯA TỪNG CHAT (Chỉ tìm theo profile CÔNG KHAI is_public=True)
            non_chatted_users = db.query(User).filter(
                User.id != user_uuid,
                ~User.id.in_(chatted_user_ids) if chatted_user_ids else True,
            ).limit(40).all()

            for user in non_chatted_users:
                prof = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                # Kiểm tra cơ chế công khai profile: nếu người dùng tắt công khai (is_public = False) thì bỏ qua
                if prof and prof.is_public is False:
                    continue

                name = str(getattr(user, "full_name", "") or getattr(user, "email", "") or "Người dùng")
                profession = str(getattr(prof, "profession", "") or "")
                company = str(getattr(prof, "company", "") or "")
                location = str(getattr(prof, "location", "") or "")
                raw_skills = getattr(prof, "skills", [])
                skills = [str(s) for s in raw_skills] if isinstance(raw_skills, (list, tuple)) else []
                raw_interests = getattr(prof, "interests", [])
                interests = [str(i) for i in raw_interests] if isinstance(raw_interests, (list, tuple)) else []
                bio = str(getattr(prof, "bio", "") or "")
                looking_for = str(getattr(prof, "looking_for", "") or "")
                offering = str(getattr(prof, "offering", "") or "")
                raw_exp = getattr(prof, "experience", []) or []
                exp_titles = [f"{e.get('title', '')} tại {e.get('company', '')}" for e in raw_exp if isinstance(e, dict)]
                raw_edu = getattr(prof, "education", []) or []
                edu_titles = [f"{e.get('school', '')} - {e.get('degree', '')}" for e in raw_edu if isinstance(e, dict)]

                candidate_pool.append({
                    "conversation_id": "",
                    "user_id": str(getattr(user, "id", "")),
                    "has_chatted": False,
                    "name": name,
                    "email": str(getattr(user, "email", "") or ""),
                    "profession": profession,
                    "company": company,
                    "location": location,
                    "skills": skills,
                    "interests": interests,
                    "tags": [],
                    "bio": bio,
                    "looking_for": looking_for,
                    "offering": offering,
                    "experience": exp_titles,
                    "education": edu_titles,
                })


        except Exception as e:
            logger.error(f"Error fetching candidate pool: {e}")
        finally:
            db.close()

        if not candidate_pool:
            return []

        # 3. Tính điểm sơ bộ (Pre-scoring heuristic) để ưu tiên các ứng viên tiềm năng trước khi gửi LLM
        query_words = [w.lower() for w in query.split() if len(w) > 1]
        scored_candidates = []
        for cand in candidate_pool:
            text_repr = (
                f"{cand.get('name', '')} {cand.get('email', '')} {cand.get('profession', '')} "
                f"{cand.get('company', '')} {' '.join(cand.get('skills', []))} {' '.join(cand.get('interests', []))} "
                f"{' '.join(cand.get('tags', []))} {cand.get('ai_summary', '')} {cand.get('last_met', '')} "
                f"{cand.get('bio', '')} {cand.get('looking_for', '')} {cand.get('offering', '')} "
                f"{' '.join(cand.get('recent_chat_snippets', []))}"
            ).lower()

            match_count = sum(1 for w in query_words if w in text_repr)
            scored_candidates.append((match_count, cand))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        # Giữ tối đa 12 ứng viên tiềm năng nhất để LLM rerank
        top_candidates = [c[1] for c in scored_candidates[:12]]

        # 4. LLM Re-ranking & Semantic Reasoning
        system_prompt, user_prompt = self._build_rerank_prompt(query, top_candidates)
        try:
            response_text = self.llm.chat(system_prompt=system_prompt, user_prompt=user_prompt)

            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()

            parsed_results = json.loads(response_text)

            results: list[SearchResult] = []
            for item in parsed_results:
                if isinstance(item, dict):
                    # Guarantee fields
                    conv_id = str(item.get("conversation_id") or "")
                    user_id_val = str(item.get("user_id") or "")
                    has_chatted = bool(item.get("has_chatted", bool(conv_id)))
                    results.append(
                        SearchResult(
                            conversation_id=conv_id,
                            user_id=user_id_val,
                            has_chatted=has_chatted,
                            name=str(item.get("name") or "Người liên hệ"),
                            email=str(item.get("email") or ""),
                            profession=str(item.get("profession") or ""),
                            company=str(item.get("company") or ""),
                            skills=item.get("skills") if isinstance(item.get("skills"), list) else [],
                            interests=item.get("interests") if isinstance(item.get("interests"), list) else [],
                            tags=item.get("tags") if isinstance(item.get("tags"), list) else [],
                            score=int(item.get("score") or 0),
                            explanation=str(item.get("explanation") or ""),
                        )
                    )

            results.sort(key=lambda x: x.score, reverse=True)
            final_results = results[:limit]
            self._log_search(query, final_results)
            return final_results

        except Exception as e:
            logger.error(f"Error in LLM re-ranking: {e}")
            fallback_results: list[SearchResult] = []
            for cand in top_candidates[:limit]:
                fallback_results.append(
                    SearchResult(
                        conversation_id=cand.get("conversation_id", ""),
                        user_id=cand.get("user_id", ""),
                        has_chatted=cand.get("has_chatted", False),
                        name=cand.get("name", "Người liên hệ"),
                        email=cand.get("email", ""),
                        profession=cand.get("profession", ""),
                        company=cand.get("company", ""),
                        skills=cand.get("skills", []),
                        interests=cand.get("interests", []),
                        tags=cand.get("tags", []),
                        score=50,
                        explanation="Tìm thấy thông tin khớp từ khóa trong hệ thống.",
                    )
                )
            self._log_search(query, fallback_results)
            return fallback_results
