from core.database.db_connection import SessionLocal
from core.database.tables import User, UserRole
from core.security import get_password_hash


def create_admin():
    db = SessionLocal()

    existing_admin = db.query(User).filter(User.role == "admin").first()
    if existing_admin:
        print("Admin zaten mevcut.")
        db.close()
        return
    admin = User(
        name="Super Admin",
        email="admin@system.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.admin,
    )
    db.add(admin)
    db.commit()
    db.close()
    print("Admin olusturuldu")

if __name__ == "__main__":
    create_admin()