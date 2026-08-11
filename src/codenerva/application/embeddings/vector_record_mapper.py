from codenerva.domain.chunk import Chunk
from codenerva.domain.vector_record import VectorRecord


class VectorRecordMapper:
    def map(
        self,
        *,
        chunks: tuple[Chunk, ...],
        vectors: tuple[tuple[float, ...], ...],
    ) -> tuple[VectorRecord, ...]:
        if len(chunks) != len(vectors):
            raise ValueError("Chunks and vectors must have the same length.")

        return tuple(
            VectorRecord(
                chunk_id=chunk.id,
                vector=vector,
                snapshot_id=chunk.snapshot_id,
                source_file_id=chunk.source_file_id,
                symbol_id=chunk.symbol_id,
                relative_path=chunk.relative_path,
                language=chunk.language,
                qualified_name=chunk.qualified_name,
                symbol_kind=chunk.symbol_kind,
            )
            for chunk, vector in zip(
                chunks,
                vectors,
                strict=True,
            )
        )
