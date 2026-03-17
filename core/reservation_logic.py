from http.client import HTTPException

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from core.database.tables import Lesson, LessonType, Reservation, StudentCredit


def create_reservation(
    db: Session,
    lesson_id: int,
    student_id: int,
):
    try:
        with db.begin():
            lesson = db.execute(
                select(Lesson).where(Lesson.id == lesson_id).with_for_update()
            ).scalar_one()

            if lesson.start_time - datetime.utcnow() < timedelta(hours=24):
                raise HTTPException(
                    status_code=400, detail="Derse 24 saat kala rezervasyon yapılamaz"
                )

            max_capacity = (
                1 if lesson.lesson_type == LessonType.private else lesson.room.capacity
            )

            current_count = db.execute(
                select(func.count(Reservation.id)).where(
                    Reservation.lesson_id == lesson.id, Reservation.is_active == True
                )
            ).scalar()

            if current_count >= max_capacity:
                raise HTTPException(status_code=400, detail="Ders dolu")

            credit = db.execute(
                select(StudentCredit)
                .where(
                    StudentCredit.user_id == student_id,
                    StudentCredit.lesson_type == lesson.lesson_type,
                )
                .with_for_update()
            ).scalar_one_or_none()

            if not credit or credit.remaining_count <= 0:
                raise Exception("Yetersiz ders hakkı")

            reservation = Reservation(
                lesson_id=lesson.id, student_id=student_id, is_active=True
            )

            credit.remaining_count -= 1

            db.add(reservation)

    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Bu derste zaten aktif bir rezervasyonunuz var"
        )


def cancel_reservation(db: Session, reservation: Reservation, student_id: int):
    try:
        with db.begin():
            if not reservation.is_active:
                raise HTTPException(
                    status_code=400, detail="Rezervasyon zaten iptal edilmis"
                )

            if reservation.lesson.start_time - datetime.utcnow() < timedelta(hours=24):
                raise HTTPException(
                    status_code=400, detail="24 saat kala rezervasyon iptali yapilamaz"
                )
            reservation.is_active = False
            reservation.deleted_at = datetime.utcnow()

            credit = (
                db.query(StudentCredit)
                .filter(
                    StudentCredit.user_id == student_id,
                    reservation.lesson.lesson_type == StudentCredit.lesson_type,
                )
                .with_for_update()
                .one()
            )

            if not credit:
                raise HTTPException(
                    status_code=404, detail="Ogrenci kredisi bulunamadi"
                )

            credit.remaining_count += 1

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Ders zaten iptal edilmis durumda")
