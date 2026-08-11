from src.models.user import Notification
from src.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    pass

notification_repo = NotificationRepository(Notification)
