from src.repositories.base import BaseRepository
from src.models.user import Notification

class NotificationRepository(BaseRepository[Notification]):
    pass

notification_repo = NotificationRepository(Notification)
