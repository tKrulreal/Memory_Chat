"""
Seed Data Script - Only seeds users, profiles, and messages
NO AI-related mock data

Usage:
    python seed_data.py
"""

import uuid
from datetime import datetime, timedelta
import random

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/memorychat"

# Bcrypt hash for password123 (pre-generated)
PASSWORD_HASH = "$2b$12$PFyD4UbRbGseOFxCzuyg0e7RFkFegiZ34FipyrPku.2JSFiyozTQK"


# ============================================================
# 5 Users with realistic profiles
# ============================================================
USERS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "minh.tran@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Trần Minh",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=minh",
        "profession": "Software Engineer",
        "company": "TechCorp Vietnam",
        "location": "Ho Chi Minh City",
        "bio": "Backend developer với 5 năm kinh nghiệm. Yêu thích Python và Go.",
        "gender": "male",
        "phone": "+84901234567",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "lan.nguyen@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Nguyễn Thị Lan",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=lan",
        "profession": "Product Manager",
        "company": "StartupHub",
        "location": "Hanoi",
        "bio": "Product Manager đam mê giải quyết vấn đề người dùng. Thích đọc sách về tư duy thiết kế.",
        "gender": "female",
        "phone": "+84987654321",
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "khoa.pham@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Phạm Khoa",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=khoa",
        "profession": "Data Scientist",
        "company": "AI Labs",
        "location": "Da Nang",
        "bio": "Data Scientist tập trung vào NLP và Computer Vision. Luôn tìm kiếm insights từ dữ liệu.",
        "gender": "male",
        "phone": "+84911223344",
    },
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "email": "mai.le@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Lê Mai",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=mai",
        "profession": "UX Designer",
        "company": "Design Studio",
        "location": "Ho Chi Minh City",
        "bio": "Designer đam mê tạo ra trải nghiệm người dùng tuyệt vời. Thích sketch và prototyping.",
        "gender": "female",
        "phone": "+84955667788",
    },
    {
        "id": "55555555-5555-5555-5555-555555555555",
        "email": "hieu.vo@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Võ Hiếu",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=hieu",
        "profession": "DevOps Engineer",
        "company": "CloudFirst",
        "location": "Hanoi",
        "bio": "DevOps với niềm đam mê tự động hóa. Kinh nghiệm với Kubernetes và CI/CD.",
        "gender": "male",
        "phone": "+84999887766",
    },
]

# ============================================================
# Relationships: Minh (1) kết bạn với Lan (2) và Khoa (3)
# ============================================================
CONVERSATIONS = [
    # Conversation between Minh and Lan (user 1 and 2)
    {
        "id": "aaaa1111-1111-1111-1111-111111111111",
        "user_a_id": "11111111-1111-1111-1111-111111111111",
        "user_b_id": "22222222-2222-2222-2222-222222222222",
        "messages": [
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Chào Minh, rất vui được kết nối với bạn!"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Chào Lan! Mình cũng rất vui. Mình thấy bạn làm PM ở StartupHub phải không?"},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Đúng rồi! Mình đang làm PM cho sản phẩm về EdTech. Bạn làm backend ở TechCorp hả?"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Mình làm backend, chủ yếu với Python và Go. Có cơ hội hợp tác không?"},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Có thể lắm! Chúng mình đang cần một backend developer cho tính năng mới. Gặp nhau uống coffee được không?"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Tuyệt vời! Cuối tuần này thì sao?"},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Ok, Saturday 3h chiều nhé. Mình sẽ gửi địa điểm."},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Perfect, see you then!"},
        ],
    },
    # Conversation between Minh and Khoa (user 1 and 3)
    {
        "id": "aaaa2222-2222-2222-2222-222222222222",
        "user_a_id": "11111111-1111-1111-1111-111111111111",
        "user_b_id": "33333333-3333-3333-3333-333333333333",
        "messages": [
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Hey Minh, thấy bạn làm backend. Mình đang cần tư vấn về kiến trúc hệ thống cho project ML."},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Chào Khoa! Mình sẵn sàng giúp. Bạn đang gặp vấn đề gì?"},
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Mình đang xây dựng một pipeline để xử lý NLP data. Không biết nên dùng Kafka hay RabbitMQ?"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Nếu bạn cần throughput cao và độ bền message tốt, mình khuyên Kafka. RabbitMQ phù hợp với queue đơn giản hơn."},
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Cảm ơn bạn! Về phần serving model, bạn có gợi ý gì không?"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Với NLP model, mình thường dùng FastAPI + uvicorn. Đơn giản và hiệu quả. Hoặc bạn có thể thử TorchServe nếu cần nhiều optimization hơn."},
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Mình sẽ thử FastAPI trước. Cảm ơn nhiều nhé!"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Không có gì. Có gì không hiểu cứ hỏi mình nhé."},
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Btw, bạn có muốn tham gia talk về AI tại công ty mình tuần sau không?"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Sounds interesting! Địa điểm và thời gian như nào?"},
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Thứ 7, 2pm tại AI Labs, quận 1. Mình sẽ talk về LLM applications."},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Mình sẽ đến. Thanks for the invite!"},
        ],
    },
    # Conversation between Lan and Mai (user 2 and 4) - no friendship with Minh
    {
        "id": "aaaa3333-3333-3333-3333-333333333333",
        "user_a_id": "22222222-2222-2222-2222-222222222222",
        "user_b_id": "44444444-4444-4444-4444-444444444444",
        "messages": [
            {"sender": "44444444-4444-4444-4444-444444444444", "content": "Chào Lan! Mình là Mai, designer mới của StartupHub."},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Welcome Mai! Rất vui được làm việc cùng bạn. Bạn đến từ đâu?"},
            {"sender": "44444444-4444-4444-4444-444444444444", "content": "Mình từ Sài Gòn, trước làm ở Design Studio. Rất háo hức được làm product mới!"},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Tuyệt! Product của chúng mình tập trung vào học tiếng Anh cho trẻ em. Bạn có kinh nghiệm với edtech không?"},
            {"sender": "44444444-4444-4444-4444-444444444444", "content": "Chưa có nhưng mình rất thích làm việc với trẻ em. Mình đã làm một vài project về gamification trước đây."},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Perfect! Chúng mình đang cần ai đó giúp thiết kế UI/UX cho phần game hóa. Gặp mình tuần này để discuss chi tiết nhé?"},
            {"sender": "44444444-4444-4444-4444-444444444444", "content": "Được luôn! Thứ 3 sáng được không?"},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Ok, 10h sáng thứ 3. Mình sẽ chuẩn bị tài liệu."},
        ],
    },
]


def generate_sql():
    """Generate SQL for seed data"""
    now = datetime.utcnow()
    sql_statements = []

    # ============================================================
    # USERS
    # ============================================================
    for user in USERS:
        sql = f"""
INSERT INTO users (id, email, password_hash, full_name, avatar, gender, phone, created_at, updated_at, is_ai)
VALUES (
    '{user["id"]}',
    '{user["email"]}',
    '{user["password_hash"]}',
    '{user["full_name"]}',
    '{user["avatar"]}',
    '{user.get("gender", "")}',
    '{user.get("phone", "")}',
    '{now.isoformat()}',
    '{now.isoformat()}',
    false
) ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    full_name = EXCLUDED.full_name,
    avatar = EXCLUDED.avatar,
    gender = EXCLUDED.gender,
    phone = EXCLUDED.phone,
    updated_at = EXCLUDED.updated_at;
"""
        sql_statements.append(sql.strip())

        # ============================================================
        # SETTINGS (default settings for each user)
        # ============================================================
        settings_sql = f"""
INSERT INTO settings (user_id, auto_tag, auto_memory, theme, language, notification)
VALUES (
    '{user["id"]}',
    true,
    true,
    'light',
    'vi',
    true
) ON CONFLICT (user_id) DO NOTHING;
"""
        sql_statements.append(settings_sql.strip())

        # ============================================================
        # USER_PROFILES (basic profile without AI data)
        # ============================================================
        profile_sql = f"""
INSERT INTO user_profiles (user_id, profession, company, location, bio, gender, phone, created_at, updated_at)
VALUES (
    '{user["id"]}',
    '{user.get("profession", "")}',
    '{user.get("company", "")}',
    '{user.get("location", "")}',
    '{user.get("bio", "")}',
    '{user.get("gender", "")}',
    '{user.get("phone", "")}',
    '{now.isoformat()}',
    '{now.isoformat()}'
) ON CONFLICT (user_id) DO UPDATE SET
    profession = EXCLUDED.profession,
    company = EXCLUDED.company,
    location = EXCLUDED.location,
    bio = EXCLUDED.bio,
    gender = EXCLUDED.gender,
    phone = EXCLUDED.phone,
    updated_at = EXCLUDED.updated_at;
"""
        sql_statements.append(profile_sql.strip())

    # ============================================================
    # CONVERSATIONS AND MESSAGES (Synchronized with system time)
    # ============================================================
    for c_idx, conv in enumerate(CONVERSATIONS):
        num_msgs = len(conv["messages"])
        last_message = conv["messages"][-1]["content"] if conv["messages"] else ""
        
        # Latest message is recent (10-30 minutes ago)
        last_message_time = now - timedelta(minutes=10 * (c_idx + 1))
        # First message started before
        created_at = last_message_time - timedelta(minutes=15 * max(num_msgs, 1))

        conv_sql = f"""
INSERT INTO direct_conversations (id, user_a_id, user_b_id, last_message_content, last_message_time, created_at, updated_at)
VALUES (
    '{conv["id"]}',
    '{conv["user_a_id"]}',
    '{conv["user_b_id"]}',
    '{last_message.replace("'", "''")}',
    '{last_message_time.isoformat()}',
    '{created_at.isoformat()}',
    '{last_message_time.isoformat()}'
) ON CONFLICT (id) DO NOTHING;
"""
        sql_statements.append(conv_sql.strip())

        # Conversation user states for both users
        for user_id in [conv["user_a_id"], conv["user_b_id"]]:
            state_sql = f"""
INSERT INTO conversation_user_state (id, conversation_id, user_id, is_archived, is_muted, updated_at)
VALUES (
    '{uuid.uuid4()}',
    '{conv["id"]}',
    '{user_id}',
    false,
    false,
    '{now.isoformat()}'
) ON CONFLICT (id) DO NOTHING;
"""
            sql_statements.append(state_sql.strip())

        # Messages: Chronologically spaced up to last_message_time
        for idx, msg in enumerate(conv["messages"]):
            msg_time = created_at + timedelta(minutes=15 * (idx + 1))

            msg_sql = f"""
INSERT INTO messages (id, conversation_id, sender_user_id, content, message_type, created_at)
VALUES (
    '{uuid.uuid4()}',
    '{conv["id"]}',
    '{msg["sender"]}',
    '{msg["content"].replace("'", "''")}',
    'text',
    '{msg_time.isoformat()}'
) ON CONFLICT (id) DO NOTHING;
"""
            sql_statements.append(msg_sql.strip())

    return "\n\n".join(sql_statements)


def seed_to_database():
    """Directly seed data into PostgreSQL/Database using SQLAlchemy with proper UTF-8 encoding"""
    from sqlalchemy import create_engine, text
    import sys
    import os

    # Attempt to import app config if available
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.config import get_settings
        db_url = get_settings().database_url
    except Exception:
        db_url = DATABASE_URL

    print(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    
    # Clean up existing messages & states for seeded conversations to ensure pure UTF-8 data
    conv_ids = [f"'{c['id']}'" for c in CONVERSATIONS]
    conv_ids_str = ", ".join(conv_ids)
    
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM messages WHERE conversation_id IN ({conv_ids_str});"))
        conn.execute(text(f"DELETE FROM conversation_user_state WHERE conversation_id IN ({conv_ids_str});"))
        conn.execute(text(f"DELETE FROM direct_conversations WHERE id IN ({conv_ids_str});"))
    
    sql = generate_sql()
    
    with engine.begin() as conn:
        for stmt in sql.split(";\n\n"):
            stmt_clean = stmt.strip()
            if stmt_clean:
                conn.execute(text(stmt_clean + ";"))
    print("✓ Successfully seeded users, profiles, conversations, and messages to database!")


def main():
    import sys
    if "--sql" in sys.argv:
        sql = generate_sql()
        print("-- ============================================================")
        print("-- SEED DATA - Users, Profiles, and Messages")
        print("-- Generated at:", datetime.utcnow().isoformat())
        print("-- ============================================================")
        print()
        print(sql)
        print()
        print("-- ============================================================")
        print("-- END OF SEED DATA")
        print("-- ============================================================")
    else:
        seed_to_database()


if __name__ == "__main__":
    main()
