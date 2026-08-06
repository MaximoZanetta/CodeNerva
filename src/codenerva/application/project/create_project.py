from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.project import Project
from codenerva.domain.project_repository import ProjectRepository


@dataclass(frozen=True, slots=True)
class CreateProjectCommand:
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class CreateProjectResult:
    id: UUID
    name: str
    description: str | None
    status: str


class CreateProjectUseCase:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def execute(self, command: CreateProjectCommand) -> CreateProjectResult:
        project = Project.create(
            name=command.name,
            description=command.description,
        )

        self._repository.save(project)

        return CreateProjectResult(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status.value,
        )
