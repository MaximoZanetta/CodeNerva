from fastapi.testclient import TestClient

from codenerva.main import app

client = TestClient(app)


def test_create_project_endpoint() -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "CodeNerva",
            "description": "Code intelligence platform",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "CodeNerva"
    assert body["description"] == "Code intelligence platform"
    assert body["status"] == "ACTIVE"
    assert body["id"]


def test_create_project_rejects_blank_name() -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "   ",
        },
    )

    assert response.status_code == 422
