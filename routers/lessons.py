from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from core.database.db_connection import get_db
from core.database.tables import Lesson, StudioRoom, User
from core.security import require_roles, UserRole
from pydantic_models.lesson_model import LessonCreate, LessonResponse

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_in: LessonCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles([UserRole.admin, UserRole.teacher])),
):
    # If current user is a teacher, they can only create lessons for themselves
    if (
        current_user.role == UserRole.teacher
        and current_user.id != lesson_in.teacher_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers can only create their own lessons",
        )

    # Validate room exists
    room = db.query(StudioRoom).filter(StudioRoom.id == lesson_in.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )

    # Validate teacher exists and has a teacher profile
    teacher = db.query(User).filter(User.id == lesson_in.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher user not found"
        )
    if teacher.role != UserRole.teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a teacher"
        )

    # Validate time range
    if lesson_in.end_time <= lesson_in.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be after start_time",
        )

    # Check for overlapping lessons for same room or same teacher
    overlap_filter = and_(
        Lesson.start_time < lesson_in.end_time,
        Lesson.end_time > lesson_in.start_time,
    )

    conflict = (
        db.query(Lesson)
        .filter(
            overlap_filter,
            or_(
                Lesson.room_id == lesson_in.room_id,
                Lesson.teacher_id == lesson_in.teacher_id,
            ),
        )
        .first()
    )

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lesson conflicts with existing lesson for the same room or teacher",
        )

    lesson = Lesson(
        lesson_type=lesson_in.lesson_type,
        lesson_category=lesson_in.lesson_category,
        room_id=lesson_in.room_id,
        teacher_id=lesson_in.teacher_id,
        start_time=lesson_in.start_time,
        end_time=lesson_in.end_time,
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return lesson
