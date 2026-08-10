from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from codenerva.application.git.git_client import GitClient
from codenerva.domain.repository_store import RepositoryStore
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.snapshot_store import SnapshotStore


class RepositoryNotFoundError(Exception):
    pass


class SnapshotAlreadyExistsError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class CreateSnapshotResult:
    id: UUID
    repository_id: UUID
    commit_sha: str
    branch: str | None
    remote_url: str
    status: str


class CreateSnapshotUseCase:
    def __init__(
        self,
        *,
        repository_store: RepositoryStore,
        snapshot_store: SnapshotStore,
        git_client: GitClient,
        storage_root: Path,
    ) -> None:
        self._repository_store = repository_store
        self._snapshot_store = snapshot_store
        self._git_client = git_client
        self._storage_root = storage_root

    def execute(self, repository_id: UUID) -> CreateSnapshotResult:
        repository = self._repository_store.get_by_id(repository_id)

        if repository is None:
            raise RepositoryNotFoundError(
                f"Repository with id {repository_id} was not found."
            )

        repository_path = self._storage_root / "repositories" / str(repository.id)

        git_info = self._git_client.inspect(
            repository_path=repository_path,
        )

        existing_snapshot = self._snapshot_store.get_by_repository_and_commit(
            repository_id=repository.id,
            commit_sha=git_info.commit_sha,
        )

        if existing_snapshot is not None:
            raise SnapshotAlreadyExistsError(
                "A snapshot for this repository and commit already exists."
            )

        snapshot = Snapshot.create(
            repository_id=repository.id,
            commit_sha=git_info.commit_sha,
            branch=git_info.branch,
            remote_url=git_info.remote_url,
        )

        self._snapshot_store.save(snapshot)

        return CreateSnapshotResult(
            id=snapshot.id,
            repository_id=snapshot.repository_id,
            commit_sha=snapshot.commit_sha,
            branch=snapshot.branch,
            remote_url=snapshot.remote_url,
            status=snapshot.status.value,
        )
