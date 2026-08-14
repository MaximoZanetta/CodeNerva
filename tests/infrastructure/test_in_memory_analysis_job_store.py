from uuid import uuid4

from codenerva.domain.analysis_job import AnalysisJob
from codenerva.infrastructure.in_memory_analysis_job_store import (
    InMemoryAnalysisJobStore,
)


def test_analysis_job_store_saves_and_loads_job() -> None:
    store = InMemoryAnalysisJobStore()

    job = AnalysisJob.create(
        snapshot_id=uuid4(),
    )

    store.save(job)

    assert store.get_by_id(job.id) == job
    assert store.get_by_snapshot_id(job.snapshot_id) == job
