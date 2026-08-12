from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.repository import (
    Repository,
    RepositoryProvider,
    RepositoryStatus,
)
from codenerva.domain.repository_store import RepositoryStore
from codenerva.infrastructure.database.models.repository_model import (
    RepositoryModel,
)


class PostgresRepositoryStore(RepositoryStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save(
        self,
        repository: Repository,
    ) -> None:
        with self._session_factory() as session:
            model = RepositoryModel(
                id=repository.id,
                project_id=repository.project_id,
                provider=repository.provider.value,
                remote_url=repository.remote_url,
                owner=repository.owner,
                name=repository.name,
                status=repository.status.value,
            )

            session.merge(model)
            session.commit()

    def get_by_id(
        self,
        repository_id: UUID,
    ) -> Repository | None:
        with self._session_factory() as session:
            model = session.get(
                RepositoryModel,
                repository_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def get_by_project_id(
        self,
        project_id: UUID,
    ) -> Repository | None:
        with self._session_factory() as session:
            statement = select(RepositoryModel).where(
                RepositoryModel.project_id == project_id
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def _to_domain(
        self,
        model: RepositoryModel,
    ) -> Repository:
        return Repository(
            id=model.id,
            project_id=model.project_id,
            provider=RepositoryProvider(model.provider),
            remote_url=model.remote_url,
            owner=model.owner,
            name=model.name,
            status=RepositoryStatus(model.status),
        )
