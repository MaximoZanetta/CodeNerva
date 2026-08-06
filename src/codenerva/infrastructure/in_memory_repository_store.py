from uuid import UUID

from codenerva.domain.repository import Repository
from codenerva.domain.repository_store import RepositoryStore


class InMemoryRepositoryStore(RepositoryStore):
    def __init__(self) -> None:
        self._repositories: dict[UUID, Repository] = {}

    def save(self, repository: Repository) -> None:
        self._repositories[repository.id] = repository

    def get_by_id(self, repository_id: UUID) -> Repository | None:
        return self._repositories.get(repository_id)

    def get_by_project_id(self, project_id: UUID) -> Repository | None:
        return next(
            (
                repository
                for repository in self._repositories.values()
                if repository.project_id == project_id
            ),
            None,
        )
