from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator


class TaskRequest(BaseModel):
    title: str = Field(..., max_length=100, description="Название задачи")
    description: str | None = Field(default=None, max_length=250, description="Описание задачи")
    deadline: datetime | None = Field(default=None, description="Дедлайн задачи. Строго в формате: 'ДЕНЬ.МЕСЯЦ.ГОД ЧАСЫ:МИНУТЫ'")
    category: str | None = Field(default="Today", max_length=100, description="Категория задачи")

    @field_validator("title")
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Task title cannot be empty.")
        return v

    @field_validator("deadline", mode="before")
    def deadline_in_correct_format(cls, v: str) -> datetime:
        return format_deadline(v)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=100, description="Название задачи")
    description: str | None = Field(default=None, max_length=250, description="Описание задачи")
    deadline: datetime | None = Field(default=None, description="Дедлайн задачи. Строго в формате: 'ДЕНЬ.МЕСЯЦ.ГОД ЧАСЫ:МИНУТЫ'")
    category: str | None = Field(default="Today", max_length=100, description="Категория задачи")

    @field_validator("title")
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Task title cannot be empty.")
        return v

    @field_validator("deadline", mode="before")
    def deadline_in_correct_format(cls, v: str) -> datetime:
        return format_deadline(v)


class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    description: str | None = None
    deadline: datetime
    category: str = "Today"


def format_deadline(deadline):
    try:
        # Конвертируем строку даты в datetime с определённым форматом
        format_deadline = datetime.strptime(deadline, "%d.%m.%Y %H:%M")
    except Exception:
        tomorrow = datetime.now() + timedelta(days=1)
        format_deadline = tomorrow
        # format_deadline = datetime.strftime(tomorrow, "%d.%m.%Y %H:%M")
        # raise HTTPException(
        #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        #     detail=f"Incorrect date format: '{e}'. Deadline will be TOMORROW."
        # )
    return format_deadline
