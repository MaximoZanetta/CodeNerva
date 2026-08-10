from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from codenerva.api.dependencies import (
    git_client,
    repository_store,
    snapshot_store,
    storage_root,
)
from codenerva.application.repository.clone_repository import (
    CloneRepositoryUseCase,
)
from codenerva.application.repository.clone_repository import (
    RepositoryNotFoundError as CloneRepositoryNotFoundError,
)
from codenerva.application.repository.create_snapshot import (
    CreateSnapshotUseCase,
    SnapshotAlreadyExistsError,
)
from codenerva.application.repository.create_snapshot import (
    RepositoryNotFoundError as SnapshotRepositoryNotFoundError,
)
from codenerva.infrastructure.subprocess_git_client import GitCloneError

router = APIRouter(
    prefix="/api/v1/repositories",
    tags=["repositories"],
)


class CloneRepositoryResponse(BaseModel):
    repository_id: str
    destination: str


class SnapshotResponse(BaseModel):
    id: str
    repository_id: str
    commit_sha: str
    branch: str | None
    remote_url: str
    status: str


def get_clone_repository_use_case() -> CloneRepositoryUseCase:
    return CloneRepositoryUseCase(
        repository_store=repository_store,
        git_client=git_client,
        storage_root=storage_root,
    )


def get_create_snapshot_use_case() -> CreateSnapshotUseCase:
    return CreateSnapshotUseCase(
        repository_store=repository_store,
        snapshot_store=snapshot_store,
        git_client=git_client,
        storage_root=storage_root,
    )


@router.post(
    "/{repository_id}/clone",
    response_model=CloneRepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def clone_repository(
    repository_id: UUID,
    use_case: Annotated[
        CloneRepositoryUseCase,
        Depends(get_clone_repository_use_case),
    ],
) -> CloneRepositoryResponse:
    try:
        result = use_case.execute(repository_id)
    except CloneRepositoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except GitCloneError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return CloneRepositoryResponse(
        repository_id=str(result.repository_id),
        destination=str(result.destination),
    )


@router.post(
    "/{repository_id}/snapshots",
    response_model=SnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_snapshot(
    repository_id: UUID,
    use_case: Annotated[
        CreateSnapshotUseCase,
        Depends(get_create_snapshot_use_case),
    ],
) -> SnapshotResponse:
    try:
        result = use_case.execute(repository_id)
    except SnapshotRepositoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except SnapshotAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except GitCloneError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return SnapshotResponse(
        id=str(result.id),
        repository_id=str(result.repository_id),
        commit_sha=result.commit_sha,
        branch=result.branch,
        remote_url=result.remote_url,
        status=result.status,
    )
