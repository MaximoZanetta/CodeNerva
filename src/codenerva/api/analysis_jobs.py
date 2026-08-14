from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    status,
)
from pydantic import BaseModel

from codenerva.application.analysis.run_analysis_job import (
    RunAnalysisJobUseCase,
)
from codenerva.application.analysis.start_analysis_job import (
    AnalysisJobAlreadyRunningError,
    AnalysisSnapshotNotFoundError,
    StartAnalysisJobUseCase,
)
from codenerva.domain.analysis_job import (
    AnalysisJob,
    AnalysisJobStatus,
)
from codenerva.domain.analysis_job_store import AnalysisJobStore


class StartAnalysisJobRequest(BaseModel):
    snapshot_id: UUID


class AnalysisJobResponse(BaseModel):
    id: UUID
    snapshot_id: UUID
    status: AnalysisJobStatus
    progress: int
    error_message: str | None


def _to_response(
    job: AnalysisJob,
) -> AnalysisJobResponse:
    return AnalysisJobResponse(
        id=job.id,
        snapshot_id=job.snapshot_id,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
    )


def build_analysis_jobs_router(
    *,
    start_analysis_job_use_case: StartAnalysisJobUseCase,
    run_analysis_job_use_case: RunAnalysisJobUseCase,
    analysis_job_store: AnalysisJobStore,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1/analysis-jobs",
        tags=["analysis-jobs"],
    )

    @router.post(
        "",
        response_model=AnalysisJobResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def start_analysis_job(
        request: StartAnalysisJobRequest,
        background_tasks: BackgroundTasks,
    ) -> AnalysisJobResponse:
        try:
            result = start_analysis_job_use_case.execute(
                snapshot_id=request.snapshot_id,
            )
        except AnalysisSnapshotNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except AnalysisJobAlreadyRunningError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

        background_tasks.add_task(
            run_analysis_job_use_case.execute,
            job_id=result.job.id,
        )

        return _to_response(result.job)

    @router.get(
        "/{job_id}",
        response_model=AnalysisJobResponse,
    )
    def get_analysis_job(
        job_id: UUID,
    ) -> AnalysisJobResponse:
        job = analysis_job_store.get_by_id(job_id)

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f"Analysis job with id {job_id} was not found."),
            )

        return _to_response(job)

    return router
