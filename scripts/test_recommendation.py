import asyncio
import sys
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.models.database import SessionLocal, Base, engine
from src.models.user import User
from src.agents.recommendation import RecommendationAgent

async def main():
    logger.info("Initializing database metadata if needed...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Failed to connect or create tables: {e}")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Get first user or create one
        user = db.query(User).first()
        if not user:
            logger.info("No user found. Creating a dummy user for testing...")
            user = User(
                email="test_recommendation@example.com",
                password_hash="fake_hash",
                full_name="Test User"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        logger.info(f"Using user_id: {user.id}")

        logger.info("Running RecommendationAgent...")
        agent = RecommendationAgent()
        recs = await agent.generate(user_id=user.id)
        
        logger.info(f"Generated {len(recs)} recommendations.")
        for r in recs:
            logger.info(f"Type: {r.type} | Priority: {r.priority} | Reason: {r.reason}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
