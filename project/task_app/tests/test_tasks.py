
import random
import string

def random_string(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def test_db_health(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    body = response.text
    assert "db_up" in body
    assert "db_query_latency_seconds" in body



def test_create_task(client):
    random_title = random_string(10)
    payload = {
        "title": random_title,
        "description": "string",
        "status": "pending"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 200 or response.status_code == 201
    
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == payload["status"]
    assert "id" in data 
    
def test_get_all_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "items" in data

    assert isinstance(data["items"], list)

    if data["items"]:
        task = data["items"][0]
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "status" in task 
    
def test_get_task_by_id(client):
    payload = {
        "title": f"Task {random_string()}",
        "description": "delete me",
        "status": "pending"
    }
    create_response = client.post("/tasks", json=payload)
    assert create_response.status_code in (200, 201)
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id    
    
def test_update_task_by_id(client):
    payload = {
        "title": f"Task {random_string()}",
        "description": "delete me",
        "status": "pending"
    }
    create_response = client.post("/tasks", json=payload)
    assert create_response.status_code in (200, 201)
    task_id = create_response.json()["id"]
    
    random_update = random_string(10)
    payload = {
        "title": random_update,
        "status": "completed"
    }
    response = client.patch(f"/tasks/{task_id}", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == payload["status"]    
    
def test_delete_task_by_id(client):
    payload = {
        "title": f"Task {random_string()}",
        "description": "delete me",
        "status": "pending"
    }
    create_response = client.post("/tasks", json=payload)
    assert create_response.status_code in (200, 201)
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code in (200, 204)

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404   