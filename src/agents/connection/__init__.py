"""
Connection Recommendation Agent.

Finds opportunities to connect contacts based on complementary needs/offers.
"""

from src.agents.connection.agent import ConnectionRecommendationAgent
from src.agents.connection.schemas import ConnectionRecommendation

__all__ = ["ConnectionRecommendationAgent", "ConnectionRecommendation"]
