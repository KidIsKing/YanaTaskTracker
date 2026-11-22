from datetime import datetime
from pydantic import BaseModel, Field, field_validator, field_serializer

from app.constants import categories, statuses


class TaskRequest(BaseModel):
    title: str = Field(..., max_length=100, description="Название задачи")
    description: str | None = Field(default=None, max_length=250, description="Описание задачи")
    category: str = Field(default=categories.in_plans, max_length=100, description="Категория задачи")
    status: str = Field(default=statuses.in_process, max_length=100, description="Статус задачи")
    deadline: datetime | None = Field(default=None, description="Дедлайн задачи. Строго в формате: 'ДЕНЬ.МЕСЯЦ.ГОД ЧАСЫ:МИНУТЫ'")

    @field_validator("title")
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Task title cannot be empty.")
        return v

    @field_validator("deadline", mode="before")
    def parse_deadline(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        return format_deadline(v)


class TaskUpdate(BaseModel):
    title: str | None = Field(default="task title", max_length=100, description="Название задачи")
    description: str | None = Field(default=None, max_length=250, description="Описание задачи")
    category: str = Field(default=categories.in_plans, max_length=100, description="Категория задачи")
    status: str = Field(default=statuses.in_process, max_length=100, description="Статус задачи")
    deadline: datetime | None = Field(default=None, description="Дедлайн задачи. Строго в формате: 'ДЕНЬ.МЕСЯЦ.ГОД ЧАСЫ:МИНУТЫ'")

    @field_validator("title")
    def title_not_empty_or_null(cls, v: str | None) -> str:
        if v is None:
            raise ValueError("Task title cannot be null.")
        v = v.strip()
        if not v:
            raise ValueError("Task title cannot be empty.")
        return v

    @field_validator("deadline", mode="before")
    def parse_deadline(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
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
