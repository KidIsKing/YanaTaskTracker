from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import FastAPI, status, HTTPException, Depends

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


def format_deadline(deadline):
    try:
        # Конвертируем строку даты в datetime с определённым форматом
        format_deadline = datetime.strptime(deadline, "%d.%m.%Y %H:%M")
    except ValueError:
        tomorrow = datetime.now() + timedelta(days=1)
        format_deadline = datetime.strftime(tomorrow, "%d.%m.%Y %H:%M")
        # raise HTTPException(
        #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        #     detail=f"Incorrect date format: '{e}'. Deadline will be TOMORROW."
        # )
    return format_deadline


@app.get("/api/v1/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/api/v1/task_by_id", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} ID not found."
        )
    return task


@app.post("/api/v1/tasks")
def add_task(
    task_title: str,
    description: str | None = None,
    deadline: str | None = None,
    category: str | None = "Today",
    db: Session = Depends(get_db),
) -> TaskResponse:
    deadline = format_deadline(deadline)
    task = Task(
        title=task_title,
        description=description,
        deadline=deadline,
        category=category
    )
    db.add(task)
    db.commit()
    return task


@app.patch("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    new_task_data: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task.title}' not found."
        )

    update_data = new_task_data.model_dump(exclude_unset=True)
    # Обновляем атрибуты найденного объекта
    for key, value in update_data.items():
        setattr(task, key, value)

    task.deadline = format_deadline(task.deadline)

    db.commit()
    db.refresh(task)

    return task


@app.put("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def replace_task(
    task_id: int,
    new_task_data: TaskUpdate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task.title}' not found."
        )

    task.title = "Default title"
    task.description = None
    task.deadline = format_deadline(task.deadline)
    task.category = "Today"

    update_data = new_task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


@app.delete("/api/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task.title}' not found."
        )

    db.delete(task)
    db.commit()
