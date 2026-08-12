from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.chunk import Chunk, ChunkKind
from codenerva.domain.chunk_store import ChunkStore
from codenerva.infrastructure.database.models.chunk_model import (
    ChunkModel,
)


class PostgresChunkStore(ChunkStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save_many(
        self,
        chunks: tuple[Chunk, ...],
    ) -> None:
        if not chunks:
            return

        with self._session_factory() as session:
            for chunk in chunks:
                model = ChunkModel(
                    id=chunk.id,
                    snapshot_id=chunk.snapshot_id,
                    source_file_id=chunk.source_file_id,
                    symbol_id=chunk.symbol_id,
                    kind=chunk.kind.value,
                    text=chunk.text,
                    code=chunk.code,
                    relative_path=chunk.relative_path,
                    language=chunk.language,
                    qualified_name=chunk.qualified_name,
                    symbol_kind=chunk.symbol_kind,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    part_index=chunk.part_index,
                    part_count=chunk.part_count,
                )

                session.merge(model)

            session.commit()

    def get_by_id(
        self,
        chunk_id: UUID,
    ) -> Chunk | None:
        with self._session_factory() as session:
            model = session.get(
                ChunkModel,
                chunk_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def list_by_symbol_id(
        self,
        symbol_id: UUID,
    ) -> tuple[Chunk, ...]:
        with self._session_factory() as session:
            statement = (
                select(ChunkModel)
                .where(ChunkModel.symbol_id == symbol_id)
                .order_by(ChunkModel.part_index)
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def _to_domain(
        self,
        model: ChunkModel,
    ) -> Chunk:
        return Chunk(
            id=model.id,
            snapshot_id=model.snapshot_id,
            source_file_id=model.source_file_id,
            symbol_id=model.symbol_id,
            kind=ChunkKind(model.kind),
            text=model.text,
            relative_path=model.relative_path,
            language=model.language,
            qualified_name=model.qualified_name,
            symbol_kind=model.symbol_kind,
            start_line=model.start_line,
            end_line=model.end_line,
            part_index=model.part_index,
            part_count=model.part_count,
            code=model.code,
        )

    def delete_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> int:
        with self._session_factory() as session:
            statement = delete(ChunkModel).where(ChunkModel.snapshot_id == snapshot_id)

            result = session.execute(statement)
            session.commit()

            return result.rowcount or 0
