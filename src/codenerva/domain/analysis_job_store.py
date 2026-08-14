from typing import Protocol
from uuid import UUID

from codenerva.domain.analysis_job import AnalysisJob


class AnalysisJobStore(Protocol):
    def save(
        self,
        job: AnalysisJob,
    ) -> None: ...

    def get_by_id(
        self,
        job_id: UUID,
    ) -> AnalysisJob | None: ...

    def get_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> AnalysisJob | None: ...
