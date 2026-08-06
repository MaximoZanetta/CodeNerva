from uuid import uuid4

from fastapi.testclient import TestClient

from codenerva.main import app

client = TestClient(app)


def test_register_repository_endpoint() -> None:
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Repository Project"},
    )

    project_id = project_response.json()["id"]

    response = client.post(
        f"/api/v1/projects/{project_id}/repository",
        json={
            "url": "https://github.com/example/shop",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["project_id"] == project_id
    assert body["remote_url"] == "https://github.com/example/shop"
    assert body["owner"] == "example"
    assert body["name"] == "shop"
    assert body["status"] == "ACTIVE"


def test_register_repository_returns_404_for_unknown_project() -> None:

    response = client.post(
        f"/api/v1/projects/{uuid4()}/repository",
        json={
            "url": "https://github.com/example/shop",
        },
    )

    assert response.status_code == 404


def test_project_cannot_register_two_repositories() -> None:
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Single Repository Project"},
    )

    project_id = project_response.json()["id"]
    payload = {"url": "https://github.com/example/shop"}

    first_response = client.post(
        f"/api/v1/projects/{project_id}/repository",
        json=payload,
    )
    second_response = client.post(
        f"/api/v1/projects/{project_id}/repository",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
