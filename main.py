from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import FastAPI, status, HTTPException, Depends

from app.config import settings
from app.database import Base, engine
from app.dependency import get_db
from app.schemas import TaskRequest, TaskResponse
from app.models import Task
from app.constants import DEFAULT_TITLE, categories


app = FastAPI(
    title=settings.title,
    debug=settings.debug,
    description=settings.description
)

Base.metadata.create_all(bind=engine)


@app.get("/api/v1/tasks", response_model=list[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.deadline).all()


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task ID {task_id} not found."
        )
    return task


@app.post("/api/v1/tasks", response_model=TaskResponse)
def add_task(
    task_data: TaskRequest,
    db: Session = Depends(get_db),
) -> TaskResponse:
    tasks = db.query(Task).all()
    print(tasks)

    task_with_already_exists_title = db.query(Task).filter(Task.title == task_data.title).first()
    if (
        task_with_already_exists_title and
        task_data.title in task_with_already_exists_title.title
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The task '{task_data.title}' already exists."
        )

    if task_data.deadline:
        tomorrow = datetime.now() + timedelta(days=1)
        if (
            task_data.category == categories.today and
            task_data.deadline > tomorrow
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="A Task in the 'TODAY' category cannot have a deadline later than tomorrow."
            )

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        category=task_data.category,
        status=task_data.status,
        deadline=task_data.deadline,
    )
    db.add(new_task)
    db.commit()

    return new_task


@app.patch("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    new_task_data: TaskRequest,
    db: Session = Depends(get_db),
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task ID {task_id} not found."
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
    new_task_data: TaskRequest,
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task ID {task_id} not found."
        )

    if new_task_data.title == DEFAULT_TITLE:
        old_task_title = task.title
        new_task_data.title = old_task_title

    update_data = new_task_data.model_dump()
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
            detail=f"Task ID {task_id} not found."
        )

    db.delete(task)
    db.commit()
