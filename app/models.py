from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.constants import CATEGORY_DEFAULT


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(nullable=True)
    category: Mapped[str | None] = mapped_column(default=CATEGORY_DEFAULT, nullable=True)
