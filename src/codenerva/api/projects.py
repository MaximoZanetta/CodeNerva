from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from codenerva.api.dependencies import (
    project_repository,
    repository_store,
)
from codenerva.application.project.create_project import (
    CreateProjectCommand,
    CreateProjectResult,
    CreateProjectUseCase,
)
from codenerva.application.repository.register_repository import (
    ProjectNotFoundError as RegisterProjectNotFoundError,
)
from codenerva.application.repository.register_repository import (
    RegisterRepositoryCommand,
    RegisterRepositoryResult,
    RegisterRepositoryUseCase,
    RepositoryAlreadyExistsError,
)

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["projects"],
)


class CreateProjectRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    description: Annotated[str | None, Field(max_length=500)] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    status: str


def get_create_project_use_case() -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repository)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    request: CreateProjectRequest,
    use_case: Annotated[
        CreateProjectUseCase,
        Depends(get_create_project_use_case),
    ],
) -> ProjectResponse:
    try:
        result: CreateProjectResult = use_case.execute(
            CreateProjectCommand(
                name=request.name,
                description=request.description,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ProjectResponse(
        id=str(result.id),
        name=result.name,
        description=result.description,
        status=result.status,
    )


class RegisterRepositoryRequest(BaseModel):
    url: str


class RepositoryResponse(BaseModel):
    id: str
    project_id: str
    remote_url: str
    owner: str
    name: str
    status: str


def get_register_repository_use_case() -> RegisterRepositoryUseCase:
    return RegisterRepositoryUseCase(
        project_repository=project_repository,
        repository_store=repository_store,
    )


@router.post(
    "/{project_id}/repository",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_repository(
    project_id: UUID,
    request: RegisterRepositoryRequest,
    use_case: Annotated[
        RegisterRepositoryUseCase,
        Depends(get_register_repository_use_case),
    ],
) -> RepositoryResponse:
    try:
        result: RegisterRepositoryResult = use_case.execute(
            RegisterRepositoryCommand(
                project_id=project_id,
                remote_url=request.url,
            )
        )
    except RegisterProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except RepositoryAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return RepositoryResponse(
        id=str(result.id),
        project_id=str(result.project_id),
        remote_url=result.remote_url,
        owner=result.owner,
        name=result.name,
        status=result.status,
    )
