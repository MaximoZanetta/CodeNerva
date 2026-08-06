from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.project_repository import ProjectRepository


class ProjectNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class GetProjectResult:
    id: UUID
    name: str
    description: str | None
    status: str


class GetProjectUseCase:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def execute(self, project_id: UUID) -> GetProjectResult:
        project = self._repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(f"Project with id {project_id} was not found.")

        return GetProjectResult(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status.value,
        )
