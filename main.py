from fastapi import FastAPI, Response, status, HTTPException

from app.config import settings
from app.database import TASKS


app = FastAPI(
    title=settings.title,
    debug=settings.debug,
)


@app.get("/health")
def check_health() -> Response:
    return Response(
        content="Everything is good in this project!",
        status_code=status.HTTP_200_OK,
    )


@app.get("/all_tasks")
def get_all_tasks() -> dict:
    return TASKS


@app.get("/task_by_title")
def get_task_by_title(title: str) -> dict:
    if title not in TASKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{title}' not found."
        )
    return TASKS[title]



@app.post("/add_task")
def add_task(title: str, description: str = None, deadline: str = None) -> dict:
    TASKS[title] = {
        "description": description,
        "deadline": deadline,
    }
    return TASKS
