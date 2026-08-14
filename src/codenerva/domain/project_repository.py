from typing import Protocol
from uuid import UUID

from codenerva.domain.project import Project


class ProjectRepository(Protocol):
    def save(self, project: Project) -> None: ...

    def get_by_id(self, project_id: UUID) -> Project | None: ...

    def list_all(self) -> tuple[Project, ...]: ...
