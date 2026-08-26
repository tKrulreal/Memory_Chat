from src.services.event_log import EventLogService
from src.services.recommendation import RecommendationService


def test_extra_services():
    assert RecommendationService is not None
    assert EventLogService is not None

