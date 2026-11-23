from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.constants import (
    DEFAULT_TITLE, DEFAULT_DESCRIPTION, DEFAULT_CATEGORY,
    DEFAULT_STATUS, DEFAULT_DEADLINE
)


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(default=DEFAULT_TITLE)
    description: Mapped[str | None] = mapped_column(default=DEFAULT_DESCRIPTION)
    category: Mapped[str] = mapped_column(default=DEFAULT_CATEGORY)
    status: Mapped[str] = mapped_column(default=DEFAULT_STATUS)
    deadline: Mapped[datetime | None] = mapped_column(default=DEFAULT_DEADLINE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
