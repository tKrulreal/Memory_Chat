#!/usr/bin/env python3
"""
MemoryChat Seed Script
======================
Creates demo data for testing and development.

Demo User: demo@example.com / demo123
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.models.chat import Conversation, Message
from src.models.contact import Contact, ContactMemory
from src.models.database import SessionLocal
from src.models.user import User
from src.schemas.enums import MessageRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

VN_TZ = timezone(timedelta(hours=7))

# Demo user credentials
DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo123"
DEMO_NAME = "Demo User"


from src.core.security import get_password_hash

def create_demo_user(db) -> User:
    """Create or get demo user."""
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if user:
        logger.info(f"Demo user already exists: {user.email}")
        return user

    user = User(
        email=DEMO_EMAIL,
        password_hash=get_password_hash(DEMO_PASSWORD),
        full_name=DEMO_NAME,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Created demo user: {user.email}")
    return user


def create_contacts(db, user: User) -> list[Contact]:
    """Create 5 demo contacts with different professions."""

    contact_data = [
        {
            "name": "Nguyễn Văn A",
            "profession": "Giáo viên",
            "company": "Trường THPT Chu Văn An",
            "summary": "Giáo viên dạy Toán cấp 3, 40 tuổi, thích đi bộ và đọc sách",
            "skills": ["dạy học", "toán học", "giáo dục"],
            "interest": {"interests": ["sách", "du lịch", "ẩm thực"]},
            "relationship_score": 60,
            "last_message": "Hôm nào cà phê nhé",
            "days_ago": 10,  # For FOLLOWUP rule
        },
        {
            "name": "Trần Thị B",
            "profession": "Lập trình viên",
            "company": "FPT Software",
            "summary": "Backend developer, 28 tuổi, chuyên Python và Go",
            "skills": ["python", "golang", "docker", "kubernetes"],
            "interest": {"interests": ["AI", "startup", "game"]},
            "relationship_score": 70,
            "last_message": "Bạn gửi báo giá cho mình chưa?",
            "days_ago": 1,  # For REPLY rule
            "hours_ago": 30,  # > 24h since last contact message
        },
        {
            "name": "Lê Văn C",
            "profession": "Bác sĩ",
            "company": "Bệnh viện Bạch Mai",
            "summary": "Bác sĩ nội khoa, 45 tuổi, chuyên gia về tim mạch",
            "skills": ["chẩn đoán", "nội khoa", "tim mạch"],
            "interest": {"interests": ["yoga", "thiền", "nấu ăn"]},
            "relationship_score": 95,  # For PRIORITY rule
            "last_message": "Cảm ơn bạn, rất vui được gặp bạn",
            "days_ago": 0,
        },
        {
            "name": "Phạm Thị D",
            "profession": "Kế toán",
            "company": "Viettel",
            "summary": "Kế toán trưởng, 35 tuổi, thích shopping và làm bánh",
            "skills": ["kế toán", "tài chính", "excel"],
            "interest": {"interests": ["shopping", "làm bánh", "mỹ phẩm"]},
            "relationship_score": 50,
            "last_message": "Cuối tuần rảnh không?",
            "days_ago": 3,
        },
        {
            "name": "Hoàng Văn E",
            "profession": "Kiến trúc sư",
            "company": "Công ty AKA",
            "summary": "Kiến trúc sư, 32 tuổi, thích vẽ và chụp ảnh",
            "skills": ["autocad", "sketchup", "vẽ", "nhiếp ảnh"],
            "interest": {"interests": ["kiến trúc", "du lịch", "nhiếp ảnh"]},
            "relationship_score": 65,
            "last_message": "Mình đang cần tư vấn về thiết kế nội thất",
            "days_ago": 1,
        },
    ]

    contacts = []
    now = datetime.now(VN_TZ)

    for i, data in enumerate(contact_data):
        # Create a user for the contact since Conversation requires two Users
        email = f"contact_{i}@example.com"
        contact_user = db.query(User).filter(User.email == email).first()
        if not contact_user:
            contact_user = User(
                email=email,
                password_hash=get_password_hash("password"),
                full_name=data["name"],
            )
            db.add(contact_user)
            db.commit()
            db.refresh(contact_user)

        # Create contact
        contact = Contact(
            owner_user_id=user.id,
            display_name=data["name"],
            phone=f"+84{random_phone()}",  # type: ignore
            avatar_url=f"https://api.dicebear.com/7.x/initials/svg?seed={data['name']}",
            profession=data["profession"],
            company=data["company"],
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        contacts.append(contact)

        # Create memory
        memory = ContactMemory(
            contact_id=contact.id,
            summary=data["summary"],
            skills=data["skills"],
            interests=data.get("interest", {}).get("interests", []),
            relationship_score=data["relationship_score"],
        )
        db.add(memory)

        # Create conversation
        hours_ago = data.get("hours_ago", data.get("days_ago", 0) * 24)
        last_time = now - timedelta(hours=hours_ago)

        user_a_id = min(user.id, contact_user.id)
        user_b_id = max(user.id, contact_user.id)

        conversation = Conversation(
            user_a_id=user_a_id,
            user_b_id=user_b_id,
            last_message_content=data["last_message"],
            last_message_time=last_time,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Link conversation to contact
        contact.conversation_id = conversation.id
        db.commit()

        # Create sample messages
        _create_sample_messages(db, conversation, user, contact_user, data, last_time)

        logger.info(f"Created contact: {data['name']} with conversation and memory")

    return contacts


def _create_sample_messages(db, conversation, user, contact_user, data: dict, last_time: datetime):
    """Create sample messages for a conversation."""
    messages = [
        (MessageRole.USER, f"Xin chào {contact_user.full_name}!"),
        (MessageRole.CONTACT, f"Chào bạn! Rất vui được trò chuyện."),
        (MessageRole.USER, f"Bạn là {data['profession']} đúng không?"),
        (MessageRole.CONTACT, f"Đúng rồi! Mình làm ở {data['company']}."),
        (MessageRole.USER, data["last_message"]),
    ]

    for i, (sender, content) in enumerate(messages):
        # Last message should have last_time
        if i == len(messages) - 1:
            msg_time = last_time
        else:
            msg_time = last_time - timedelta(minutes=(len(messages) - i) * 10)

        message = Message(
            conversation_id=conversation.id,
            sender_user_id=user.id if sender == MessageRole.USER else contact_user.id,
            content=content,
            message_type="TEXT",
        )
        db.add(message)

    db.commit()


def random_phone() -> str:
    """Generate random Vietnamese phone number."""
    import random
    return "".join([str(random.randint(0, 9)) for _ in range(9)])


def seed_data():
    """Main seeding function."""
    logger.info("🌱 Starting MemoryChat seed...")
    logger.info("=" * 50)

    db = SessionLocal()
    try:
        # Create demo user
        user = create_demo_user(db)

        # Clear existing contacts for this user (optional - comment out to keep existing)
        existing = db.query(Contact).filter(Contact.user_id == user.id).count()
        if existing > 0:
            logger.info(f"Found {existing} existing contacts. Skipping contact creation.")
            logger.info("To re-seed, delete existing contacts first.")
        else:
            # Create contacts
            contacts = create_contacts(db, user)

            logger.info("")
            logger.info("=" * 50)
            logger.info("✅ Seed completed successfully!")
            logger.info("")
            logger.info("📋 Demo credentials:")
            logger.info(f"   Email: {DEMO_EMAIL}")
            logger.info(f"   Password: {DEMO_PASSWORD}")
            logger.info("")
            logger.info("📊 Data created:")
            logger.info(f"   - User: 1")
            logger.info(f"   - Contacts: {len(contacts)}")
            logger.info(f"   - Conversations: {len(contacts)}")
            logger.info(f"   - Messages: ~{len(contacts) * 5}")
            logger.info(f"   - Memories: {len(contacts)}")
            logger.info("")

    except Exception as e:
        logger.error(f"❌ Seed failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
