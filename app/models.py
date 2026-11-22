from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.constants import status


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str | None]
    category: Mapped[str | None]
    # status: Mapped[str] = mapped_column(default=status.in_process)
    deadline: Mapped[datetime | None]
    # created_at: Mapped[datetime] = mapped_column(default=datetime.now())
