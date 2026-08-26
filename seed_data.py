"""
Seed Data Script - Comprehensive Seed for MemoryChat
Seeds users, extended profiles, settings, conversations, messages, tags, AI configs, and connection requests.

Usage:
    python seed_data.py          # Wipe and re-seed database cleanly
    python seed_data.py --sql    # Print SQL dump
"""

import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/memorychat")

# Bcrypt hash for "password123"
PASSWORD_HASH = "$2b$12$PFyD4UbRbGseOFxCzuyg0e7RFkFegiZ34FipyrPku.2JSFiyozTQK"

# ============================================================
# 5 Users with realistic profiles and matchmaker metadata
# ============================================================
USERS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "minh.tran@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Trần Minh",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=minh",
        "gender": "male",
        "phone": "+84901234567",
        "profession": "Senior Backend Engineer",
        "company": "TechCorp Vietnam",
        "location": "Ho Chi Minh City",
        "bio": "Backend developer với hơn 5 năm kinh nghiệm. Đam mê thiết kế kiến trúc phân tán, Python, Go và ứng dụng AI Agent.",
        "skills": ["Python", "FastAPI", "Go", "Docker", "PostgreSQL", "System Architecture", "Redis"],
        "interests": ["Backend Development", "Cloud Computing", "AI Agents", "Open Source", "Microservices"],
        "looking_for": ["Machine Learning Engineer", "Frontend Developer", "Product Manager"],
        "offering": ["High Performance Backend", "API Design", "Database Optimization"],
        "github": "https://github.com/minhtran-tech",
        "linkedin": "https://linkedin.com/in/minhtran-engineer",
        "website": "https://minhtran.dev",
        "experience": [
            {"role": "Senior Backend Engineer", "company": "TechCorp Vietnam", "years": "2021 - Present", "description": "Thiết kế và tối ưu hệ thống microservices phục vụ 2M+ active users."},
            {"role": "Backend Developer", "company": "VNG Corporation", "years": "2019 - 2021", "description": "Phát triển các RESTful & gRPC APIs bằng Python & Go."}
        ],
        "education": [
            {"school": "Đại học Bách Khoa TP.HCM", "degree": "Kỹ sư Khoa học Máy tính", "year": "2015 - 2019"}
        ]
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "lan.nguyen@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Nguyễn Thị Lan",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=lan",
        "gender": "female",
        "phone": "+84987654321",
        "profession": "Lead Product Manager",
        "company": "StartupHub",
        "location": "Hanoi",
        "bio": "Product Manager đam mê giải quyết bài toán người dùng. Thích đọc sách về tư duy thiết kế và tối ưu trải nghiệm EdTech.",
        "skills": ["Product Management", "User Research", "Agile/Scrum", "Product Analytics", "Roadmapping"],
        "interests": ["EdTech", "SaaS Growth", "Design Thinking", "Startups", "AI Tools"],
        "looking_for": ["Backend Engineer", "Data Scientist", "UI/UX Designer"],
        "offering": ["Product Roadmap", "Market Strategy", "User Journey Mapping"],
        "github": None,
        "linkedin": "https://linkedin.com/in/lan-nguyen-pm",
        "website": None,
        "experience": [
            {"role": "Lead Product Manager", "company": "StartupHub", "years": "2022 - Present", "description": "Dẫn dắt đội ngũ phát triển nền tảng học tập thông minh EdTech."},
            {"role": "Product Owner", "company": "TopCV", "years": "2020 - 2022", "description": "Quản trị tính năng tuyển dụng và phân tích hành vi người dùng."}
        ],
        "education": [
            {"school": "Đại học Ngoại Thương Hà Nội", "degree": "Cử nhân Kinh tế Đối ngoại", "year": "2016 - 2020"}
        ]
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "khoa.pham@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Phạm Khoa",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=khoa",
        "gender": "male",
        "phone": "+84911223344",
        "profession": "AI & Data Scientist",
        "company": "AI Labs",
        "location": "Da Nang",
        "bio": "AI Engineer & Data Scientist tập trung vào NLP, RAG và Computer Vision. Luôn tìm kiếm giải pháp AI thực chiến cho doanh nghiệp.",
        "skills": ["Python", "PyTorch", "NLP", "LLMs", "LangChain", "Vector Search", "Qdrant"],
        "interests": ["Generative AI", "RAG Pipelines", "Computer Vision", "Deep Learning", "Automation"],
        "looking_for": ["DevOps Engineer", "Backend Developer", "Product Manager"],
        "offering": ["LLM Integration", "Semantic Search", "Model Fine-tuning"],
        "github": "https://github.com/khoapham-ai",
        "linkedin": "https://linkedin.com/in/khoapham-data",
        "website": "https://khoapham.ai",
        "experience": [
            {"role": "Senior AI Engineer", "company": "AI Labs", "years": "2021 - Present", "description": "Xây dựng các giải pháp Copilot, Semantic Search và Chatbot thông minh."},
            {"role": "Data Scientist", "company": "FPT Software", "years": "2019 - 2021", "description": "Phát triển mô hình OCR và phân loại dữ liệu lớn."}
        ],
        "education": [
            {"school": "Đại học Bách Khoa Đà Nẵng", "degree": "Kỹ sư Công nghệ Thông tin", "year": "2015 - 2019"}
        ]
    },
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "email": "mai.le@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Lê Mai",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=mai",
        "gender": "female",
        "phone": "+84955667788",
        "profession": "Lead UI/UX Designer",
        "company": "Design Studio",
        "location": "Ho Chi Minh City",
        "bio": "Designer đam mê tạo ra trải nghiệm người dùng tinh tế, chuẩn mực. Chuyên sâu về Design System và Gamification.",
        "skills": ["Figma", "UI Design", "Design Systems", "Prototyping", "User Testing", "Tailwind CSS"],
        "interests": ["Product Design", "Gamification", "Design Systems", "Frontend", "Typography"],
        "looking_for": ["Frontend Developer", "Product Manager", "Backend Engineer"],
        "offering": ["Mobile UI/UX", "Web Application Design", "Design Audit"],
        "github": "https://github.com/maile-design",
        "linkedin": "https://linkedin.com/in/maile-ux",
        "website": "https://maile.design",
        "experience": [
            {"role": "Lead UI/UX Designer", "company": "Design Studio", "years": "2021 - Present", "description": "Thiết kế bộ nhận diện và Design System cho các sản phẩm SaaS đa nền tảng."},
            {"role": "UI Designer", "company": "Garena", "years": "2019 - 2021", "description": "Thiết kế giao diện ứng dụng và game events."}
        ],
        "education": [
            {"school": "Đại học Kiến Trúc TP.HCM", "degree": "Cử nhân Thiết kế Đồ họa", "year": "2015 - 2019"}
        ]
    },
    {
        "id": "55555555-5555-5555-5555-555555555555",
        "email": "hieu.vo@example.com",
        "password_hash": PASSWORD_HASH,
        "full_name": "Võ Hiếu",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=hieu",
        "gender": "male",
        "phone": "+84999887766",
        "profession": "DevOps & Cloud Engineer",
        "company": "CloudFirst",
        "location": "Hanoi",
        "bio": "DevOps với niềm đam mê tự động hóa và hạ tầng đám mây tin cậy. Kinh nghiệm sâu rộng với Kubernetes, Docker và CI/CD.",
        "skills": ["Kubernetes", "Docker", "CI/CD", "AWS", "Terraform", "Linux", "Prometheus"],
        "interests": ["DevOps", "Site Reliability", "Cloud Infrastructure", "Security", "Monitoring"],
        "looking_for": ["Backend Engineer", "AI Engineer"],
        "offering": ["Cloud Architecture", "Kubernetes Deployment", "CI/CD Automation"],
        "github": "https://github.com/hieuvo-cloud",
        "linkedin": "https://linkedin.com/in/hieuvo-devops",
        "website": None,
        "experience": [
            {"role": "Lead DevOps Engineer", "company": "CloudFirst", "years": "2021 - Present", "description": "Quản trị cụm Kubernetes AWS EKS và tự động hóa pipeline GitHub Actions."},
            {"role": "System Administrator", "company": "Viettel IDC", "years": "2018 - 2021", "description": "Vận hành hệ thống trung tâm dữ liệu và giám sát hạ tầng."}
        ]
    },
]

# ============================================================
# Relationships & Conversations (Strictly user_a_id < user_b_id)
# ============================================================
CONVERSATIONS = [
    # 1. Minh (1) & Lan (2)
    {
        "id": "aaaa1111-1111-1111-1111-111111111111",
        "user_a_id": "11111111-1111-1111-1111-111111111111",
        "user_b_id": "22222222-2222-2222-2222-222222222222",
        "messages": [
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Chào Minh, rất vui được kết nối với bạn qua MemoryChat!"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Chào Lan! Mình cũng rất vui. Mình thấy bạn đang làm PM mảng EdTech tại StartupHub phải không?"},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Đúng rồi! Bên mình đang mở rộng tính năng AI gợi ý bài học cá nhân hóa. Bên bạn TechCorp có áp dụng nhiều AI Agent không?"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Có chứ! Mình vừa hoàn thiện hệ thống FastAPI + Vector Search với Qdrant để match profiles. Rất mượt mà và chính xác."},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Tuyệt quá! Cuối tuần này chúng mình cafe trao đổi thêm về mô hình hợp tác nhé?"},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Nhất trí! Hẹn bạn chiều Thứ 7 lúc 3h nha."},
        ],
    },
    # 2. Minh (1) & Khoa (3)
    {
        "id": "aaaa2222-2222-2222-2222-222222222222",
        "user_a_id": "11111111-1111-1111-1111-111111111111",
        "user_b_id": "33333333-3333-3333-3333-333333333333",
        "messages": [
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Hey Minh, thấy bạn làm backend phân tán. Mình đang cần tư vấn về kiến trúc phục vụ LLM serving."},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Chào Khoa! Rất sẵn lòng. Bạn đang dùng model gì và throughput dự kiến bao nhiêu?"},
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Mình đang chạy RAG pipeline với embedding đa chiều và LLM router cho copilot. Đang băn khoăn giữa Redis và Kafka để lưu context window."},
            {"sender": "11111111-1111-1111-1111-111111111111", "content": "Nếu cần truy xuất context realtime dưới 10ms thì Redis Cluster là tối ưu nhất. Kafka dùng khi cần log streaming và replay tin nhắn."},
            {"sender": "33333333-3333-3333-3333-333333333333", "content": "Cảm ơn Minh rất nhiều! Để mình benchmark thử trên cluster của bên mình."},
        ],
    },
    # 3. Lan (2) & Mai (4)
    {
        "id": "aaaa3333-3333-3333-3333-333333333333",
        "user_a_id": "22222222-2222-2222-2222-222222222222",
        "user_b_id": "44444444-4444-4444-4444-444444444444",
        "messages": [
            {"sender": "44444444-4444-4444-4444-444444444444", "content": "Chào Lan! Mình là Mai từ Design Studio. Mình thấy bạn đang tìm kiếm Designer cho dự án EdTech."},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Chào Mai! Đúng rồi, bên mình cần thiết kế giao diện game hóa (gamification) cho ứng dụng học tập."},
            {"sender": "44444444-4444-4444-4444-444444444444", "content": "Mình có portfolio chuyên về Gamification và Design Systems, mình vừa gửi qua email cho bạn tham khảo nhé!"},
            {"sender": "22222222-2222-2222-2222-222222222222", "content": "Portfolio đẹp và chỉn chu lắm Mai ơi. Sáng mai 10h mình setup buổi meeting online nhé!"},
        ],
    },
]

# ============================================================
# Pending Connection Requests (for testing Accept / Reject)
# ============================================================
CONNECTION_REQUESTS = [
    # Mai (4) sent friend request to Minh (1) -> PENDING (Minh can Accept or Reject)
    {
        "id": "bbbb1111-1111-1111-1111-111111111111",
        "sender_id": "44444444-4444-4444-4444-444444444444",
        "receiver_id": "11111111-1111-1111-1111-111111111111",
        "status": "PENDING",
    },
    # Minh (1) and Lan (2) -> ACCEPTED
    {
        "id": "bbbb2222-2222-2222-2222-222222222222",
        "sender_id": "11111111-1111-1111-1111-111111111111",
        "receiver_id": "22222222-2222-2222-2222-222222222222",
        "status": "ACCEPTED",
    },
    # Minh (1) and Khoa (3) -> ACCEPTED
    {
        "id": "bbbb3333-3333-3333-3333-333333333333",
        "sender_id": "33333333-3333-3333-3333-333333333333",
        "receiver_id": "11111111-1111-1111-1111-111111111111",
        "status": "ACCEPTED",
    },
    # Lan (2) and Mai (4) -> ACCEPTED
    {
        "id": "bbbb4444-4444-4444-4444-444444444444",
        "sender_id": "44444444-4444-4444-4444-444444444444",
        "receiver_id": "22222222-2222-2222-2222-222222222222",
        "status": "ACCEPTED",
    },
]

# ============================================================
# Tags
# ============================================================
DEFAULT_TAGS = [
    {"name": "Python", "category": "Tech"},
    {"name": "FastAPI", "category": "Tech"},
    {"name": "Go", "category": "Tech"},
    {"name": "Backend", "category": "Role"},
    {"name": "DevOps", "category": "Role"},
    {"name": "UI/UX", "category": "Role"},
    {"name": "Product", "category": "Role"},
    {"name": "AI/ML", "category": "Tech"},
    {"name": "Kubernetes", "category": "Tech"},
    {"name": "EdTech", "category": "Domain"},
]


def generate_sql():
    """Generate SQL statements for seeding"""
    now = datetime.now(timezone.utc)
    sql_statements = []

    # 1. USERS, PROFILES, SETTINGS, AI CONFIG
    for user in USERS:
        # Users
        u_sql = f"""
INSERT INTO users (id, email, password_hash, full_name, avatar, gender, phone, created_at, updated_at, is_ai)
VALUES (
    '{user["id"]}',
    '{user["email"]}',
    '{user["password_hash"]}',
    '{user["full_name"]}',
    '{user["avatar"]}',
    '{user["gender"]}',
    '{user["phone"]}',
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
        sql_statements.append(u_sql.strip())

        # Settings
        s_sql = f"""
INSERT INTO settings (
    user_id, auto_tag, auto_memory, theme, language, notification,
    ai_enabled, ai_read_profile, ai_extract_chat,
    sound_enabled, enter_is_send, read_receipts, online_status,
    media_auto_download, message_preview, accent_color, font_size,
    ai_memory_refresh_interval, ai_memory_window, ai_recommendation_interval, ai_copilot_context_turns
) VALUES (
    '{user["id"]}', true, true, 'system', 'vi', true,
    true, true, true,
    true, true, true, true,
    true, true, 'blue', 'medium',
    'realtime', 'unlimited', '24h', 10
) ON CONFLICT (user_id) DO UPDATE SET
    auto_tag = EXCLUDED.auto_tag,
    auto_memory = EXCLUDED.auto_memory,
    ai_extract_chat = EXCLUDED.ai_extract_chat,
    sound_enabled = EXCLUDED.sound_enabled,
    enter_is_send = EXCLUDED.enter_is_send,
    read_receipts = EXCLUDED.read_receipts,
    online_status = EXCLUDED.online_status,
    media_auto_download = EXCLUDED.media_auto_download,
    message_preview = EXCLUDED.message_preview,
    accent_color = EXCLUDED.accent_color,
    font_size = EXCLUDED.font_size;
"""
        sql_statements.append(s_sql.strip())

        # User Profiles
        skills_json = json.dumps(user.get("skills", [])).replace("'", "''")
        interests_json = json.dumps(user.get("interests", [])).replace("'", "''")
        looking_for_json = json.dumps(user.get("looking_for", [])).replace("'", "''")
        offering_json = json.dumps(user.get("offering", [])).replace("'", "''")
        experience_json = json.dumps(user.get("experience", [])).replace("'", "''")
        education_json = json.dumps(user.get("education", [])).replace("'", "''")
        bio_escaped = user.get("bio", "").replace("'", "''")
        github_val = f"'{user['github']}'" if user.get("github") else "NULL"
        linkedin_val = f"'{user['linkedin']}'" if user.get("linkedin") else "NULL"
        website_val = f"'{user['website']}'" if user.get("website") else "NULL"

        p_sql = f"""
INSERT INTO user_profiles (
    user_id, profession, company, location, bio, gender, phone,
    skills, interests, looking_for, offering, is_public,
    github, linkedin, website, experience, education,
    created_at, updated_at
) VALUES (
    '{user["id"]}',
    '{user.get("profession", "")}',
    '{user.get("company", "")}',
    '{user.get("location", "")}',
    '{bio_escaped}',
    '{user.get("gender", "")}',
    '{user.get("phone", "")}',
    '{skills_json}'::jsonb,
    '{interests_json}'::jsonb,
    '{looking_for_json}'::jsonb,
    '{offering_json}'::jsonb,
    true,
    {github_val},
    {linkedin_val},
    {website_val},
    '{experience_json}'::jsonb,
    '{education_json}'::jsonb,
    '{now.isoformat()}',
    '{now.isoformat()}'
) ON CONFLICT (user_id) DO UPDATE SET
    profession = EXCLUDED.profession,
    company = EXCLUDED.company,
    location = EXCLUDED.location,
    bio = EXCLUDED.bio,
    gender = EXCLUDED.gender,
    phone = EXCLUDED.phone,
    skills = EXCLUDED.skills,
    interests = EXCLUDED.interests,
    looking_for = EXCLUDED.looking_for,
    offering = EXCLUDED.offering,
    github = EXCLUDED.github,
    linkedin = EXCLUDED.linkedin,
    website = EXCLUDED.website,
    experience = EXCLUDED.experience,
    education = EXCLUDED.education,
    updated_at = EXCLUDED.updated_at;
"""
        sql_statements.append(p_sql.strip())

        # AI System Config
        ai_config_val = json.dumps({
            "features": {
                "tagging": True,
                "memory": True,
                "copilot": True,
                "reply_suggestions": True,
                "recommendation": True
            },
            "tag_whitelist": ["Python", "FastAPI", "Go", "Backend", "DevOps", "UI/UX", "Product", "AI/ML", "Kubernetes", "EdTech"],
            "max_tags_per_contact": 10,
            "min_matching_score": 0.5
        }).replace("'", "''")

        ai_cfg_sql = f"""
INSERT INTO ai_system_config (id, user_id, key, value, description, created_at, updated_at)
VALUES (
    '{uuid.uuid4()}',
    '{user["id"]}',
    'ai_settings',
    '{ai_config_val}'::json,
    'Default AI configurations',
    '{now.isoformat()}',
    '{now.isoformat()}'
) ON CONFLICT (user_id, key) DO UPDATE SET
    value = EXCLUDED.value,
    updated_at = EXCLUDED.updated_at;
"""
        sql_statements.append(ai_cfg_sql.strip())

        # Tags for each user
        for tag in DEFAULT_TAGS:
            tag_id = uuid.uuid4()
            tag_sql = f"""
INSERT INTO tags (id, user_id, name, category, is_active, created_at, updated_at)
VALUES ('{tag_id}', '{user["id"]}', '{tag["name"]}', '{tag["category"]}', true, '{now.isoformat()}', '{now.isoformat()}')
ON CONFLICT (user_id, name) DO NOTHING;
"""
            sql_statements.append(tag_sql.strip())

    # 2. CONVERSATIONS & MESSAGES
    for c_idx, conv in enumerate(CONVERSATIONS):
        # Enforce user_a_id < user_b_id
        uid_a, uid_b = sorted([conv["user_a_id"], conv["user_b_id"]])
        num_msgs = len(conv["messages"])
        last_message = conv["messages"][-1]["content"] if conv["messages"] else ""
        last_message_time = now - timedelta(minutes=10 * (c_idx + 1))
        created_at = last_message_time - timedelta(minutes=15 * max(num_msgs, 1))

        conv_sql = f"""
INSERT INTO direct_conversations (id, user_a_id, user_b_id, last_message_content, last_message_time, created_at, updated_at)
VALUES (
    '{conv["id"]}',
    '{uid_a}',
    '{uid_b}',
    '{last_message.replace("'", "''")}',
    '{last_message_time.isoformat()}',
    '{created_at.isoformat()}',
    '{last_message_time.isoformat()}'
) ON CONFLICT (id) DO UPDATE SET
    last_message_content = EXCLUDED.last_message_content,
    last_message_time = EXCLUDED.last_message_time,
    updated_at = EXCLUDED.updated_at;
"""
        sql_statements.append(conv_sql.strip())

        # Conversation user states
        for user_id in [uid_a, uid_b]:
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

        # Messages
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

    # 3. CONNECTION REQUESTS
    for req in CONNECTION_REQUESTS:
        req_sql = f"""
INSERT INTO connection_requests (id, sender_id, receiver_id, status, created_at, updated_at)
VALUES (
    '{req["id"]}',
    '{req["sender_id"]}',
    '{req["receiver_id"]}',
    '{req["status"]}',
    '{now.isoformat()}',
    '{now.isoformat()}'
) ON CONFLICT (id) DO UPDATE SET
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at;
"""
        sql_statements.append(req_sql.strip())

    # 4. NOTIFICATIONS
    user_map = {u["id"]: u for u in USERS}

    for req in CONNECTION_REQUESTS:
        if req["status"] == "PENDING":
            sender = user_map.get(req["sender_id"])
            if sender:
                notif_data_json = json.dumps({
                    "request_id": req["id"],
                    "sender_id": req["sender_id"],
                    "sender_name": sender["full_name"],
                    "sender_avatar": sender["avatar"],
                    "sender_profession": sender.get("profession"),
                    "sender_company": sender.get("company"),
                }).replace("'", "''")

                notif_sql = f"""
INSERT INTO notifications (id, user_id, type, title, content, data, status, created_at)
VALUES (
    '{uuid.uuid4()}',
    '{req["receiver_id"]}',
    'CONNECTION_REQUEST',
    'Lời mời kết bạn mới',
    '{sender["full_name"]} đã gửi cho bạn một lời mời kết bạn.',
    '{notif_data_json}'::json,
    'UNREAD',
    '{now.isoformat()}'
) ON CONFLICT (id) DO NOTHING;
"""
                sql_statements.append(notif_sql.strip())

    # Sample matching notification for User 1 (Minh Tran)
    target_user = USERS[3] # Mai Le
    match_data_json = json.dumps({
        "target_user_id": target_user["id"],
        "target_name": target_user["full_name"],
        "target_avatar": target_user["avatar"],
        "target_profession": target_user.get("profession"),
        "target_company": target_user.get("company"),
        "target_location": target_user.get("location"),
        "match_score": 92,
    }).replace("'", "''")

    match_notif_sql = f"""
INSERT INTO notifications (id, user_id, type, title, content, data, status, created_at)
VALUES (
    '{uuid.uuid4()}',
    '{USERS[0]["id"]}',
    'MATCH_SUGGESTION',
    'Gợi ý kết nối AI',
    'Profile của {target_user["full_name"]} rất phù hợp với bạn, hãy thử kết nối!',
    '{match_data_json}'::json,
    'UNREAD',
    '{(now - timedelta(hours=2)).isoformat()}'
) ON CONFLICT (id) DO NOTHING;
"""
    sql_statements.append(match_notif_sql.strip())

    return "\n\n".join(sql_statements)


def clean_and_seed_database():
    """Wipes all table data completely and seeds fresh consistent data"""
    from src.config import get_settings
    try:
        db_url = get_settings().database_url
    except Exception:
        db_url = DATABASE_URL

    print(f"Connecting to database: {db_url}", flush=True)
    engine = create_engine(db_url)

    # Terminate stale idle connections
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE pid <> pg_backend_pid() 
                  AND datname = current_database()
                  AND state IN ('idle', 'idle in transaction');
            """))
    except Exception:
        pass

    # 1. Delete all records from tables in foreign-key safe order
    tables_to_clean = [
        "message_reactions",
        "messages",
        "conversation_user_state",
        "assistant_memories",
        "contact_memories",
        "contacts",
        "direct_conversations",
        "connection_requests",
        "recommendations",
        "user_tags",
        "tags",
        "ai_system_config",
        "search_history",
        "notifications",
        "event_logs",
        "user_blocks",
        "user_profiles",
        "settings",
        "users",
    ]

    print("Cleaning all existing database tables...", flush=True)
    with engine.begin() as conn:
        for tbl in tables_to_clean:
            try:
                conn.execute(text(f"DELETE FROM {tbl};"))
            except Exception as e:
                print(f"Notice cleaning {tbl}: {e}", flush=True)

    print("✓ Successfully cleaned database tables.", flush=True)

    # 2. Seed fresh data
    print("Seeding fresh data...", flush=True)
    sql = generate_sql()

    with engine.begin() as conn:
        for stmt in sql.split(";\n\n"):
            stmt_clean = stmt.strip()
            if stmt_clean:
                conn.execute(text(stmt_clean + ";"))

    print("✓ Successfully seeded Users, Profiles, Settings, AI Configs, Tags, Conversations, Messages, and Connection Requests!", flush=True)


def main():
    if "--sql" in sys.argv:
        sql = generate_sql()
        print("-- ============================================================")
        print("-- SEED DATA - Comprehensive Schema")
        print("-- Generated at:", datetime.now(timezone.utc).isoformat())
        print("-- ============================================================")
        print()
        print(sql)
        print()
        print("-- ============================================================")
        print("-- END OF SEED DATA")
        print("-- ============================================================")
    else:
        clean_and_seed_database()


if __name__ == "__main__":
    main()
