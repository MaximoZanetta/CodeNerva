from uuid import UUID, uuid4

import pytest

from codenerva.application.analysis.run_analysis_job import (
    AnalysisJobNotFoundError,
    AnalysisJobNotQueuedError,
    RunAnalysisJobUseCase,
)
from codenerva.domain.analysis_job import (
    AnalysisJob,
    AnalysisJobStatus,
)
from codenerva.domain.snapshot import (
    Snapshot,
    SnapshotStatus,
)
from codenerva.infrastructure.in_memory_analysis_job_store import (
    InMemoryAnalysisJobStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)


class FakeAnalysisPipeline:
    def __init__(
        self,
        *,
        fail_at: str | None = None,
    ) -> None:
        self.fail_at = fail_at
        self.calls: list[str] = []
        self.snapshot_ids: list[UUID] = []

    def discover(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        self._execute_stage(
            stage="discover",
            snapshot_id=snapshot_id,
        )

    def process(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        self._execute_stage(
            stage="process",
            snapshot_id=snapshot_id,
        )

    def _execute_stage(
        self,
        *,
        stage: str,
        snapshot_id: UUID,
    ) -> None:
        self.calls.append(stage)
        self.snapshot_ids.append(snapshot_id)

        if self.fail_at == stage:
            raise RuntimeError(f"{stage} failed.")


def _create_snapshot() -> Snapshot:
    return Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )


def test_run_analysis_job_completes_pipeline() -> None:
    snapshot = _create_snapshot()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    job_store = InMemoryAnalysisJobStore()

    job = AnalysisJob.create(
        snapshot_id=snapshot.id,
    )

    job_store.save(job)

    pipeline = FakeAnalysisPipeline()

    use_case = RunAnalysisJobUseCase(
        analysis_job_store=job_store,
        analysis_pipeline=pipeline,
        snapshot_store=snapshot_store,
    )

    result = use_case.execute(
        job_id=job.id,
    )

    assert result.status is AnalysisJobStatus.READY
    assert result.progress == 100
    assert result.error_message is None

    assert pipeline.calls == [
        "discover",
        "process",
    ]

    assert all(snapshot_id == snapshot.id for snapshot_id in pipeline.snapshot_ids)

    saved_job = job_store.get_by_id(job.id)

    assert saved_job == result

    saved_snapshot = snapshot_store.get_by_id(snapshot.id)

    assert saved_snapshot is not None
    assert saved_snapshot.status is SnapshotStatus.READY


def test_run_analysis_job_marks_failed_when_pipeline_fails() -> None:
    snapshot = _create_snapshot()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    job_store = InMemoryAnalysisJobStore()

    job = AnalysisJob.create(
        snapshot_id=snapshot.id,
    )

    job_store.save(job)

    pipeline = FakeAnalysisPipeline(
        fail_at="process",
    )

    use_case = RunAnalysisJobUseCase(
        analysis_job_store=job_store,
        analysis_pipeline=pipeline,
        snapshot_store=snapshot_store,
    )

    result = use_case.execute(
        job_id=job.id,
    )

    assert result.status is AnalysisJobStatus.FAILED
    assert result.progress == 30
    assert result.error_message == "process failed."

    assert pipeline.calls == [
        "discover",
        "process",
    ]

    saved_job = job_store.get_by_id(job.id)

    assert saved_job == result

    saved_snapshot = snapshot_store.get_by_id(snapshot.id)

    assert saved_snapshot is not None
    assert saved_snapshot.status is SnapshotStatus.FAILED


def test_run_analysis_job_rejects_unknown_job() -> None:
    use_case = RunAnalysisJobUseCase(
        analysis_job_store=InMemoryAnalysisJobStore(),
        analysis_pipeline=FakeAnalysisPipeline(),
        snapshot_store=InMemorySnapshotStore(),
    )

    with pytest.raises(AnalysisJobNotFoundError):
        use_case.execute(
            job_id=uuid4(),
        )


def test_run_analysis_job_rejects_non_queued_job() -> None:
    snapshot = _create_snapshot()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    job_store = InMemoryAnalysisJobStore()

    job = AnalysisJob.create(
        snapshot_id=snapshot.id,
    ).transition_to(
        status=AnalysisJobStatus.PROCESSING,
        progress=30,
    )

    job_store.save(job)

    use_case = RunAnalysisJobUseCase(
        analysis_job_store=job_store,
        analysis_pipeline=FakeAnalysisPipeline(),
        snapshot_store=snapshot_store,
    )

    with pytest.raises(AnalysisJobNotQueuedError):
        use_case.execute(
            job_id=job.id,
        )


def test_run_analysis_job_marks_failed_when_discovery_fails() -> None:
    snapshot = _create_snapshot()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    job_store = InMemoryAnalysisJobStore()

    job = AnalysisJob.create(
        snapshot_id=snapshot.id,
    )

    job_store.save(job)

    pipeline = FakeAnalysisPipeline(
        fail_at="discover",
    )

    use_case = RunAnalysisJobUseCase(
        analysis_job_store=job_store,
        analysis_pipeline=pipeline,
        snapshot_store=snapshot_store,
    )

    result = use_case.execute(
        job_id=job.id,
    )

    assert result.status is AnalysisJobStatus.FAILED
    assert result.progress == 10
    assert result.error_message == "discover failed."

    assert pipeline.calls == [
        "discover",
    ]

    saved_job = job_store.get_by_id(job.id)

    assert saved_job == result

    saved_snapshot = snapshot_store.get_by_id(snapshot.id)

    assert saved_snapshot is not None
    assert saved_snapshot.status is SnapshotStatus.FAILED
