import pytest
import requests
from fastapi.testclient import TestClient
from task_app.app.services_config.config import *
from task_app.app.main import app


@pytest.fixture(scope="session")
def access_token():
    data = {
        "grant_type": GRANT_TYPE,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

@pytest.fixture
def client(access_token):
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client
