from src.repositories.base import BaseRepository
from src.models.user import SearchHistory

class SearchHistoryRepository(BaseRepository[SearchHistory]):
    pass

search_history_repo = SearchHistoryRepository(SearchHistory)
