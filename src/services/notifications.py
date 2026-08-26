import asyncio
import logging
import uuid
from typing import Any
from sqlalchemy.orm import Session

from src.models.user import Notification, User, UserProfile
from src.api.ws import manager

logger = logging.getLogger(__name__)


class NotificationService:
    _instance: "NotificationService | None" = None

    @classmethod
    def get_instance(cls) -> "NotificationService":
        if cls._instance is None:
            cls._instance = NotificationService()
        return cls._instance

    def create_notification(
        self,
        db: Session,
        user_id: uuid.UUID,
        type: str,
        title: str,
        content: str,
        data: dict[str, Any] | None = None,
    ) -> Notification:
        """Tạo notification trong DB và broadcast realtime qua WebSocket."""
        notif = Notification(
            user_id=user_id,
            type=type,
            title=title,
            content=content,
            data=data or {},
            status="UNREAD",
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        # Broadcast via WebSocket
        self._broadcast_notification(notif)
        return notif

    def _broadcast_notification(self, notif: Notification) -> None:
        try:
            payload = {
                "type": "NEW_NOTIFICATION",
                "notification": {
                    "id": str(notif.id),
                    "user_id": str(notif.user_id),
                    "type": notif.type,
                    "title": notif.title,
                    "content": notif.content,
                    "status": notif.status,
                    "data": notif.data,
                    "created_at": notif.created_at.isoformat() if notif.created_at else "",
                }
            }
            # Attempt to schedule broadcast in running loop
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.broadcast_to_user(notif.user_id, payload))
            except RuntimeError:
                # If no event loop in thread, run in new loop
                try:
                    asyncio.run(manager.broadcast_to_user(notif.user_id, payload))
                except Exception as inner_e:
                    logger.debug("Failed sync broadcast: %s", inner_e)
        except Exception as e:
            logger.warning("Failed to broadcast notification: %s", e)

    def send_matching_notification(
        self,
        db: Session,
        user_id: uuid.UUID,
        target_user: User,
        match_score: int,
        recommendation_id: uuid.UUID | str | None = None,
    ) -> Notification:
        """
        Tạo thông báo matching ngắn gọn theo yêu cầu:
        'Profile của người này hợp với bạn, hãy thử kết nối'
        """
        target_profile = db.query(UserProfile).filter(UserProfile.user_id == target_user.id).first()
        target_name = target_user.full_name or target_user.email
        notif_data = {
            "target_user_id": str(target_user.id),
            "target_name": target_name,
            "target_avatar": target_user.avatar,
            "target_profession": target_profile.profession if target_profile else None,
            "target_company": target_profile.company if target_profile else None,
            "target_location": target_profile.location if target_profile else None,
            "match_score": match_score,
            "recommendation_id": str(recommendation_id) if recommendation_id else None,
        }
        return self.create_notification(
            db=db,
            user_id=user_id,
            type="MATCH_SUGGESTION",
            title="Gợi ý kết nối AI",
            content="Profile của người này hợp với bạn, hãy thử kết nối",
            data=notif_data,
        )

    def send_connection_request_notification(
        self,
        db: Session,
        receiver_id: uuid.UUID,
        sender_user: User,
        request_id: uuid.UUID | str,
    ) -> Notification:
        """Tạo thông báo lời mời kết bạn mới."""
        sender_profile = db.query(UserProfile).filter(UserProfile.user_id == sender_user.id).first()
        sender_name = sender_user.full_name or sender_user.email
        if request_id is None or str(request_id) == "None":
            from src.models.connection import ConnectionRequest
            req = db.query(ConnectionRequest).filter(
                ConnectionRequest.sender_id == sender_user.id,
                ConnectionRequest.receiver_id == receiver_id,
                ConnectionRequest.status == "PENDING",
            ).first()
            req_id_str = str(req.id) if req else None
        else:
            req_id_str = str(request_id)

        notif_data = {
            "sender_id": str(sender_user.id),
            "sender_name": sender_name,
            "sender_avatar": sender_user.avatar,
            "sender_profession": sender_profile.profession if sender_profile else None,
            "sender_company": sender_profile.company if sender_profile else None,
            "request_id": req_id_str,
        }
        return self.create_notification(
            db=db,
            user_id=receiver_id,
            type="CONNECTION_REQUEST",
            title="Lời mời kết bạn mới",
            content=f"{sender_name} đã gửi cho bạn một lời mời kết bạn.",
            data=notif_data,
        )

    def send_connection_accepted_notification(
        self,
        db: Session,
        sender_id: uuid.UUID,
        receiver_user: User,
    ) -> Notification:
        """Tạo thông báo khi lời mời kết bạn được chấp nhận."""
        receiver_profile = db.query(UserProfile).filter(UserProfile.user_id == receiver_user.id).first()
        receiver_name = receiver_user.full_name or receiver_user.email
        notif_data = {
            "user_id": str(receiver_user.id),
            "user_name": receiver_name,
            "user_avatar": receiver_user.avatar,
            "user_profession": receiver_profile.profession if receiver_profile else None,
        }
        return self.create_notification(
            db=db,
            user_id=sender_id,
            type="CONNECTION_ACCEPTED",
            title="Lời mời kết bạn đã được chấp nhận",
            content=f"{receiver_name} đã chấp nhận lời mời kết bạn của bạn.",
            data=notif_data,
        )
