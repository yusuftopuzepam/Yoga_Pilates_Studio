from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from core.database.tables import LessonType, LessonCategory


class LessonCreate(BaseModel):
    lesson_type: LessonType
    lesson_category: LessonCategory
    room_id: int
    teacher_id: int
    start_time: datetime
    end_time: datetime

    model_config = ConfigDict(extra="forbid")

    @field_validator("end_time")
    def end_after_start(cls, v, info):
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class LessonResponse(BaseModel):
    id: int
    lesson_type: LessonType
    lesson_category: LessonCategory
    room_id: int
    teacher_id: int
    start_time: datetime
    end_time: datetime

    model_config = ConfigDict(from_attributes=True)
