from dataclasses import dataclass

from codenerva.application.embeddings.vector_record_mapper import (
    VectorRecordMapper,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.embedding_provider import EmbeddingProvider
from codenerva.domain.vector_store import VectorStore


@dataclass(frozen=True, slots=True)
class EmbedChunksResult:
    embedded_chunks: int


class EmbedChunksUseCase:
    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        vector_record_mapper: VectorRecordMapper,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._vector_record_mapper = vector_record_mapper

    def execute(
        self,
        *,
        chunks: tuple[Chunk, ...],
    ) -> EmbedChunksResult:
        if not chunks:
            return EmbedChunksResult(embedded_chunks=0)

        texts = tuple(chunk.text for chunk in chunks)

        vectors = self._embedding_provider.embed(texts)

        records = self._vector_record_mapper.map(
            chunks=chunks,
            vectors=vectors,
        )

        self._vector_store.save_many(records)

        return EmbedChunksResult(embedded_chunks=len(records))
