from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder

from app.config import settings
from app.database import Base, engine
from app.dependency import get_db
from app.schemas import TaskRequest, TaskUpdate, TaskResponse
from app.models import Task


app = FastAPI(
    title=settings.title,
    debug=settings.debug,
    description=settings.description
)

Base.metadata.create_all(bind=engine)


@app.get("/api/v1/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/api/v1/task_by_title", response_model=TaskResponse)
def get_task_by_title(
    task_title: str,
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.title == task_title).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_title}' not found."
        )
    return task


@app.post("/api/v1/tasks")
def add_task(
    task_title: str,
    description: str | None = None,
    deadline: str | None = None,
    category: str | None = "Today",
    db: Session = Depends(get_db),
):
    try:
        # Конвертируем строку даты в datetime с определённым форматом
        format_deadline = datetime.strptime(deadline, "%d.%m.%Y %H:%M")
    except ValueError as e:
        format_deadline = datetime.strftime(datetime.now() + timedelta(days=1), "%d.%m.%Y %H:%M")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Incorrect date format: '{e}'. Deadline will be TOMORROW."
        )
    finally:
        task = Task(
            title=task_title,
            description=description,
            deadline=format_deadline,
            category=category
        )
        db.add(task)
        db.commit()
    return task


@app.patch("/api/v1/tasks/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task.title}' not found."
        )

    update_data = task_data.model_dump(exclude_unset=True)
    # Обновляем атрибуты найденного объекта
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task
