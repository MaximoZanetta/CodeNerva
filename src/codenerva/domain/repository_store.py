from typing import Protocol
from uuid import UUID

from codenerva.domain.repository import Repository


class RepositoryStore(Protocol):
    def save(self, repository: Repository) -> None: ...

    def get_by_id(self, repository_id: UUID) -> Repository | None: ...

    def get_by_project_id(self, project_id: UUID) -> Repository | None: ...
