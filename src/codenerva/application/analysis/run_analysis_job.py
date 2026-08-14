from dataclasses import replace
from uuid import UUID

from codenerva.application.analysis.analysis_pipeline import (
    AnalysisPipeline,
)
from codenerva.domain.analysis_job import (
    AnalysisJob,
    AnalysisJobStatus,
)
from codenerva.domain.analysis_job_store import (
    AnalysisJobStore,
)
from codenerva.domain.snapshot import (
    SnapshotStatus,
)
from codenerva.domain.snapshot_store import (
    SnapshotStore,
)


class AnalysisJobNotFoundError(Exception):
    pass


class AnalysisJobNotQueuedError(Exception):
    pass


class RunAnalysisJobUseCase:
    def __init__(
        self,
        *,
        analysis_job_store: AnalysisJobStore,
        analysis_pipeline: AnalysisPipeline,
        snapshot_store: SnapshotStore,
    ) -> None:
        self._analysis_job_store = analysis_job_store
        self._analysis_pipeline = analysis_pipeline
        self._snapshot_store = snapshot_store

    def execute(
        self,
        *,
        job_id: UUID,
    ) -> AnalysisJob:
        job = self._analysis_job_store.get_by_id(job_id)

        if job is None:
            raise AnalysisJobNotFoundError(
                f"Analysis job with id {job_id} was not found."
            )

        if job.status is not AnalysisJobStatus.QUEUED:
            raise AnalysisJobNotQueuedError(
                "Only queued analysis jobs can be executed."
            )

        try:
            job = self._transition(
                job=job,
                status=AnalysisJobStatus.DISCOVERING,
                progress=10,
            )

            self._analysis_pipeline.discover(
                snapshot_id=job.snapshot_id,
            )

            job = self._transition(
                job=job,
                status=AnalysisJobStatus.PROCESSING,
                progress=30,
            )

            self._analysis_pipeline.process(
                snapshot_id=job.snapshot_id,
            )

            job = job.mark_ready()

            self._analysis_job_store.save(job)

            self._update_snapshot_status(
                snapshot_id=job.snapshot_id,
                status=SnapshotStatus.READY,
            )

            return job

        except Exception as exc:  # noqa: BLE001
            failed_job = job.mark_failed(
                error_message=(str(exc) or exc.__class__.__name__),
            )

            self._analysis_job_store.save(failed_job)

            self._update_snapshot_status(
                snapshot_id=failed_job.snapshot_id,
                status=SnapshotStatus.FAILED,
            )

            return failed_job

    def _transition(
        self,
        *,
        job: AnalysisJob,
        status: AnalysisJobStatus,
        progress: int,
    ) -> AnalysisJob:
        updated_job = job.transition_to(
            status=status,
            progress=progress,
        )

        self._analysis_job_store.save(updated_job)

        return updated_job

    def _update_snapshot_status(
        self,
        *,
        snapshot_id: UUID,
        status: SnapshotStatus,
    ) -> None:
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            return

        updated_snapshot = replace(
            snapshot,
            status=status,
        )

        self._snapshot_store.save(updated_snapshot)
