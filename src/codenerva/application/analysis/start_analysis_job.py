from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.analysis_job import (
    AnalysisJob,
    AnalysisJobStatus,
)
from codenerva.domain.analysis_job_store import (
    AnalysisJobStore,
)
from codenerva.domain.snapshot_store import SnapshotStore


class AnalysisSnapshotNotFoundError(Exception):
    pass


class AnalysisJobAlreadyRunningError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class StartAnalysisJobResult:
    job: AnalysisJob


class StartAnalysisJobUseCase:
    def __init__(
        self,
        *,
        snapshot_store: SnapshotStore,
        analysis_job_store: AnalysisJobStore,
    ) -> None:
        self._snapshot_store = snapshot_store
        self._analysis_job_store = analysis_job_store

    def execute(
        self,
        *,
        snapshot_id: UUID,
    ) -> StartAnalysisJobResult:
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            raise AnalysisSnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        existing_job = self._analysis_job_store.get_by_snapshot_id(snapshot_id)

        if existing_job is not None and existing_job.status not in {
            AnalysisJobStatus.READY,
            AnalysisJobStatus.FAILED,
        }:
            raise AnalysisJobAlreadyRunningError(
                f"An analysis job is already running for snapshot {snapshot_id}."
            )

        job = AnalysisJob.create(
            snapshot_id=snapshot_id,
        )

        self._analysis_job_store.save(job)

        return StartAnalysisJobResult(
            job=job,
        )
