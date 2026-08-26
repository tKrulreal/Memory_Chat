from src.models.user import Setting
from src.repositories.base import BaseRepository


class SettingRepository(BaseRepository[Setting]):
    pass

setting_repo = SettingRepository(Setting)
