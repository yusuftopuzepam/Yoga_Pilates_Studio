from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Boolean,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)

    teacher_profile = relationship(
        "TeacherProfile", back_populates="user", uselist=False
    )


class RoomType(enum.Enum):
    YOGA = "yoga"
    PILATES = "pilates"


class StudioRoom(Base):
    __tablename__ = "studio_rooms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)


class Specialty(enum.Enum):
    yoga = "yoga"
    pilates = "pilates"
    both = "both"


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    specialty = Column(Enum(Specialty), nullable=False)

    user = relationship("User", back_populates="teacher_profile")


class LessonType(enum.Enum):
    private = "private"
    group = "group"


class StudentCredit(Base):
    __tablename__ = "student_credits"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_type = Column(Enum(LessonType), nullable=False)
    remaining_count = Column(Integer, nullable=False, default=0)


class LessonCategory(enum.Enum):
    yoga = "yoga"
    pilates = "pilates"


class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_type = Column(Enum(LessonType), nullable=False)
    lesson_category = Column(Enum(LessonCategory), nullable=False)

    room_id = Column(Integer, ForeignKey("studio_rooms.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    room = relationship("StudioRoom")
    reservations = relationship("Reservation", back_populates="lesson")


class Reservation(Base):
    __tablename__ = "reservations"

    __table_args__ = (UniqueConstraint("lesson_id", "student_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    lesson = relationship("Lesson", back_populates="reservations")
