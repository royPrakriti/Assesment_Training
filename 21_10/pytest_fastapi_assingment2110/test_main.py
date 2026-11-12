from urllib import response

from fastapi.testclient import TestClient
from main import app,task_day

client = TestClient(app)

def test_get_task():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_task_by_id():
    response = client.get("/tasks/1")
    assert response.status_code == 200

    assert response.json().get("id") == 1

def test_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404



def test_add_task():
    response = client.post("/tasks", json = {"id":4,"title":"check server logs","status":"Pending"})
    assert response.status_code == 200
    assert response.json().get("id") == 4
    assert response.json().get("title") == "check server logs"

def test_added_task_missing():
    response = client.post("/tasks", json = {"title":"check server logs","status":"Pending"})
    assert response.status_code == 422


def test_update_task():
    response = client.put("/tasks/2",json = {"id":2, "title":"Practice pytest","status":"Completed"})
    assert response.status_code == 200
    assert response.json().get("task").get("status") == "Completed"


def test_delete_3():
    response = client.delete("/tasks/3")
    assert response.status_code == 200

    response = client.get("/tasks/3")
    assert response.status_code == 404