import logging
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

    try:
        query_embedding = LLMGateway.get_instance().embed(query)
    except Exception as e:
        logger.error(f"Error embedding query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process search query")

    try:
        vector_results = VectorStoreService.get_instance().query(
            query_embedding=query_embedding,
            owner_user_id=str(current_user.id),
            conversation_id=None,
            top_k=top_k
        )
    except Exception as e:
        logger.error(f"Error querying vector store: {e}")
        raise HTTPException(status_code=500, detail="Search service unavailable")

    if not vector_results["ids"]:
        return []

    results = []
    
    # In ChromaDB response, distances are returned. We don't have access to distances in the VectorSearchResult dict yet,
    # because VectorSearchResult doesn't include distances. Let's just mock score for now or omit it.
    # The documents list contains the snippet.
    for doc, meta in zip(vector_results["documents"], vector_results["metadatas"]):
        conversation_id_str = meta.get("conversation_id")
        if not conversation_id_str:
            continue
            
        # Find the conversation to get the peer
        conv = db.query(Conversation).filter(Conversation.id == conversation_id_str).first()
        if not conv:
            continue
            
        # Determine peer
        peer = conv.user_b if str(conv.user_a_id) == str(current_user.id) else conv.user_a
        
        # Avoid duplicates if multiple chunks from same conversation match
        if any(r.conversation_id == conversation_id_str for r in results):
            continue
            
        results.append(SearchResult(
            conversation_id=conversation_id_str,
            peer=ParticipantResponse.model_validate(peer),
            summary_snippet=doc,
            score=1.0  # Dummy score since distances aren't in VectorSearchResult
        ))

    return results
