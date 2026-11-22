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


@app.get("/api/v1/tasks", response_model=list[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
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


@app.post("/api/v1/tasks", response_model=TaskResponse)
def add_task(
    task_data: TaskRequest,
    db: Session = Depends(get_db),
) -> TaskResponse:
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        deadline=task_data.deadline,
        category=task_data.category
    )
    db.add(new_task)
    db.commit()
    return new_task


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
            detail=f"Task {task_id} ID not found."
        )

    update_data = new_task_data.model_dump(exclude_unset=True)
    # Обновляем атрибуты найденного объекта
    for key, value in update_data.items():
        setattr(task, key, value)

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

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} ID not found."
        )

    task.title = "Default title"
    task.description = "Default description"
    task.deadline = datetime.now() + timedelta(days=1)
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
            detail=f"Task {task_id} ID not found."
        )

    db.delete(task)
    db.commit()
