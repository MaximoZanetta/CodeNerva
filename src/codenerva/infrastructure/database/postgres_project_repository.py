from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.project import (
    Project,
    ProjectStatus,
)
from codenerva.domain.project_repository import (
    ProjectRepository,
)
from codenerva.infrastructure.database.models.project_model import (
    ProjectModel,
)


class PostgresProjectRepository(ProjectRepository):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save(
        self,
        project: Project,
    ) -> None:
        with self._session_factory() as session:
            model = ProjectModel(
                id=project.id,
                name=project.name,
                description=project.description,
                status=project.status.value,
            )

            session.merge(model)
            session.commit()

    def get_by_id(
        self,
        project_id: UUID,
    ) -> Project | None:
        with self._session_factory() as session:
            model = session.get(
                ProjectModel,
                project_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def _to_domain(
        self,
        model: ProjectModel,
    ) -> Project:
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            status=ProjectStatus(model.status),
        )
