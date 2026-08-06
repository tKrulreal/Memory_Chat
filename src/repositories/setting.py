from src.repositories.base import BaseRepository
from src.models.user import Setting

class SettingRepository(BaseRepository[Setting]):
    pass

setting_repo = SettingRepository(Setting)
