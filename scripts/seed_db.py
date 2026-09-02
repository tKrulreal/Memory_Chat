import sys
import os
import uuid
import logging
import subprocess
from datetime import datetime, timezone, timedelta

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session
from src.models.database import Base, SessionLocal, engine
from src.models.user import User, UserProfile, Setting, UserBlock, Notification, SearchHistory
from src.models.chat import Conversation, ConversationUserState, Message, MessageReaction
from src.models.contact import Contact, ContactMemory
from src.models.connection import ConnectionRequest
from src.models.tag import Tag, UserTag, AISystemConfig
from src.models.ai import AssistantMemory, Recommendation, EventLog, OutboxEvent, CopilotMessage
from src.core.security import get_password_hash
from src.schemas.enums import MessageRole

def seed_db():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger.info("Applying database migrations...")
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=project_root,
            check=True,
        )
    except subprocess.CalledProcessError:
        if not str(engine.url).startswith("sqlite"):
            raise
        # This script is destructive by design. Recreate an old local SQLite
        # schema instead of trying to seed tables with missing columns.
        logger.warning("Alembic could not upgrade the local SQLite schema; creating missing tables from models.")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        logger.info("Starting database seed with 15 test users...")
        
        # 1. Clear existing data in dependency order
        logger.info("Clearing existing data...")
        db.query(MessageReaction).delete()
        db.query(Message).delete()
        db.query(ConversationUserState).delete()
        db.query(Conversation).delete()
        db.query(ConnectionRequest).delete()
        db.query(ContactMemory).delete()
        db.query(Contact).delete()
        db.query(UserProfile).delete()
        db.query(Setting).delete()
        db.query(SearchHistory).delete()
        db.query(Notification).delete()
        db.query(UserBlock).delete()
        db.query(UserTag).delete()
        db.query(Tag).delete()
        db.query(AISystemConfig).delete()
        db.query(AssistantMemory).delete()
        db.query(Recommendation).delete()
        db.query(EventLog).delete()
        db.query(OutboxEvent).delete()
        db.query(CopilotMessage).delete()
        db.query(User).delete()
        db.commit()
        logger.info("All existing tables cleared.")

        # 2. Define 15 users details
        user_data = [
            {
                "email": "user1@example.com",
                "password": "password123",
                "full_name": "Nguyễn Văn Một",
                "gender": "Male",
                "phone": "0911111111",
                "profile": {
                    "profession": "Product Manager",
                    "company": "Google",
                    "location": "Hà Nội",
                    "skills": ["Product Strategy", "UX Design", "Roadmapping", "NLP", "Generative AI", "AI Product Management"],
                    "interests": ["AI", "Startups", "Books", "Generative AI", "Robotics", "AI Ethics"],
                    "looking_for": ["AI Researchers to collaborate on NLP projects", "AI Model Deployment partner", "VinAI collaborations"],
                    "offering": ["Product Management expertise for AI startups", "UX Strategy", "AI Product Roadmapping"],
                    "bio": "Tôi là PM thích kết nối lập trình viên và thiết kế.",
                    "is_public": True
                }
            },
            {
                "email": "user2@example.com",
                "password": "password123",
                "full_name": "Trần Thị Hai",
                "gender": "Female",
                "phone": "0922222222",
                "profile": {
                    "profession": "Backend Developer",
                    "company": "VNG",
                    "location": "Hà Nội",
                    "skills": ["Python", "FastAPI", "PostgreSQL"],
                    "interests": ["Machine Learning", "Hiking"],
                    "looking_for": ["Project collaboration"],
                    "offering": ["Backend expertise"],
                    "bio": "Lập trình viên backend thích viết code sạch.",
                    "is_public": True
                }
            },
            {
                "email": "user3@example.com",
                "password": "password123",
                "full_name": "Lê Văn Ba",
                "gender": "Male",
                "phone": "0933333333",
                "profile": {
                    "profession": "Frontend Developer",
                    "company": "FPT",
                    "location": "TP. HCM",
                    "skills": ["React", "TypeScript", "TailwindCSS"],
                    "interests": ["UI/UX", "Music"],
                    "looking_for": ["Mentorship", "Side projects"],
                    "offering": ["Frontend development"],
                    "bio": "Đam mê thiết kế giao diện đẹp và tối ưu.",
                    "is_public": True
                }
            },
            {
                "email": "user4@example.com",
                "password": "password123",
                "full_name": "Phạm Thị Bốn",
                "gender": "Female",
                "phone": "0944444444",
                "profile": {
                    "profession": "AI Researcher",
                    "company": "VinAI",
                    "location": "Hà Nội",
                    "skills": ["PyTorch", "NLP", "Deep Learning", "Transformers", "Generative AI"],
                    "interests": ["Generative AI", "Robotics", "Chess", "AI Ethics"],
                    "looking_for": ["Product Managers with UX experience to build AI product roadmap", "AI Product Roadmapping support"],
                    "offering": ["AI model training", "NLP expertise", "Generative AI model development"],
                    "bio": "Đang làm nghiên cứu về NLP và cần đối tác triển khai DevOps.",
                    "is_public": True
                }
            },
            {
                "email": "user5@example.com",
                "password": "password123",
                "full_name": "Hoàng Văn Năm",
                "gender": "Male",
                "phone": "0955555555",
                "profile": {
                    "profession": "DevOps Engineer",
                    "company": "Viettel",
                    "location": "Hà Nội",
                    "skills": ["Docker", "Kubernetes", "DevOps", "CI/CD", "AWS"],
                    "interests": ["System architecture", "Cloud", "Generative AI"],
                    "looking_for": ["AI researchers looking to deploy production models"],
                    "offering": ["Dockerization", "Cloud deployment pipelines", "Kubernetes scaling"],
                    "bio": "Kỹ sư DevOps đam mê tối ưu hóa hạ tầng cho AI.",
                    "is_public": True
                }
            },
            {
                "email": "user6@example.com",
                "password": "password123",
                "full_name": "Đỗ Hoàng Sáu",
                "gender": "Male",
                "phone": "0966666666",
                "profile": {
                    "profession": "Mobile Developer",
                    "company": "Techcombank",
                    "location": "Hà Nội",
                    "skills": ["Swift", "iOS", "Flutter", "CocoaPods"],
                    "interests": ["Mobile Apps", "Traveling", "Biking"],
                    "looking_for": ["UI/UX Designers for side project", "Backend APIs"],
                    "offering": ["iOS App development", "Flutter cross-platform tips"],
                    "bio": "Lập trình viên di động muốn đưa app chat AI lên iOS.",
                    "is_public": True
                }
            },
            {
                "email": "user7@example.com",
                "password": "password123",
                "full_name": "Bùi Quang Bảy",
                "gender": "Male",
                "phone": "0977777777",
                "profile": {
                    "profession": "UI/UX Designer",
                    "company": "Be Group",
                    "location": "TP. HCM",
                    "skills": ["Figma", "Design Systems", "Prototyping", "User Research"],
                    "interests": ["Art", "Photography", "Tech Gadgets"],
                    "looking_for": ["Mobile Developers", "Product managers for collaboration"],
                    "offering": ["Mockups, UX advice", "Interactive prototypes"],
                    "bio": "Designer đam mê tạo trải nghiệm người dùng mượt mà.",
                    "is_public": True
                }
            },
            {
                "email": "user8@example.com",
                "password": "password123",
                "full_name": "Ngô Văn Tám",
                "gender": "Male",
                "phone": "0988888888",
                "profile": {
                    "profession": "Data Analyst",
                    "company": "Shopee",
                    "location": "TP. HCM",
                    "skills": ["SQL", "Python", "Tableau", "PowerBI"],
                    "interests": ["Data Science", "E-commerce", "Football"],
                    "looking_for": ["Machine Learning mentors", "Data engineers"],
                    "offering": ["Data clean up, SQL queries tuning", "Dashboard building"],
                    "bio": "Chuyên viên phân tích dữ liệu muốn lấn sân sang ML/AI.",
                    "is_public": True
                }
            },
            {
                "email": "user9@example.com",
                "password": "password123",
                "full_name": "Nguyễn Thị Chín",
                "gender": "Female",
                "phone": "0999999999",
                "profile": {
                    "profession": "QA/Tester",
                    "company": "KMS Technology",
                    "location": "Đà Nẵng",
                    "skills": ["Selenium", "Jira", "Postman", "Automation Testing"],
                    "interests": ["Software Quality", "Yoga", "Baking"],
                    "looking_for": ["Open source projects to test", "Automation testing tips"],
                    "offering": ["Writing test cases", "Bug reporting", "API testing"],
                    "bio": "Kỹ sư kiểm thử phần mềm thích tìm bug.",
                    "is_public": True
                }
            },
            {
                "email": "user10@example.com",
                "password": "password123",
                "full_name": "Vũ Đức Mười",
                "gender": "Male",
                "phone": "0910101010",
                "profile": {
                    "profession": "Business Analyst",
                    "company": "VNPay",
                    "location": "Hà Nội",
                    "skills": ["Requirements Gathering", "UML", "PRD writing", "Agile"],
                    "interests": ["Fintech", "Payment Gateways", "Chess"],
                    "looking_for": ["Product Managers to network", "Tech leads"],
                    "offering": ["Business analysis documentation", "Fintech domain knowledge"],
                    "bio": "BA Fintech thích tối ưu hóa luồng nghiệp vụ.",
                    "is_public": True
                }
            },
            {
                "email": "user11@example.com",
                "password": "password123",
                "full_name": "Phạm Văn Mười Một",
                "gender": "Male",
                "phone": "0911111122",
                "profile": {
                    "profession": "Cloud Architect",
                    "company": "AWS Vietnam",
                    "location": "Hà Nội",
                    "skills": ["AWS", "Terraform", "Cloud Migration", "Cost Optimization"],
                    "interests": ["Cloud Native", "Serverless", "Running"],
                    "looking_for": ["Startups needing cloud advice", "DevOps engineers"],
                    "offering": ["AWS architecture review", "Infrastructure as Code tips"],
                    "bio": "Kiến trúc sư đám mây chuyên tối ưu hóa hệ thống lớn.",
                    "is_public": True
                }
            },
            {
                "email": "user12@example.com",
                "password": "password123",
                "full_name": "Trần Thị Mười Hai",
                "gender": "Female",
                "phone": "0912121212",
                "profile": {
                    "profession": "HR Manager",
                    "company": "VNG",
                    "location": "TP. HCM",
                    "skills": ["Talent Acquisition", "Technical Recruiting", "Employer Branding"],
                    "interests": ["HR Tech", "Psychology", "Cooking"],
                    "looking_for": ["Tech leads/Managers for hiring insights", "HR specialists"],
                    "offering": ["CV review", "Interview coaching", "Tech market trends"],
                    "bio": "HR đam mê tuyển dụng nhân tài công nghệ.",
                    "is_public": True
                }
            },
            {
                "email": "user13@example.com",
                "password": "password123",
                "full_name": "Lê Văn Mười Ba",
                "gender": "Male",
                "phone": "0913131313",
                "profile": {
                    "profession": "Cybersecurity Specialist",
                    "company": "Viettel Cyber Security",
                    "location": "Hà Nội",
                    "skills": ["Penetration Testing", "OWASP", "Code Auditing", "Cryptography"],
                    "interests": ["Ethical Hacking", "CTF", "Gaming"],
                    "looking_for": ["Developers interested in secure coding", "System admins"],
                    "offering": ["Vulnerability assessment", "Secure code reviews"],
                    "bio": "Chuyên gia bảo mật thích hack và bảo vệ hệ thống.",
                    "is_public": True
                }
            },
            {
                "email": "user14@example.com",
                "password": "password123",
                "full_name": "Hoàng Thị Mười Bốn",
                "gender": "Female",
                "phone": "0914141414",
                "profile": {
                    "profession": "Marketing Specialist",
                    "company": "Freelance",
                    "location": "Đà Nẵng",
                    "skills": ["Content Marketing", "SEO Strategy", "Social Media", "Google Analytics"],
                    "interests": ["Digital Marketing", "Traveling", "Writing"],
                    "looking_for": ["Web developers to build blog", "Graphic designers"],
                    "offering": ["SEO audit", "Content strategy formulation"],
                    "bio": "Chuyên viên Marketing tự do đam mê SEO và content sáng tạo.",
                    "is_public": True
                }
            },
            {
                "email": "user15@example.com",
                "password": "password123",
                "full_name": "Nguyễn Văn Mười Lăm",
                "gender": "Male",
                "phone": "0915151515",
                "profile": {
                    "profession": "Golang Developer",
                    "company": "FPT Software",
                    "location": "Hà Nội",
                    "skills": ["Golang", "gRPC", "Redis", "Microservices"],
                    "interests": ["High Performance Systems", "Concurrency", "Algorithms"],
                    "looking_for": ["Large scale microservice projects", "Backend developers"],
                    "offering": ["Golang concurrency optimization", "API performance tuning"],
                    "bio": "Lập trình viên Go đam mê tối ưu hóa hệ thống chịu tải cao.",
                    "is_public": True
                }
            }
        ]

        # 3. Create Users, Profiles, and Settings
        created_users = []
        for ud in user_data:
            user = User(
                id=uuid.uuid4(),
                email=ud["email"],
                password_hash=get_password_hash(ud["password"]),
                full_name=ud["full_name"],
                gender=ud["gender"],
                phone=ud["phone"],
                is_ai=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create setting
            setting = Setting(
                user_id=user.id,
                ai_enabled=True,
                ai_read_profile=True,
                ai_extract_chat=True,
                notification=True
            )
            db.add(setting)
            
            # Create profile
            prof_data = ud["profile"]
            profile = UserProfile(
                user_id=user.id,
                profession=prof_data["profession"],
                company=prof_data["company"],
                location=prof_data["location"],
                skills=prof_data["skills"],
                interests=prof_data["interests"],
                looking_for=prof_data["looking_for"],
                offering=prof_data["offering"],
                bio=prof_data["bio"],
                is_public=prof_data["is_public"]
            )
            db.add(profile)

            # Create AI System Config
            ai_config_val = {
                "features": {
                    "copilot": True,
                    "chat_copilot": True,
                    "recommendation": True,
                    "memory": True,
                    "tagging": True,
                    "reply_suggestions": True,
                },
                "chat_copilot_context_mode": "scoped_chat",
                "chat_copilot_message_limit": 20,
                "chat_copilot_quick_actions": True,
                "model_name": "gpt-4o-mini",
                "temperature": 0.7,
                "tag_limit": 3,
                "min_matching_score": 50,
                "notification_interval": "24h",
            }
            ai_cfg = AISystemConfig(
                id=uuid.uuid4(),
                user_id=user.id,
                key="ai_settings",
                value=ai_config_val,
                description="Default AI configurations",
            )
            db.add(ai_cfg)

            # Create Default Tags
            for tag_name, tag_cat in [("Developer", "profession"), ("AI & Data", "skill"), ("Startup & Founder", "interest"), ("Product Manager", "profession")]:
                tag = Tag(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    name=tag_name,
                    category=tag_cat,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(tag)

            db.commit()
            db.refresh(user)
            created_users.append(user)
            logger.info(f"Created user: {user.email}")
        
        logger.info(f"Seeded {len(created_users)} users with profiles, AI configs, and tags.")

        # 4. Create Direct Conversations & Messages for User 1 (Nguyễn Văn Một)
        u1 = created_users[0]
        
        targets = [
            (created_users[1], "Trần Thị Hai", [
                "Chào Hai, mình đang lên kế hoạch xây dựng ứng dụng AI Chat thế hệ mới.",
                "Chào Một, dự án nghe hấp dẫn đấy! Bạn dự định dùng stack công nghệ nào?",
                "Mình định dùng FastAPI + Next.js 15 và PostgreSQL với Qdrant vector DB.",
                "Stack này rất tối ưu cho real-time và RAG. Khi nào bạn bắt đầu triển khai kiến trúc?"
            ]),
            (created_users[2], "Lê Văn Ba", [
                "Chào Ba, bạn có kinh nghiệm tối ưu hiệu năng React/Next.js không?",
                "Chào bạn. Mình thường dùng React Query và tối ưu re-render qua Zustand.",
                "Tuyệt vời, dự án chat của mình đang cần một frontend lead có kinh nghiệm như bạn.",
                "Rất sẵn lòng hợp tác, gửi mình xem qua wireframe nhé!"
            ]),
            (created_users[4], "Hoàng Văn Năm", [
                "Chào Năm, bạn đã từng deploy mô hình LLM trên Kubernetes chưa?",
                "Chào Một, mình từng dựng cluster K8s với vLLM và GPU orchestration rồi.",
                "Hay quá, lúc nào rảnh mình trao đổi kỹ hơn về infra cho AI agents nhé.",
                "OK bạn, cứ ping mình bất cứ lúc nào."
            ]),
            (created_users[5], "Đỗ Hoàng Sáu", [
                "Chào Sáu, hiện tại bên bạn có nhận dự án outsource app mobile Flutter không?",
                "Chào Một. Bên mình có team 5 devs Flutter sẵn sàng onboard trong tháng tới.",
                "Để mình gửi tài liệu specs và yêu cầu tính năng qua email nhé.",
                "Đã nhận thông tin, team mình sẽ ước lượng timeline và báo lại bạn sớm."
            ]),
            (created_users[9], "Vũ Đức Mười", [
                "Chào Mười, bạn có kinh nghiệm phân tích nghiệp vụ các hệ thống chat không?",
                "Chào anh Một. Trước đây em từng viết PRD cho hệ thống tin nhắn nội bộ của doanh nghiệp rồi ạ.",
                "Thế thì tốt quá. Hôm nào rảnh anh em mình cafe bàn về tính năng workspace cho AI Chat nhé.",
                "Dạ vâng, chiều thứ 5 tuần này em rảnh, anh em mình hẹn ở Duy Tân nhé."
            ]),
            (created_users[10], "Phạm Văn Mười Một", [
                "Chào anh Mười Một, em đang gặp vấn đề tối ưu chi phí lưu trữ PostgreSQL trên AWS.",
                "Chào Một. Em đang dùng RDS hay chạy trên EC2? Có partition bảng chưa?",
                "Em đang dùng RDS Postgresql và lượng tin nhắn chat tăng nhanh quá.",
                "Để anh xem thử cấu hình và mức độ truy vấn rồi tư vấn giải pháp lưu trữ lạnh nhé."
            ])
        ]
        
        seeded_convs = []
        for idx, (target_user, target_name, msgs) in enumerate(targets):
            ua_id, ub_id = sorted([u1.id, target_user.id])
            conv = Conversation(
                id=uuid.uuid4(),
                user_a_id=ua_id,
                user_b_id=ub_id,
                type="P2P",
                last_message_content=msgs[-1],
                last_message_time=datetime.now(timezone.utc) - timedelta(hours=idx)
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)
            seeded_convs.append(conv)
            
            db.add(ConversationUserState(id=uuid.uuid4(), conversation_id=conv.id, user_id=u1.id))
            db.add(ConversationUserState(id=uuid.uuid4(), conversation_id=conv.id, user_id=target_user.id))
            
            base_time = datetime.now(timezone.utc) - timedelta(hours=idx, minutes=len(msgs)*5)
            for m_idx, content in enumerate(msgs):
                # Alternate sender between User 1 and Target User
                sender_id = u1.id if m_idx % 2 == 0 else target_user.id
                msg = Message(
                    id=uuid.uuid4(),
                    conversation_id=conv.id,
                    sender_user_id=sender_id,
                    content=content,
                    message_type="TEXT",
                    created_at=base_time + timedelta(minutes=m_idx * 5)
                )
                db.add(msg)
            
        db.commit()
        logger.info("Seeded 6 conversations and messages for User 1 successfully.")

        # 5. Seed Copilot Messages for User 1 (both Global Copilot & In-Chat Copilot)
        # Global Copilot Messages (conversation_id = None)
        global_copilot_msgs = [
            ("user", "Chào bạn, hãy tóm tắt các cuộc trò chuyện gần đây của tôi?", [], []),
            ("assistant", "Chào bạn! Gần đây bạn đã trao đổi với Trần Thị Hai về việc thiết kế API Backend cho dự án AI Chat, trao đổi với Lê Văn Ba về giao diện React/TailwindCSS, và bàn bạc với Đỗ Hoàng Sáu về dự án app di động iOS.", [], ["messages"]),
            ("user", "Trong mạng lưới của tôi có ai có kinh nghiệm về DevOps không?", [], []),
            ("assistant", "Trong mạng lưới của bạn có Hoàng Văn Năm (DevOps Engineer tại Viettel chuyên Docker/K8s) và Phạm Văn Mười Một (Cloud Architect chuyên AWS/Terraform). Bạn có thể kết nối với họ để nhận tư vấn hạ tầng.", [], ["contacts", "user_profile"]),
        ]
        for c_idx, (c_role, c_content, c_tools, c_sources) in enumerate(global_copilot_msgs):
            c_msg = CopilotMessage(
                id=uuid.uuid4(),
                user_id=u1.id,
                conversation_id=None,
                role=c_role,
                content=c_content,
                tools_used=c_tools,
                sources=c_sources,
                created_at=datetime.now(timezone.utc) - timedelta(minutes=30 - c_idx * 5),
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=30 - c_idx * 5),
            )
            db.add(c_msg)
        db.commit()

        # In-Chat Copilot Messages for Conversation with Trần Thị Hai (conversation_id = seeded_convs[0].id)
        first_conv = seeded_convs[0]
        in_chat_msgs = [
            ("user", "Tóm tắt giúp tôi những gì tôi và Trần Thị Hai đã trao đổi?", ["get_recent_messages"]),
            ("assistant", "Trong cuộc trò chuyện này, bạn và Trần Thị Hai đã thảo luận về việc xây dựng ứng dụng AI Chat thế hệ mới sử dụng FastAPI, Next.js 15, PostgreSQL và Qdrant vector DB cho kiến trúc RAG real-time. Hai đã đánh giá stack này rất tối ưu và đang chờ bạn bắt đầu triển khai kiến trúc.", ["get_recent_messages", "get_peer_info"]),
        ]
        for ic_idx, (ic_role, ic_content, ic_tools) in enumerate(in_chat_msgs):
            ic_msg = CopilotMessage(
                id=uuid.uuid4(),
                user_id=u1.id,
                conversation_id=first_conv.id,
                role=ic_role,
                content=ic_content,
                tools_used=ic_tools,
                sources=["conversation_messages"],
                intent="SEARCH" if ic_role == "assistant" else None,
                created_at=datetime.now(timezone.utc) - timedelta(minutes=15 - ic_idx * 5),
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=15 - ic_idx * 5),
            )
            db.add(ic_msg)

        db.commit()
        logger.info("Seeded Global & In-Chat Copilot messages history for User 1.")

        # 6. Seed AI Matchmaker Recommendation & Synchronized Notification for User 1 matching User 4 (Phạm Thị Bốn)
        u4 = created_users[3] # Phạm Thị Bốn - AI Researcher at VinAI
        rec_id = uuid.uuid4()
        rec = Recommendation(
            id=rec_id,
            owner_user_id=u1.id,
            target_user_id=u4.id,
            type="CONNECTION",
            status="PENDING",
            reason=f"Profile của {u4.full_name} có sự tương đồng cao về định hướng phát triển sản phẩm AI và nghiên cứu NLP/Generative AI.",
            match_score=0.92,
            priority="HIGH",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            updated_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db.add(rec)

        notif = Notification(
            id=uuid.uuid4(),
            user_id=u1.id,
            type="MATCH_SUGGESTION",
            title="Gợi ý kết nối AI",
            content=f"Profile của {u4.full_name} rất phù hợp với bạn, hãy thử kết nối!",
            data={
                "target_user_id": str(u4.id),
                "target_name": u4.full_name,
                "target_avatar": None,
                "target_profession": "AI Researcher",
                "target_company": "VinAI",
                "target_location": "Hà Nội",
                "match_score": 92,
                "recommendation_id": str(rec_id),
            },
            status="UNREAD",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db.add(notif)
        db.commit()
        logger.info("Seeded synchronized AI Matchmaker recommendation and notification for User 1.")
        logger.info("Database seeding successfully completed!")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
