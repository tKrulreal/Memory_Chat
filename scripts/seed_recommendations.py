#!/usr/bin/env python3
"""
Seed realistic Real Users, Assistant Memories, and Real User-to-User Recommendations.

Usage:
    .venv/Scripts/python scripts/seed_recommendations.py
"""

import argparse
import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone


# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from src.models.database import SessionLocal
from src.models.user import User
from src.models.ai import AssistantMemory, Recommendation
from src.models.chat import Conversation, ConversationUserState, Message
from src.core.security import get_password_hash
from src.agents.connection.agent import ConnectionRecommendationAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed_recommendations")

VN_TZ = timezone(timedelta(hours=7))

# 8 Real User Profiles with distinct professions, skills, and needs
REAL_USERS_DATA = [
    {
        "email": "user1@gmail.com",
        "full_name": "Nguyễn Hoàng Long",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=NguyenHoangLong",
        "profession": "Tech Product Lead",
        "company": "NextGen Innovation",
        "location": "Hà Nội",
        "summary": "Product Lead tại NextGen Innovation, đang tìm kiếm các giải pháp tích hợp AI và mở rộng mạng lưới đối tác công nghệ và tuyển dụng kỹ sư.",
        "skills": ["Product Management", "AI Strategy", "Agile", "Business Analysis", "Python"],
        "interests": ["Generative AI", "EdTech", "Startups", "Mobile Apps"],
        "current_needs": [
            "Tìm Senior AI Engineer để tư vấn giải pháp RAG và AI Agent",
            "Tìm đối tác phát triển ứng dụng di động Flutter/React Native",
            "Học hỏi kinh nghiệm tối ưu hóa logistics và vận hành E-commerce"
        ],
        "current_offers": [
            "Tư vấn phát triển sản phẩm công nghệ (Product Discovery & Delivery)",
            "Kết nối các quỹ đầu tư thiên thần và mạng lưới khởi nghiệp",
            "Chia sẻ kinh nghiệm quản lý đội ngũ kỹ thuật Agile"
        ],
    },
    {
        "email": "nam.le@edutech.vn",
        "full_name": "Lê Hoàng Nam",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=LeHoangNam",
        "profession": "Startup Founder & CEO",
        "company": "EduTech Labs",
        "location": "Hà Nội",
        "summary": "Founder & CEO tại EduTech Labs, 32 tuổi. Đang phát triển hệ thống gia sư AI cá nhân hoá cho học sinh cấp 3. Cần tìm nhân sự AI chất lượng cao.",
        "skills": ["EdTech", "Product Strategy", "Fundraising", "Business Development"],
        "interests": ["GenAI in Education", "Startups", "Venture Capital"],
        "current_needs": [
            "Tuyển Senior AI Engineer xây dựng AI Tutor và hệ thống RAG",
            "Tìm mentor có kinh nghiệm scale mô hình LLM chi phí tối ưu",
            "Mở rộng mạng lưới trường học đối tác"
        ],
        "current_offers": [
            "Vốn đầu tư hạt giống và cổ phần (Equity) cho Co-founder",
            "Kinh nghiệm gọi vốn Pre-Series A và kết nối quỹ đầu tư",
            "Mạng lưới hơn 50 trường học đối tác tại Hà Nội"
        ],
    },
    {
        "email": "quan.tran@vinai.io",
        "full_name": "Trần Minh Quân",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=TranMinhQuan",
        "profession": "Senior AI / LLM Engineer",
        "company": "VinAI Research",
        "location": "Hà Nội",
        "summary": "Senior AI Engineer tại VinAI Research, 29 tuổi. Chuyên gia về NLP, LLM Fine-tuning và RAG architecture.",
        "skills": ["Python", "PyTorch", "LLM Fine-tuning", "RAG Architecture", "FastAPI", "Computer Vision"],
        "interests": ["AI", "Startup", "Computer Vision", "Open Source AI"],
        "current_needs": [
            "Tìm dự án Startup AI thực tế để làm Technical Advisor / Co-founder ngoài giờ",
            "Học hỏi thêm về mô hình kinh doanh và chiến lược sản phẩm EdTech"
        ],
        "current_offers": [
            "Tư vấn kiến trúc hệ thống RAG và Agentic AI cấp production",
            "Tối ưu chi phí inference và huấn luyện mô hình ngôn ngữ lớn",
            "Kinh nghiệm triển khai pipeline MLOps thực chiến"
        ],
    },
    {
        "email": "thao.nguyen@globalbrands.vn",
        "full_name": "Nguyễn Phương Thảo",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=NguyenPhuongThao",
        "profession": "E-commerce Operations Manager",
        "company": "GlobalBrands Vietnam",
        "location": "TP. Hồ Chí Minh",
        "summary": "Quản lý vận hành E-commerce xuất khẩu đi Mỹ & EU trên Amazon FBA và TikTok Shop US.",
        "skills": ["E-commerce Operations", "Amazon FBA", "Shopify", "Digital Marketing"],
        "interests": ["Cross-border Trade", "Supply Chain Tech", "TikTok Shop Global"],
        "current_needs": [
            "Tìm đối tác Logistics xuất khẩu đi Mỹ và EU với giá cước cạnh tranh",
            "Tư vấn thủ tục hải quan và giải pháp kho bãi fulfillment bờ Tây nước Mỹ"
        ],
        "current_offers": [
            "Kinh nghiệm tối ưu chuyển đổi và chạy quảng cáo Amazon/TikTok Shop",
            "Mạng lưới xưởng sản xuất thủ công mỹ nghệ xuất khẩu chất lượng cao"
        ],
    },
    {
        "email": "ducanh.pham@fastcargo.vn",
        "full_name": "Phạm Đức Anh",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=PhamDucAnh",
        "profession": "Head of Business Development",
        "company": "FastCargo Logistics",
        "location": "TP. Hồ Chí Minh",
        "summary": "Trưởng phòng BD tại FastCargo Logistics, hơn 8 năm trong ngành vận tải quốc tế và kho bãi fulfillment.",
        "skills": ["Freight Forwarding", "Cross-border Fulfillment", "Customs Clearance", "Warehousing"],
        "interests": ["Global Trade", "Logistics Tech", "Supply Chain Optimization"],
        "current_needs": [
            "Mở rộng tệp khách hàng doanh nghiệp D2C và seller E-commerce xuất khẩu đi US/EU",
            "Tìm đối tác công nghệ để tích hợp API tự động hóa đơn vận chuyển"
        ],
        "current_offers": [
            "Dịch vụ vận chuyển Door-to-Door đi US/EU trọn gói bao thuế",
            "Hệ thống kho ngoại quan và fulfillment center tại California và Texas"
        ],
    },
    {
        "email": "chi.dang@studiominimal.io",
        "full_name": "Đặng Quỳnh Chi",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=DangQuynhChi",
        "profession": "Lead Product Designer",
        "company": "Studio Minimal",
        "location": "Đà Nẵng",
        "summary": "Lead UI/UX Designer tự do tại Đà Nẵng, thiết kế ứng dụng di động và hệ thống Design System cho nhiều khách hàng quốc tế.",
        "skills": ["Figma", "Design Systems", "User Research", "Mobile UI", "Prototyping"],
        "interests": ["Fintech UI", "Micro-interactions", "Design Thinking"],
        "current_needs": [
            "Tìm Mobile Developer giỏi Flutter/React Native để nhận thầu trọn gói dự án app",
            "Hợp tác phát triển ứng dụng di động cá nhân dạng Indie Project"
        ],
        "current_offers": [
            "Thiết kế UI/UX chuẩn Mobile Design Guidelines",
            "Bộ Design System hoàn chỉnh, export asset tối ưu cho Developer"
        ],
    },
    {
        "email": "long.vu@technova.dev",
        "full_name": "Vũ Hải Long",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=VuHaiLong",
        "profession": "Senior Mobile Developer",
        "company": "TechNova Solutions",
        "location": "Hà Nội",
        "summary": "Senior Mobile Developer với 6 năm kinh nghiệm xây dựng ứng dụng di động Flutter và React Native.",
        "skills": ["Flutter", "React Native", "iOS Swift", "Clean Architecture", "CI/CD Mobile"],
        "interests": ["Mobile Apps", "Fintech", "Indie Hacking", "Cà phê"],
        "current_needs": [
            "Tìm Product Designer giỏi để cùng làm các dự án freelance ngoài giờ và build app indie",
            "Tối ưu trải nghiệm người dùng (UX) cho app đang phát triển"
        ],
        "current_offers": [
            "Phát triển ứng dụng di động đa nền tảng hiệu năng cao",
            "Kinh nghiệm đưa app lên App Store/Google Play và tích hợp thanh toán"
        ],
    },
    {
        "email": "khanh.bui@growthhub.vn",
        "full_name": "Bùi Quốc Khánh",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=BuiQuocKhanh",
        "profession": "Marketing Director",
        "company": "GrowthHub Agency",
        "location": "TP. Hồ Chí Minh",
        "summary": "Giám đốc Marketing tại GrowthHub, chuyên Performance Marketing và B2B growth.",
        "skills": ["Performance Marketing", "B2B Marketing", "Brand Strategy", "Data Analytics"],
        "interests": ["SaaS Growth", "Content Marketing", "Podcasts"],
        "current_needs": ["Tìm Content Creator chuyên nghiệp để sản xuất video ngắn B2B"],
        "current_offers": ["Ngân sách tài trợ và hợp đồng truyền thông dài hạn"],
    },
    {
        "email": "ngoc.lam@viralmedia.vn",
        "full_name": "Lâm Bảo Ngọc",
        "password": "password123",
        "avatar": "https://api.dicebear.com/7.x/initials/svg?seed=LamBaoNgoc",
        "profession": "Content Strategist & Creator",
        "company": "ViralMedia",
        "location": "Hà Nội",
        "summary": "Content Creator và chiến lược gia nội dung số, kênh công nghệ hơn 200k followers.",
        "skills": ["Short-form Video", "Storytelling", "Video Editing", "Content Strategy"],
        "interests": ["Tech Trends", "Creative Writing", "KOL Marketing"],
        "current_needs": ["Hợp tác với các Brand công nghệ uy tín để sản xuất nội dung"],
        "current_offers": ["Kỹ năng sáng tạo video viral và kịch bản video hấp dẫn"],
    }
]


def seed_real_users(db: Session) -> dict[str, User]:
    """Tạo hoặc cập nhật các User thật với Assistant Memories và Chat History thực tế."""
    user_map = {}
    now = datetime.now(VN_TZ)

    for data in REAL_USERS_DATA:
        user = db.query(User).filter(User.email == data["email"]).first()
        if not user:
            user = User(
                email=data["email"],
                password_hash=get_password_hash(data["password"]),
                full_name=data["full_name"],
                avatar=data["avatar"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created real user: {user.email} ({user.full_name})")
        else:
            user.full_name = data["full_name"]
            user.avatar = data["avatar"]
            db.commit()

        user_map[data["email"]] = user

        # Clear old memories for this user
        db.query(AssistantMemory).filter(AssistantMemory.owner_user_id == user.id).delete()
        db.commit()

        # Create dummy conversation for memory link if needed
        dummy_conv = (
            db.query(Conversation)
            .filter(
                (Conversation.user_a_id == user.id) | (Conversation.user_b_id == user.id)
            )
            .first()
        )
        if not dummy_conv:
            dummy_conv = Conversation(
                user_a_id=user.id,
                user_b_id=user.id,
                created_at=now,
                updated_at=now,
            )
            db.add(dummy_conv)
            db.commit()
            db.refresh(dummy_conv)

        # Create rich AssistantMemory with real facts
        memory = AssistantMemory(
            owner_user_id=user.id,
            conversation_id=dummy_conv.id,
            summary=data["summary"],
            facts={
                "profession": data["profession"],
                "company": data["company"],
                "location": data.get("location", "Hà Nội"),
                "skills": data["skills"],
                "interests": data["interests"],
                "looking_for": data["current_needs"],
                "current_needs": data["current_needs"],
                "offering": data["current_offers"],
                "current_offers": data["current_offers"],
            },

        )
        db.add(memory)
        db.commit()

    return user_map


def seed_real_recommendations_for_user(db: Session, target_user: User, user_map: dict[str, User]):
    """Tạo các gợi ý kết nối thật bằng AI Agent cho target_user."""
    logger.info(f"AI Agent generating live recommendations for: {target_user.email}")

    # Xóa các recommendations cũ của target_user
    db.query(Recommendation).filter(Recommendation.owner_user_id == target_user.id).delete()
    db.commit()

    agent = ConnectionRecommendationAgent()
    recs = asyncio.run(agent.generate(target_user.id, min_score=0.5, limit=5))
    logger.info(f"   ✓ AI Agent dynamically generated {len(recs)} real recommendations for {target_user.email}")


def main():
    parser = argparse.ArgumentParser(description="Seed real users and recommendations")
    parser.add_argument("--email", help="Specific user to seed recommendations for")
    args = parser.parse_args()


    db = SessionLocal()
    try:
        # 1. Seed Real Users & Assistant Memories
        user_map = seed_real_users(db)

        # 2. Seed recommendations for main user(s)
        if args.email:
            target = user_map.get(args.email) or db.query(User).filter(User.email == args.email).first()
            if target:
                seed_real_recommendations_for_user(db, target, user_map)
        else:
            # Seed for user1@gmail.com and other test users
            for email in ["user1@gmail.com", "user2@gmail.com", "demo@example.com"]:
                u = user_map.get(email) or db.query(User).filter(User.email == email).first()
                if u:
                    seed_real_recommendations_for_user(db, u, user_map)

        print("\n" + "=" * 65)
        print("SEED REAL USERS & RECOMMENDATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 65)
        print("Created REAL User Accounts in database (password: password123):")
        print("  - user1@gmail.com             (Tech Product Lead - Main Test Account)")
        print("  - quan.tran@vinai.io          (Senior AI / LLM Engineer @ VinAI)")
        print("  - nam.le@edutech.vn           (Startup Founder & CEO @ EduTech Labs)")
        print("  - long.vu@technova.dev        (Senior Mobile Developer @ TechNova)")
        print("  - thao.nguyen@globalbrands.vn (E-commerce Manager @ GlobalBrands)")
        print("  - ducanh.pham@fastcargo.vn    (Head of BD @ FastCargo Logistics)")
        print("  - chi.dang@studiominimal.io   (Lead Product Designer @ Studio Minimal)")
        print("  - khanh.bui@growthhub.vn      (Marketing Director @ GrowthHub)")
        print("  - ngoc.lam@viralmedia.vn      (Content Strategist & Creator @ ViralMedia)")
        print("=" * 65)
        print("Test on Web:")
        print("  1. Login with: user1@gmail.com / password123")
        print("  2. Visit: http://localhost:3000/recommendations")
        print("  3. Click 'Gui loi chao & Mo Chat' to start real chat!")
        print("=" * 65 + "\n")


    finally:
        db.close()


if __name__ == "__main__":
    main()
