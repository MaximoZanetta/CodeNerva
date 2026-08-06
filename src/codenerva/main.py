from fastapi import FastAPI

from codenerva.api.health import router as health_router
from codenerva.api.projects import router as projects_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="CodeNerva API",
        version="0.1.0",
    )

    app.include_router(health_router)
    app.include_router(projects_router)

    return app


app = create_app()
