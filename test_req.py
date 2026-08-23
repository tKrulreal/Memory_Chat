import asyncio
from src.database.session import SessionLocal
from src.models.user import User
from src.api.v1.connection_requests import send_connection_request
from src.schemas.connection import ConnectionRequestCreate

db = SessionLocal()
long_user = db.query(User).filter(User.email == "long2004@test.com").first()
demo_user = db.query(User).filter(User.email == "demo@example.com").first()
req_in = ConnectionRequestCreate(target_user_id=demo_user.id)

class MockEventBus:
    async def publish(self, *args, **kwargs):
        pass
    def publish_sync(self, *args, **kwargs):
        pass

try:
    res = send_connection_request(request_in=req_in, current_user=long_user, db=db, event_bus=MockEventBus())
    print("SUCCESS", res)
except Exception as e:
    import traceback
    print("ERROR:")
    traceback.print_exc()
