from datetime import datetime, timedelta
from fastapi import status

from app.models import Task


def test_get_all_tasks(db_session, client):
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
