"""
from core.security import get_password_hash
from core.database.db_connection import SessionLocal, engine
from core.database.tables import User, UserRole

db = SessionLocal()

print(engine.url)
user = User(
    name="Testuser",
    email="testuser@test.com",
    password_hash=get_password_hash("123456"),
    role=UserRole.student
)

db.add(user)
db.commit()
db.close()
"""
