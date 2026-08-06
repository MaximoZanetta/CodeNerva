from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from codenerva.application.git.git_client import GitClient
from codenerva.domain.repository_store import RepositoryStore


class RepositoryNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class CloneRepositoryResult:
    repository_id: UUID
    destination: Path


class CloneRepositoryUseCase:
    def __init__(
        self,
        *,
        repository_store: RepositoryStore,
        git_client: GitClient,
        storage_root: Path,
    ) -> None:
        self._repository_store = repository_store
        self._git_client = git_client
        self._storage_root = storage_root

    def execute(self, repository_id: UUID) -> CloneRepositoryResult:
        repository = self._repository_store.get_by_id(repository_id)

        if repository is None:
            raise RepositoryNotFoundError(
                f"Repository with id {repository_id} was not found."
            )

        destination = self._storage_root / "repositories" / str(repository.id)

        self._git_client.clone(
            remote_url=repository.remote_url,
            destination=destination,
        )

        return CloneRepositoryResult(
            repository_id=repository.id,
            destination=destination,
        )
