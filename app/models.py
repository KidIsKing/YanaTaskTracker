from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.constants import categories, statuses


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)
    category: Mapped[str] = mapped_column(default=categories.in_plans)
    status: Mapped[str] = mapped_column(default=statuses.in_process)
    deadline: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime]
