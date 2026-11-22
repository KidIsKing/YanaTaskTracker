from datetime import datetime, timedelta
from fastapi import status

from app.models import Task


def test_get_all_tasks(db_session, client):
    tomorrow_time = datetime.now() + timedelta(days=1)
    one_week_time = datetime.now() + timedelta(weeks=1)
    task1 = Task(
        title="test task 1",
        description="test 1 some info",
        deadline=tomorrow_time,
        category="TODAY"
    )
    task2 = Task(
        title="test task 2",
        description="test 2 some info",
        deadline=one_week_time,
        category="IN PLANS"
    )
    db_session.add(task1)
    db_session.add(task2)
    db_session.commit()
    db_session.refresh(task1)
    db_session.refresh(task2)

    response = client.get("api/v1/tasks")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == 1  # Первый объект соответствует ID 1
    assert response.json()[1]["id"] == 2
    assert response.json()[0]["title"] == "test task 1"
    assert response.json()[1]["title"] == "test task 2"
    # assert isinstance(datetime.strftime(response.json()[0]["deadline"], "%d.%m.%Y %H:%M"), str)
    # assert isinstance(response.json()[1]["deadline"], datetime)
