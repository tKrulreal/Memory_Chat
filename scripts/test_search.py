import asyncio
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.search import SearchAgent

async def main():
    agent = SearchAgent()
    
    queries = [
        "người thích lập trình Python",
        "ai có kinh nghiệm làm DevOps",
        "nhân sự giỏi về AI",
        "chuyên gia thiết kế UI/UX",
        "những người làm quản lý dự án"
    ]
    
    print("=== BẮT ĐẦU TEST SEARCH AGENT ===")
    for q in queries:
        print(f"\n[Query]: {q}")
        try:
            results = await agent.search(q, limit=3)
            if not results:
                print("  => Không tìm thấy kết quả phù hợp.")
            for r in results:
                print(f"  - [{r.score}] {r.name} ({r.contact_id})")
                print(f"    {r.explanation}")
        except Exception as e:
            print(f"  => Lỗi khi search: {e}")
            
    print("\n=== HOÀN THÀNH ===")

if __name__ == "__main__":
    asyncio.run(main())
