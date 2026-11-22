from datetime import datetime, timedelta
from fastapi import status

from app.models import Task


def test_get_all_valid_tasks(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    one_week_time = datetime.now() + timedelta(weeks=1)
    task1 = Task(
        title="test task 1",
        description="test 1 some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=one_week_time,
        created_at=datetime.now()
    )
    task2 = Task(
        title="test task 2",
        description="test 2 some info",
        category="IN PLANS",
        status="IN PROCESS",
        deadline=tomorrow_time,
        created_at=datetime.now()
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
        created_at=datetime.now()
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.get(f"/api/v1/tasks/{task.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "test task"
    assert datetime.strptime(data["deadline"], "%d.%m.%Y %H:%M") > datetime.strptime(data["created_at"], "%d.%m.%Y %H:%M:%S")


def test_add_valid_task(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "new test task",
            "description": "test some info",
            "category": "TODAY",
            "status": "IN PROCESS",
            "deadline": "23.11.2026 21:39",
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "new test task"
    assert datetime.strptime(data["deadline"], "%d.%m.%Y %H:%M") > datetime.strptime(data["created_at"], "%d.%m.%Y %H:%M:%S")


def test_update_valid_task(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    task = Task(
        title="test task",
        description="test some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=tomorrow_time,
        created_at=datetime.now()
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
        created_at=datetime.now()
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
    assert data["title"] == "task title"
    assert data["description"] == "anoter description"
    assert data["category"] == "IN PLANS"
    assert data["status"] == "IN PROCESS"
    assert data["deadline"] == None


def test_delete_valid_task(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    task = Task(
        title="test task",
        description="test some info",
        category="TODAY",
        status="IN PROCESS",
        deadline=tomorrow_time,
        created_at=datetime.now()
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.delete(f"/api/v1/tasks/{task.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
