from datetime import datetime
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.encoders import jsonable_encoder

from app.config import settings
from app.schemas import TaskRequest, TaskUpdate
from app.database import TASKS


app = FastAPI(
    title=settings.title,
    debug=settings.debug,
    description=settings.description
)


@app.get("/health")
def check_health() -> Response:
    return Response(
        content="Everything is good in this project!",
        status_code=status.HTTP_200_OK,
    )


@app.get("/api/v1/tasks")
def get_all_tasks() -> dict:
    return TASKS


@app.get("/api/v1/task_by_title")
def get_task_by_title(task_title: str):
    if task_title not in TASKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_title}' not found."
        )
    return TASKS[task_title]


@app.post("/api/v1/tasks")
def add_task(task: TaskRequest):
    try:
        # Конвертируем строку даты в datetime с определённым форматом
        format_deadline = datetime.strptime(task.deadline, "%d.%m.%Y %H:%M")
    except ValueError as e:
        format_deadline = None
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Incorrect date format: '{e}'. Deadline will be None."
        )
    finally:
        TASKS[task.title] = {
                "description": task.description,
                "deadline": format_deadline,
                "category": task.category,
            }
    return TASKS


@app.patch("/api/v1/tasks/{title}")
def update_task(task: TaskUpdate):
    if task.title not in TASKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task.title}' not found."
        )

    stored_task_data = TASKS[task.title]
    stored_task_model = TaskUpdate(**stored_task_data)
    update_data = task.model_dump(exclude_unset=True)
    updated_task = stored_task_model.model_copy(update=update_data)
    TASKS[task.title] = jsonable_encoder(updated_task)

    return updated_task
