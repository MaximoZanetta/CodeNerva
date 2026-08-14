from uuid import uuid4

import pytest

from codenerva.application.analysis.start_analysis_job import (
    AnalysisJobAlreadyRunningError,
    AnalysisSnapshotNotFoundError,
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


def _create_snapshot() -> Snapshot:
    return Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )


def test_start_analysis_job_creates_queued_job() -> None:
    snapshot = _create_snapshot()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    job_store = InMemoryAnalysisJobStore()

    use_case = StartAnalysisJobUseCase(
        snapshot_store=snapshot_store,
        analysis_job_store=job_store,
    )

    result = use_case.execute(
        snapshot_id=snapshot.id,
    )

    assert result.job.snapshot_id == snapshot.id
    assert result.job.status is AnalysisJobStatus.QUEUED
    assert result.job.progress == 0

    assert job_store.get_by_id(result.job.id) == result.job


def test_start_analysis_job_rejects_unknown_snapshot() -> None:
    use_case = StartAnalysisJobUseCase(
        snapshot_store=InMemorySnapshotStore(),
        analysis_job_store=InMemoryAnalysisJobStore(),
    )

    with pytest.raises(AnalysisSnapshotNotFoundError):
        use_case.execute(
            snapshot_id=uuid4(),
        )


def test_start_analysis_job_rejects_running_job() -> None:
    snapshot = _create_snapshot()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    job_store = InMemoryAnalysisJobStore()

    existing_job = AnalysisJob.create(
        snapshot_id=snapshot.id,
    ).transition_to(
        status=AnalysisJobStatus.PROCESSING,
        progress=40,
    )

    job_store.save(existing_job)

    use_case = StartAnalysisJobUseCase(
        snapshot_store=snapshot_store,
        analysis_job_store=job_store,
    )

    with pytest.raises(AnalysisJobAlreadyRunningError):
        use_case.execute(
            snapshot_id=snapshot.id,
        )


def test_start_analysis_job_allows_retry_after_failed_job() -> None:
    snapshot = _create_snapshot()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    job_store = InMemoryAnalysisJobStore()

    failed_job = AnalysisJob.create(
        snapshot_id=snapshot.id,
    ).mark_failed(
        error_message="Parser failed.",
    )

    job_store.save(failed_job)

    use_case = StartAnalysisJobUseCase(
        snapshot_store=snapshot_store,
        analysis_job_store=job_store,
    )

    result = use_case.execute(
        snapshot_id=snapshot.id,
    )

    assert result.job.id != failed_job.id
    assert result.job.status is AnalysisJobStatus.QUEUED
