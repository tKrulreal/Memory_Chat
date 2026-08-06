from sqlalchemy.orm import Session
from src.repositories.recommendation import recommendation_repo
from src.models.ai import Recommendation

class RecommendationService:
    @staticmethod
    def list_pending(db: Session, limit: int = 100):
        return recommendation_repo.list_pending(db, limit=limit)
    
    @staticmethod
    def accept(db: Session, db_obj: Recommendation):
        return recommendation_repo.update(db, db_obj=db_obj, obj_in={"status": "accepted"})
    
    @staticmethod
    def reject(db: Session, db_obj: Recommendation):
        return recommendation_repo.update(db, db_obj=db_obj, obj_in={"status": "rejected"})
