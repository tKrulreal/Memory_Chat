import logging
from datetime import datetime, timedelta, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.models.chat import Conversation, Message
from src.models.contact import Contact, ContactMemory
from src.models.database import SessionLocal
from src.models.user import User
from src.schemas.enums import MessageRole

VN_TZ = timezone(timedelta(hours=7))

def seed_data():
    db = SessionLocal()
    try:
        # Lấy User đầu tiên trong DB
        user = db.query(User).first()
        if not user:
            logger.error("Không tìm thấy user. Vui lòng chạy test_recommendation.py trước.")
            return

        logger.info(f"Seeding data for user: {user.email}")

        # Xóa dữ liệu cũ nếu có
        db.query(Contact).filter_by(user_id=user.id).delete()
        db.commit()

        now = datetime.now(VN_TZ)

        # 1. Contact 1: Sẽ dính rule FOLLOWUP (idle > 7 days)
        contact1 = Contact(user_id=user.id, display_name="Nguyễn Văn A (Lâu không gặp)")
        db.add(contact1)
        db.commit()
        db.refresh(contact1)

        mem1 = ContactMemory(contact_id=contact1.id, relationship_score=50, summary="Bạn cấp 3")
        db.add(mem1)

        conv1 = Conversation(user_id=user.id, contact_id=contact1.id,
                             last_message="Hôm nào cà phê nhé",
                             last_message_time=now - timedelta(days=10)) # > 7 ngày
        db.add(conv1)
        db.commit()
        db.refresh(conv1)

        msg1 = Message(conversation_id=conv1.id, sender_type=MessageRole.USER,
                       content="Hôm nào cà phê nhé", message_type="TEXT")
        # override created_at is tricky via ORM for auto fields, we just need the conversation's last_message_time for the rule.
        db.add(msg1)

        # 2. Contact 2: Sẽ dính rule REPLY (tin nhắn cuối từ contact > 24h)
        contact2 = Contact(user_id=user.id, display_name="Trần Thị B (Đang đợi rep)")
        db.add(contact2)
        db.commit()
        db.refresh(contact2)

        mem2 = ContactMemory(contact_id=contact2.id, relationship_score=60, summary="Khách hàng tiềm năng")
        db.add(mem2)

        conv2 = Conversation(user_id=user.id, contact_id=contact2.id,
                             last_message="Bạn gửi báo giá cho mình chưa?",
                             last_message_time=now - timedelta(hours=30)) # > 24h
        db.add(conv2)
        db.commit()
        db.refresh(conv2)

        msg2 = Message(conversation_id=conv2.id, sender_type=MessageRole.CONTACT,
                       content="Bạn gửi báo giá cho mình chưa?", message_type="TEXT")
        db.add(msg2)

        # 3. Contact 3: Sẽ dính rule PRIORITY (score > 80)
        contact3 = Contact(user_id=user.id, display_name="Phạm Văn C (VIP)")
        db.add(contact3)
        db.commit()
        db.refresh(contact3)

        mem3 = ContactMemory(contact_id=contact3.id, relationship_score=95, summary="Đối tác chiến lược VIP")
        db.add(mem3)

        conv3 = Conversation(user_id=user.id, contact_id=contact3.id,
                             last_message="Cảm ơn bạn",
                             last_message_time=now - timedelta(hours=2)) # Gần đây
        db.add(conv3)
        db.commit()

        db.commit()
        logger.info("Seed data hoàn tất! Đã tạo 3 contacts giả lập để test các rules: FOLLOWUP, REPLY, PRIORITY.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
