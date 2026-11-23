from datetime import datetime, timedelta
from fastapi import status

from app.models import Task
from app.constants import (
    DEFAULT_TITLE, DEFAULT_DESCRIPTION, DEFAULT_CATEGORY,
    DEFAULT_STATUS, DEFAULT_DEADLINE, categories, statuses
)


def test_get_all_valid_tasks(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    one_week_time = datetime.now() + timedelta(weeks=1)
    task1 = Task(
        title="test task 1",
        description="test 1 some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=one_week_time,
    )
    task2 = Task(
        title="test task 2",
        description="test 2 some info",
        category="IN PLANS",
        status="IN PROCESS",
        deadline=tomorrow_time,
    )
    db_session.add(task1)
    db_session.add(task2)
    db_session.commit()
    db_session.refresh(task1)
    db_session.refresh(task2)

    response = client.get("api/v1/tasks")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == 2  # Ранний дедлайн соответствует объекту с ID 2
    assert response.json()[1]["id"] == 1
    assert response.json()[0]["title"] == "test task 2"
    assert response.json()[1]["title"] == "test task 1"


def test_get_task_by_valid_id(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    task = Task(
        title="test task",
        description="test some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=tomorrow_time,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.get(f"/api/v1/tasks/{task.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "test task"
    assert datetime.strptime(data["deadline"], "%d.%m.%Y %H:%M") > datetime.strptime(data["created_at"], "%d.%m.%Y %H:%M:%S")


def test_get_task_by_not_exists_id(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    task = Task(
        title="test task",
        description="test some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=tomorrow_time,
    )  # Задача с ID 1
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    incorrect_id = 2
    response = client.get(f"/api/v1/tasks/{incorrect_id}")  # Другой ID

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Task ID {incorrect_id} not found."


def test_add_valid_task(client):
    tomorrow_time_str = datetime.strftime((datetime.now() + timedelta(days=1)), "%d.%m.%Y %H:%M")
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "new test task",
            "description": "test some info",
            "category": "TODAY",
            "status": "IN PROCESS",
            "deadline": tomorrow_time_str,
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "new test task"
    assert datetime.strptime(data["deadline"], "%d.%m.%Y %H:%M") > datetime.strptime(data["created_at"], "%d.%m.%Y %H:%M:%S")


def test_add_task_without_values(client):  # Тест значений по умолчанию
    response = client.post("/api/v1/tasks", json={})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == DEFAULT_TITLE
    assert data["description"] == DEFAULT_DESCRIPTION
    assert data["category"] == DEFAULT_CATEGORY
    assert data["status"] == DEFAULT_STATUS
    assert data["deadline"] == DEFAULT_DEADLINE


def test_add_task_with_empty_title(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "  "
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["msg"] == "Value error, Task title cannot be empty."


def test_add_task_with_too_much_title(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best yana is the best "
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_task_with_already_exists_title(client, db_session):
    task = Task(
        title="test task title",
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "test task title"
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_add_task_with_custom_status(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "status": "custom status"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["msg"] == "Value error, Task's status cannot be custom. Try: 'IN PROCESS', 'DONE' or 'BLOCKED'."


def test_add_task_with_invalid_deadline(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "category": "TODAY",
            "deadline": "23.12.26 15:16"  # Год должен быть в формате YYYY
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_task_with_deadline_later_tomorrow_and_today_category(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "category": "TODAY",
            "deadline": "23.12.2026 15:16"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"] == "A Task in the 'TODAY' category cannot have a deadline later than tomorrow."


def test_update_valid_task(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    task = Task(
        title="test task",
        description="test some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=tomorrow_time,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.patch(
        f"/api/v1/tasks/{task.id}",
        json={
            "description": "anoter description",
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "test task"
    assert data["description"] == "anoter description"
    assert data["category"] == "TODAY"
    assert data["status"] == "IN PROCESS"
    assert datetime.strptime(data["deadline"], "%d.%m.%Y %H:%M") > datetime.strptime(data["created_at"], "%d.%m.%Y %H:%M:%S")


def test_replace_valid_task(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    task = Task(
        title="test task",
        description="test some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=tomorrow_time,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json={
            "description": "anoter description",
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "test task"  # Старое название сохранилось
    assert data["description"] == "anoter description"  # Изменённое поле
    # Дефолтные значения
    assert data["category"] == DEFAULT_CATEGORY
    assert data["status"] == DEFAULT_STATUS
    assert data["deadline"] == DEFAULT_DEADLINE


def test_delete_valid_task(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    task = Task(
        title="test task",
        description="test some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=tomorrow_time,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.delete(f"/api/v1/tasks/{task.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
