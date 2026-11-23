from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator, field_serializer

from app.constants import (
    DEFAULT_TITLE, DEFAULT_DESCRIPTION, DEFAULT_CATEGORY,
    DEFAULT_STATUS, DEFAULT_DEADLINE, statuses
)


class TaskRequest(BaseModel):
    title: str = Field(default=DEFAULT_TITLE, max_length=100, description="Название задачи")
    description: str | None = Field(default=DEFAULT_DESCRIPTION, max_length=250, description="Описание задачи")
    category: str = Field(default=DEFAULT_CATEGORY, max_length=100, description="Категория задачи")
    status: str = Field(default=DEFAULT_STATUS, max_length=100, description="Статус задачи")
    deadline: datetime | None = Field(default=DEFAULT_DEADLINE, description="Дедлайн задачи. Строго в формате: 'ДЕНЬ.МЕСЯЦ.ГОД ЧАСЫ:МИНУТЫ'")

    @field_validator("title")
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Task title cannot be empty.")
        return v

    @field_validator("status")
    def not_custom_status(cls, v: str) -> str:
        if v not in [statuses.in_process, statuses.in_process, statuses.blocked]:
            raise ValueError(
                "Task's status cannot be custom. "
                f"Try: '{statuses.in_process}', '{statuses.done}' or '{statuses.blocked}'."
            )
        return v

    @field_validator("deadline")
    def actual_deadline(cls, v: datetime) -> datetime:
        min_timedelta_for_deadline = datetime.now() + timedelta(hours=1)  # 1 час
        if v and v < min_timedelta_for_deadline:
            raise ValueError("Deadline cannot be less than one hour.")
        return v

    @field_validator("deadline", mode="before")
    def parse_deadline(cls, v):
        if v is None:
            return None
        return format_deadline(v)


class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    description: str | None
    category: str
    status: str
    deadline: datetime | None
    created_at: datetime

    @field_serializer("deadline")
    def serialize_deadline(self, v: datetime | None) -> str | None:
        if isinstance(v, datetime):
            return v.strftime("%d.%m.%Y %H:%M")
        return v

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime) -> str:
        return v.strftime("%d.%m.%Y %H:%M:%S")


def format_deadline(deadline: str) -> datetime:
    return datetime.strptime(deadline, "%d.%m.%Y %H:%M")
