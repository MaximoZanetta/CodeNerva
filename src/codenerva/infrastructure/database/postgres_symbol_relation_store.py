from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)
from codenerva.domain.symbol_relation_store import (
    SymbolRelationStore,
)
from codenerva.infrastructure.database.models.symbol_relation_model import (
    SymbolRelationModel,
)


class PostgresSymbolRelationStore(SymbolRelationStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save_many(
        self,
        relations: tuple[SymbolRelation, ...],
    ) -> None:
        if not relations:
            return

        with self._session_factory() as session:
            for relation in relations:
                model = SymbolRelationModel(
                    id=relation.id,
                    source_symbol_id=relation.source_symbol_id,
                    target_symbol_id=relation.target_symbol_id,
                    kind=relation.kind.value,
                )

                session.merge(model)

            session.commit()

    def list_by_source_symbol_id(
        self,
        source_symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]:
        with self._session_factory() as session:
            statement = (
                select(SymbolRelationModel)
                .where(SymbolRelationModel.source_symbol_id == source_symbol_id)
                .order_by(SymbolRelationModel.target_symbol_id)
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def list_by_target_symbol_id(
        self,
        target_symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]:
        with self._session_factory() as session:
            statement = (
                select(SymbolRelationModel)
                .where(SymbolRelationModel.target_symbol_id == target_symbol_id)
                .order_by(SymbolRelationModel.source_symbol_id)
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def _to_domain(
        self,
        model: SymbolRelationModel,
    ) -> SymbolRelation:
        return SymbolRelation(
            id=model.id,
            source_symbol_id=model.source_symbol_id,
            target_symbol_id=model.target_symbol_id,
            kind=SymbolRelationKind(model.kind),
        )
