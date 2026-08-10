from uuid import uuid4

from fastapi.testclient import TestClient

from codenerva.main import app

client = TestClient(app)


def test_discover_snapshot_files_returns_404_for_unknown_snapshot() -> None:
    response = client.post(f"/api/v1/snapshots/{uuid4()}/discover-files")

    assert response.status_code == 404


def test_analyze_snapshot_returns_404_for_unknown_snapshot() -> None:
    response = client.post(f"/api/v1/snapshots/{uuid4()}/analyze")

    assert response.status_code == 404
