from uuid import uuid4

import pytest

from codenerva.domain.analysis_job import (
    AnalysisJob,
    AnalysisJobStatus,
)


def test_analysis_job_starts_queued() -> None:
    snapshot_id = uuid4()

    job = AnalysisJob.create(
        snapshot_id=snapshot_id,
    )

    assert job.snapshot_id == snapshot_id
    assert job.status is AnalysisJobStatus.QUEUED
    assert job.progress == 0
    assert job.error_message is None


def test_analysis_job_can_transition() -> None:
    job = AnalysisJob.create(
        snapshot_id=uuid4(),
    )

    job = job.transition_to(
        status=AnalysisJobStatus.PROCESSING,
        progress=40,
    )

    assert job.status is AnalysisJobStatus.PROCESSING
    assert job.progress == 40


def test_analysis_job_progress_cannot_decrease() -> None:
    job = AnalysisJob.create(
        snapshot_id=uuid4(),
    )

    job = job.transition_to(
        status=AnalysisJobStatus.PROCESSING,
        progress=50,
    )

    with pytest.raises(ValueError):
        job.transition_to(
            status=AnalysisJobStatus.PROCESSING,
            progress=40,
        )


def test_analysis_job_can_be_marked_ready() -> None:
    job = AnalysisJob.create(
        snapshot_id=uuid4(),
    )

    job = job.mark_ready()

    assert job.status is AnalysisJobStatus.READY
    assert job.progress == 100


def test_analysis_job_can_be_marked_failed() -> None:
    job = AnalysisJob.create(
        snapshot_id=uuid4(),
    )

    job = job.mark_failed(
        error_message="Parser failed.",
    )

    assert job.status is AnalysisJobStatus.FAILED
    assert job.error_message == "Parser failed."


def test_finished_job_cannot_transition() -> None:
    job = AnalysisJob.create(
        snapshot_id=uuid4(),
    ).mark_ready()

    with pytest.raises(ValueError):
        job.transition_to(
            status=AnalysisJobStatus.PROCESSING,
            progress=90,
        )
