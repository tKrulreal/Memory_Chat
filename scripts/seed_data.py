import sys
import os
import uuid
import random
from datetime import datetime, timezone, timedelta

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.models.database import engine
from src.models.user import User, UserProfile
from src.models.tag import Tag, UserTag
from src.models.connection import ConnectionRequest
from src.models.chat import Conversation, ConversationUserState, Message
from src.core.security import get_password_hash

def seed_data(reset=False):
    with Session(engine) as session:
        if reset:
            print("Resetting data...")
            session.query(Message).delete()
            session.query(ConversationUserState).delete()
            session.query(Conversation).delete()
            session.query(ConnectionRequest).delete()
            session.query(UserTag).delete()
            session.query(Tag).delete()
            session.query(UserProfile).delete()
            session.query(User).delete()
            session.commit()
            print("Data reset complete.")

        print("Reading taikhoan.txt...")
        try:
            with open("taikhoan.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print("taikhoan.txt not found!")
            return

        users = []
        for line in lines[1:]: # Skip header
            if not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                full_name = parts[1]
                email = parts[2]
                password = parts[3]
                
                # Check if user exists
                user = session.query(User).filter(User.email == email).first()
                if not user:
                    user = User(
                        id=uuid.uuid4(),
                        email=email,
                        password_hash=get_password_hash(password),
                        full_name=full_name,
                        gender=random.choice(["Male", "Female"]),
                        phone=f"09{random.randint(10000000, 99999999)}"
                    )
                    session.add(user)
                users.append(user)
        
        session.commit()
        print(f"Seeded {len(users)} users.")

        # Seed Profiles
        professions = ["Backend Developer", "Frontend Developer", "Product Manager", "Data Scientist", "UI/UX Designer", "DevOps Engineer", "Mobile Developer"]
        skills_pool = ["Python", "Java", "React", "Node.js", "AWS", "SQL", "Docker", "Machine Learning", "Figma", "Go", "C++"]
        interests_pool = ["AI", "Blockchain", "Startups", "Gaming", "Music", "Reading", "Traveling", "Photography", "Investing"]
        
        for user in users:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            if not profile:
                profile = UserProfile(
                    user_id=user.id,
                    bio=f"Xin chào, tôi là {user.full_name}. Rất vui được kết nối!",
                    profession=random.choice(professions),
                    company="Tech Innovators VN",
                    location="Hà Nội, Việt Nam" if random.random() > 0.5 else "TP. HCM, Việt Nam",
                    skills=random.sample(skills_pool, k=random.randint(2, 4)),
                    interests=random.sample(interests_pool, k=random.randint(2, 4)),
                    looking_for=["Networking", "Mentorship", "Collaboration"],
                    offering=["Experience", "Code Review"]
                )
                session.add(profile)
        session.commit()
        print("Seeded user profiles.")

        # Seed Tags
        tags_dict = {}
        for tag_name in skills_pool + interests_pool:
            tag = session.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(id=uuid.uuid4(), name=tag_name, category="skill" if tag_name in skills_pool else "interest")
                session.add(tag)
            tags_dict[tag_name] = tag
        session.commit()

        for user in users:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            if profile:
                for t_name in (profile.skills or []) + (profile.interests or []):
                    tag = tags_dict.get(t_name)
                    if tag:
                        existing_ut = session.query(UserTag).filter(UserTag.user_id == user.id, UserTag.tag_id == tag.id).first()
                        if not existing_ut:
                            session.add(UserTag(id=uuid.uuid4(), user_id=user.id, tag_id=tag.id))
        session.commit()
        print("Seeded tags and user tags.")

        # Seed Connections & Conversations
        print("Seeding connections and conversations...")
        n = len(users)
        for i in range(n):
            # Connect with the next 5 users (wrap around)
            for j in range(1, 6):
                target_idx = (i + j) % n
                if i >= target_idx:
                    continue # To avoid duplicates (only i < target_idx creates connection)
                
                u1 = users[i]
                u2 = users[target_idx]
                
                # Check connection
                conn = session.query(ConnectionRequest).filter(
                    ConnectionRequest.sender_id == u1.id,
                    ConnectionRequest.receiver_id == u2.id
                ).first()
                
                if not conn:
                    conn = ConnectionRequest(
                        id=uuid.uuid4(),
                        sender_id=u1.id,
                        receiver_id=u2.id,
                        status="ACCEPTED"
                    )
                    session.add(conn)
                    
                    # Create conversation
                    ua_id, ub_id = sorted([u1.id, u2.id])
                    conv = Conversation(
                        id=uuid.uuid4(),
                        user_a_id=ua_id,
                        user_b_id=ub_id,
                        type="P2P"
                    )
                    session.add(conv)
                    
                    # Add states
                    session.add(ConversationUserState(id=uuid.uuid4(), conversation_id=conv.id, user_id=u1.id))
                    session.add(ConversationUserState(id=uuid.uuid4(), conversation_id=conv.id, user_id=u2.id))
                    session.commit()

                    # Seed messages
                    msgs = [
                        f"Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?",
                        f"Mình đang tập trung nghiên cứu AI và phát triển Backend.",
                        f"Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.",
                        f"Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!",
                        f"Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé."
                    ]
                    base_time = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10))
                    for idx, text in enumerate(msgs):
                        sender = u1 if idx % 2 == 0 else u2
                        m = Message(
                            id=uuid.uuid4(),
                            conversation_id=conv.id,
                            sender_user_id=sender.id,
                            content=text,
                            message_type="TEXT",
                            created_at=base_time + timedelta(minutes=idx * 5)
                        )
                        session.add(m)
                    session.commit()

        print("Seeding completed successfully!")

if __name__ == "__main__":
    reset = "--reset" in sys.argv
    seed_data(reset=reset)
