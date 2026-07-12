"""
API-level tests for /tasks. These go through real HTTP + auth, which is
exactly the layer where we found the original bug (routes crashing because
user_id was never wired in, and no auth dependency at all). The
`no_auth_header` tests specifically pin down that every task route now
requires a valid token.
"""
from datetime import datetime, timedelta


def test_create_task_requires_auth(client):
    response = client.post("/tasks/", json={"title": "no auth"})
    assert response.status_code in (401, 403)


def test_list_tasks_requires_auth(client):
    response = client.get("/tasks/")
    assert response.status_code in (401, 403)


def test_create_and_list_task(client, auth_headers):
    payload = {
        "user_id": 999,  # deliberately wrong -- server must ignore this
        "title": "Write report",
        "category": "WORK",
        "priority": "HIGH",
        "status": "TODO",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "estimated_minutes": 45,
    }

    create_resp = client.post("/tasks/", json=payload, headers=auth_headers)
    assert create_resp.status_code == 200
    created = create_resp.json()

    # Server must override the client-supplied user_id with the
    # authenticated user's id, not trust the request body.
    assert created["user_id"] != 999
    assert created["title"] == "Write report"

    list_resp = client.get("/tasks/", headers=auth_headers)
    assert list_resp.status_code == 200
    titles = [t["title"] for t in list_resp.json()]
    assert "Write report" in titles


def test_cannot_fetch_another_users_task(client, auth_headers, db_session):
    # Create a task owned by a different user directly in the DB.
    from app.models.user import User
    from app.models.task import Task

    other_user = User(name="Other", email="isolated@example.com")
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    other_task = Task(
        user_id=other_user.id,
        title="Not yours",
        category="WORK",
        priority="LOW",
        status="TODO",
        due_date=datetime.utcnow() + timedelta(days=1),
        estimated_minutes=15,
    )
    db_session.add(other_task)
    db_session.commit()
    db_session.refresh(other_task)

    response = client.get(f"/tasks/{other_task.id}", headers=auth_headers)
    assert response.status_code == 404


def test_complete_task_flow(client, auth_headers):
    create_resp = client.post(
        "/tasks/",
        json={
            "user_id": 1,
            "title": "Finish thing",
            "category": "STUDY",
            "priority": "MEDIUM",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "estimated_minutes": 30,
        },
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    complete_resp = client.patch(
        f"/tasks/{task_id}/complete",
        params={"actual_minutes": 40},
        headers=auth_headers,
    )

    assert complete_resp.status_code == 200
    body = complete_resp.json()
    assert body["status"] == "COMPLETED"
    assert body["actual_minutes"] == 40


def test_delete_task(client, auth_headers):
    create_resp = client.post(
        "/tasks/",
        json={
            "user_id": 1,
            "title": "Delete me",
            "category": "PERSONAL",
            "priority": "LOW",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "estimated_minutes": 10,
        },
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert delete_resp.status_code == 200

    fetch_resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert fetch_resp.status_code == 404


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/tasks/", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
