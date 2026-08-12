from uuid import UUID

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)
from codenerva.infrastructure.database.models.source_file_relation_model import (
    SourceFileRelationModel,
)


class PostgresSourceFileRelationStore(SourceFileRelationStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save_many(
        self,
        relations: tuple[SourceFileRelation, ...],
    ) -> None:
        if not relations:
            return

        with self._session_factory() as session:
            for relation in relations:
                model = SourceFileRelationModel(
                    id=relation.id,
                    source_file_id=relation.source_file_id,
                    target_file_id=relation.target_file_id,
                    kind=relation.kind.value,
                )

                session.merge(model)

            session.commit()

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]:
        with self._session_factory() as session:
            statement = (
                select(SourceFileRelationModel)
                .where(SourceFileRelationModel.source_file_id == source_file_id)
                .order_by(SourceFileRelationModel.target_file_id)
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def list_by_target_file_id(
        self,
        target_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]:
        with self._session_factory() as session:
            statement = (
                select(SourceFileRelationModel)
                .where(SourceFileRelationModel.target_file_id == target_file_id)
                .order_by(SourceFileRelationModel.source_file_id)
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def _to_domain(
        self,
        model: SourceFileRelationModel,
    ) -> SourceFileRelation:
        return SourceFileRelation(
            id=model.id,
            source_file_id=model.source_file_id,
            target_file_id=model.target_file_id,
            kind=SourceFileRelationKind(model.kind),
        )

    def delete_by_source_file_ids(
        self,
        source_file_ids: tuple[UUID, ...],
    ) -> int:
        if not source_file_ids:
            return 0

        with self._session_factory() as session:
            statement = delete(SourceFileRelationModel).where(
                or_(
                    SourceFileRelationModel.source_file_id.in_(source_file_ids),
                    SourceFileRelationModel.target_file_id.in_(source_file_ids),
                )
            )

            result = session.execute(statement)
            session.commit()

            return result.rowcount or 0
