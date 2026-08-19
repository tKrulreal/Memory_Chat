import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.security import get_current_user
from src.gateways.llm import LLMGateway
from src.models.chat import Conversation
from src.models.user import User
from src.schemas.search import SearchResult
from src.schemas.conversation import ParticipantResponse
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/conversations", response_model=list[SearchResult])
def search_conversations(
    query: str = Query(..., description="Tìm kiếm người liên hệ theo ngữ cảnh"),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not query.strip():
        return []

    vector_results = None
    try:
        query_embedding = LLMGateway().embed(query)
        vector_results = VectorStoreService.get_instance().query(
            query_embedding=query_embedding,
            owner_user_id=str(current_user.id),
            conversation_id=None,
            top_k=top_k
        )
    except Exception as e:
        logger.warning(f"Vector search failed, falling back to DB: {e}")

    results = []

    if vector_results and vector_results.get("ids"):
        # Process vector search results
        for doc, meta in zip(vector_results["documents"], vector_results["metadatas"]):
            conversation_id_str = meta.get("conversation_id")
            if not conversation_id_str:
                continue
                
            try:
                conv_id = uuid.UUID(conversation_id_str)
            except ValueError:
                continue
                
            conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
            if not conv:
                continue
                
            peer = conv.user_b if str(conv.user_a_id) == str(current_user.id) else conv.user_a
            
            if any(r.conversation_id == conversation_id_str for r in results):
                continue
                
            results.append(SearchResult(
                conversation_id=conversation_id_str,
                peer=ParticipantResponse.model_validate(peer),
                summary_snippet=doc,
                score=1.0 
            ))
    else:
        # Graceful Fallback: Search by peer name or email in PostgreSQL
        from sqlalchemy import or_
        conversations = db.query(Conversation).filter(
            or_(
                Conversation.user_a_id == current_user.id,
                Conversation.user_b_id == current_user.id
            )
        ).all()
        
        query_lower = query.lower()
        for conv in conversations:
            peer = conv.user_b if str(conv.user_a_id) == str(current_user.id) else conv.user_a
            peer_name = (peer.full_name or "").lower()
            peer_email = (peer.email or "").lower()
            
            if query_lower in peer_name or query_lower in peer_email:
                results.append(SearchResult(
                    conversation_id=str(conv.id),
                    peer=ParticipantResponse.model_validate(peer),
                    summary_snippet="Tìm thấy thông tin khớp từ khóa.",
                    score=0.5
                ))
                if len(results) >= top_k:
                    break

    return results


