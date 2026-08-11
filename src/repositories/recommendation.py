
from sqlalchemy.orm import Session

from src.models.ai import Recommendation
from src.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    def list_pending(self, db: Session, limit: int = 100) -> list[Recommendation]:
        return db.query(self.model).filter(self.model.status == "pending").limit(limit).all()

recommendation_repo = RecommendationRepository(Recommendation)
