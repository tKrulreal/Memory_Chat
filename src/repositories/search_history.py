from src.models.user import SearchHistory
from src.repositories.base import BaseRepository


class SearchHistoryRepository(BaseRepository[SearchHistory]):
    pass

search_history_repo = SearchHistoryRepository(SearchHistory)
