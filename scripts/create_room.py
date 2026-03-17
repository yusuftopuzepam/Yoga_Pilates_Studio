from core.database.db_connection import SessionLocal
from core.database.tables import StudioRoom, RoomType


def create_room():
    db = SessionLocal()
    existing_rooms = db.query(StudioRoom).count()
    if existing_rooms > 0:
        print("Studio odası zaten mevcut.")
        db.close()
        return
    rooms = [
        StudioRoom(name="Yoga Room 1", capacity=4, room_type=RoomType.YOGA),
        StudioRoom(name="Yoga Room 2", capacity=4, room_type=RoomType.YOGA),
        StudioRoom(name="Pilates Room 1", capacity=4, room_type=RoomType.PILATES),
        StudioRoom(name="Pilates Room 2", capacity=4, room_type=RoomType.PILATES),
    ]
    db.add_all(rooms)
    db.commit()
    db.close()
    print("Studio odaları oluşturuldu.")


if __name__ == "__main__":
    create_room()
