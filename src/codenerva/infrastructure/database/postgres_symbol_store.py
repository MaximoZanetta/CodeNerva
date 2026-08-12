from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_store import SymbolStore
from codenerva.infrastructure.database.models.symbol_model import (
    SymbolModel,
)


class PostgresSymbolStore(SymbolStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save_many(
        self,
        symbols: tuple[Symbol, ...],
    ) -> None:
        if not symbols:
            return

        with self._session_factory() as session:
            for symbol in symbols:
                model = SymbolModel(
                    id=symbol.id,
                    source_file_id=symbol.source_file_id,
                    name=symbol.name,
                    qualified_name=symbol.qualified_name,
                    kind=symbol.kind.value,
                    start_line=symbol.start_line,
                    end_line=symbol.end_line,
                    parent_symbol_id=symbol.parent_symbol_id,
                )

                session.merge(model)

            session.commit()

    def get_by_id(
        self,
        symbol_id: UUID,
    ) -> Symbol | None:
        with self._session_factory() as session:
            model = session.get(
                SymbolModel,
                symbol_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[Symbol, ...]:
        with self._session_factory() as session:
            statement = (
                select(SymbolModel)
                .where(SymbolModel.source_file_id == source_file_id)
                .order_by(
                    SymbolModel.start_line,
                    SymbolModel.end_line,
                )
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def _to_domain(
        self,
        model: SymbolModel,
    ) -> Symbol:
        return Symbol(
            id=model.id,
            source_file_id=model.source_file_id,
            name=model.name,
            qualified_name=model.qualified_name,
            kind=SymbolKind(model.kind),
            start_line=model.start_line,
            end_line=model.end_line,
            parent_symbol_id=model.parent_symbol_id,
        )

    def delete_by_source_file_ids(
        self,
        source_file_ids: tuple[UUID, ...],
    ) -> int:
        if not source_file_ids:
            return 0

        with self._session_factory() as session:
            statement = delete(SymbolModel).where(
                SymbolModel.source_file_id.in_(source_file_ids)
            )

            result = session.execute(statement)
            session.commit()

            return result.rowcount or 0
