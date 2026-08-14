from uuid import UUID

from codenerva.domain.project import Project
from codenerva.domain.project_repository import ProjectRepository


class InMemoryProjectRepository(ProjectRepository):
    def __init__(self) -> None:
        self._projects: dict[UUID, Project] = {}

    def save(self, project: Project) -> None:
        self._projects[project.id] = project

    def get_by_id(self, project_id: UUID) -> Project | None:
        return self._projects.get(project_id)

    def list_all(
        self,
    ) -> tuple[Project, ...]:
        return tuple(
            sorted(
                self._projects.values(),
                key=lambda project: project.name,
            )
        )
