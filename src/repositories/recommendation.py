from typing import List
from sqlalchemy.orm import Session
from src.repositories.base import BaseRepository
from src.models.ai import Recommendation

class RecommendationRepository(BaseRepository[Recommendation]):
    def list_pending(self, db: Session, limit: int = 100) -> List[Recommendation]:
        return db.query(self.model).filter(self.model.status == "pending").limit(limit).all()

recommendation_repo = RecommendationRepository(Recommendation)
