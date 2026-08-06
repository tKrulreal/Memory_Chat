from src.repositories.event_log import event_log_repo
from src.repositories.memory import memory_repo
from src.repositories.recommendation import recommendation_repo


def test_extra_repos():
    # Just basic assertions to ensure they can be imported and initialized
    assert memory_repo is not None
    assert recommendation_repo is not None
    assert event_log_repo is not None
