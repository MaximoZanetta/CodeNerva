from uuid import UUID

from codenerva.domain.analysis_job import AnalysisJob


class InMemoryAnalysisJobStore:
    def __init__(self) -> None:
        self._jobs: dict[UUID, AnalysisJob] = {}

    def save(
        self,
        job: AnalysisJob,
    ) -> None:
        self._jobs[job.id] = job

    def get_by_id(
        self,
        job_id: UUID,
    ) -> AnalysisJob | None:
        return self._jobs.get(job_id)

    def get_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> AnalysisJob | None:
        matching_jobs = tuple(
            job for job in self._jobs.values() if job.snapshot_id == snapshot_id
        )

        if not matching_jobs:
            return None

        return max(
            matching_jobs,
            key=lambda job: job.created_at,
        )
