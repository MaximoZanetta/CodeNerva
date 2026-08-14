from datetime import UTC
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.snapshot import (
    Snapshot,
    SnapshotStatus,
)
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.infrastructure.database.models.snapshot_model import (
    SnapshotModel,
)


class PostgresSnapshotStore(SnapshotStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save(
        self,
        snapshot: Snapshot,
    ) -> None:
        with self._session_factory() as session:
            model = SnapshotModel(
                id=snapshot.id,
                repository_id=snapshot.repository_id,
                commit_sha=snapshot.commit_sha,
                branch=snapshot.branch,
                remote_url=snapshot.remote_url,
                status=snapshot.status.value,
                created_at=snapshot.created_at,
            )

            session.merge(model)
            session.commit()

    def get_by_id(
        self,
        snapshot_id: UUID,
    ) -> Snapshot | None:
        with self._session_factory() as session:
            model = session.get(
                SnapshotModel,
                snapshot_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def get_by_repository_and_commit(
        self,
        repository_id: UUID,
        commit_sha: str,
    ) -> Snapshot | None:
        with self._session_factory() as session:
            statement = select(SnapshotModel).where(
                SnapshotModel.repository_id == repository_id,
                SnapshotModel.commit_sha == commit_sha,
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def _to_domain(
        self,
        model: SnapshotModel,
    ) -> Snapshot:
        created_at = model.created_at

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=UTC,
            )

        return Snapshot(
            id=model.id,
            repository_id=model.repository_id,
            commit_sha=model.commit_sha,
            branch=model.branch,
            remote_url=model.remote_url,
            status=SnapshotStatus(model.status),
            created_at=created_at,
        )

    def delete(
        self,
        snapshot_id: UUID,
    ) -> bool:
        with self._session_factory() as session:
            statement = delete(SnapshotModel).where(SnapshotModel.id == snapshot_id)

            result = session.execute(statement)
            session.commit()

            return bool(result.rowcount)

    def list_by_repository_id(
        self,
        repository_id: UUID,
    ) -> tuple[Snapshot, ...]:
        with self._session_factory() as session:
            statement = (
                select(SnapshotModel)
                .where(SnapshotModel.repository_id == repository_id)
                .order_by(SnapshotModel.created_at.asc())
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)
