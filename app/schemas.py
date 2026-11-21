from datetime import datetime
from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    title: str = Field(..., max_leght=100, description="Название задачи")
    description: str = Field(default=None, max_leght=250, description="Описание задачи")
    deadline: str = Field(default=None, max_leght=50, description="Дедлайн задачи. Строго в формате: 'ДЕНЬ.МЕСЯЦ.ГОД ЧАСЫ:МИНУТЫ'")
    category: str = Field(default="Today", max_leght=100, description="Категория задачи")


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_leght=100, description="Название задачи")
    description: str | None = Field(default=None, max_leght=250, description="Описание задачи")
    deadline: str | None = Field(default=None, max_leght=50, description="Дедлайн задачи. Строго в формате: 'ДЕНЬ.МЕСЯЦ.ГОД ЧАСЫ:МИНУТЫ'")
    category: str | None = Field(default="Today", max_leght=100, description="Категория задачи")
