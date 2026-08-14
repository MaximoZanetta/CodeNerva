from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from codenerva.api.analysis_jobs import (
    build_analysis_jobs_router,
)
from codenerva.application.analysis.start_analysis_job import (
    StartAnalysisJobUseCase,
)
from codenerva.domain.analysis_job import (
    AnalysisJob,
    AnalysisJobStatus,
)
from codenerva.domain.snapshot import Snapshot
from codenerva.infrastructure.in_memory_analysis_job_store import (
    InMemoryAnalysisJobStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)


class FakeRunAnalysisJobUseCase:
    def __init__(
        self,
        *,
        analysis_job_store: InMemoryAnalysisJobStore,
    ) -> None:
        self._analysis_job_store = analysis_job_store
        self.calls: list[UUID] = []

    def execute(
        self,
        *,
        job_id: UUID,
    ) -> AnalysisJob:
        self.calls.append(job_id)

        job = self._analysis_job_store.get_by_id(job_id)

        if job is None:
            raise RuntimeError("Analysis job was not found.")

        ready_job = job.mark_ready()

        self._analysis_job_store.save(ready_job)

        return ready_job


def _build_client() -> tuple[
    TestClient,
    InMemorySnapshotStore,
    InMemoryAnalysisJobStore,
    FakeRunAnalysisJobUseCase,
]:
    snapshot_store = InMemorySnapshotStore()
    job_store = InMemoryAnalysisJobStore()

    start_use_case = StartAnalysisJobUseCase(
        snapshot_store=snapshot_store,
        analysis_job_store=job_store,
    )

    run_use_case = FakeRunAnalysisJobUseCase(
        analysis_job_store=job_store,
    )

    app = FastAPI()

    app.include_router(
        build_analysis_jobs_router(
            start_analysis_job_use_case=start_use_case,
            run_analysis_job_use_case=run_use_case,
            analysis_job_store=job_store,
        )
    )

    return (
        TestClient(app),
        snapshot_store,
        job_store,
        run_use_case,
    )


def _create_snapshot() -> Snapshot:
    return Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )


def test_start_analysis_job_returns_202() -> None:
    (
        client,
        snapshot_store,
        _,
        run_use_case,
    ) = _build_client()

    snapshot = _create_snapshot()
    snapshot_store.save(snapshot)

    response = client.post(
        "/api/v1/analysis-jobs",
        json={
            "snapshot_id": str(snapshot.id),
        },
    )

    assert response.status_code == 202

    payload = response.json()

    assert payload["snapshot_id"] == str(snapshot.id)

    assert payload["status"] == "QUEUED"
    assert payload["progress"] == 0
    assert payload["error_message"] is None

    assert len(run_use_case.calls) == 1


def test_start_analysis_job_rejects_unknown_snapshot() -> None:
    client, _, _, run_use_case = _build_client()

    snapshot_id = uuid4()

    response = client.post(
        "/api/v1/analysis-jobs",
        json={
            "snapshot_id": str(snapshot_id),
        },
    )

    assert response.status_code == 404
    assert run_use_case.calls == []


def test_get_analysis_job_after_background_execution() -> None:
    client, snapshot_store, _, _ = _build_client()

    snapshot = _create_snapshot()
    snapshot_store.save(snapshot)

    created = client.post(
        "/api/v1/analysis-jobs",
        json={
            "snapshot_id": str(snapshot.id),
        },
    )

    job_id = created.json()["id"]

    response = client.get(f"/api/v1/analysis-jobs/{job_id}")

    assert response.status_code == 200

    payload = response.json()

    assert payload["id"] == job_id
    assert payload["snapshot_id"] == str(snapshot.id)

    assert payload["status"] == (AnalysisJobStatus.READY.value)

    assert payload["progress"] == 100


def test_get_unknown_analysis_job_returns_404() -> None:
    client, _, _, _ = _build_client()

    response = client.get(f"/api/v1/analysis-jobs/{uuid4()}")

    assert response.status_code == 404
