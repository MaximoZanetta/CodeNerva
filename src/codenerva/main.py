from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from codenerva.api.analysis_jobs import (
    build_analysis_jobs_router,
)
from codenerva.api.dependencies import (
    analysis_job_store,
    get_run_analysis_job_use_case,
    get_start_analysis_job_use_case,
)
from codenerva.api.health import router as health_router
from codenerva.api.projects import router as projects_router
from codenerva.api.repositories import router as repositories_router
from codenerva.api.snapshots import router as snapshots_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="CodeNerva API",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(projects_router)
    app.include_router(repositories_router)
    app.include_router(snapshots_router)

    app.include_router(
        build_analysis_jobs_router(
            start_analysis_job_use_case=(get_start_analysis_job_use_case()),
            run_analysis_job_use_case=(get_run_analysis_job_use_case()),
            analysis_job_store=analysis_job_store,
        )
    )

    return app


app = create_app()
