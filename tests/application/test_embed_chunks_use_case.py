from uuid import uuid4

from codenerva.application.embeddings.embed_chunks import (
    EmbedChunksUseCase,
)
from codenerva.application.embeddings.vector_record_mapper import (
    VectorRecordMapper,
)
from codenerva.domain.chunk import Chunk
from codenerva.infrastructure.deterministic_embedding_provider import (
    DeterministicEmbeddingProvider,
)
from codenerva.infrastructure.in_memory_vector_store import (
    InMemoryVectorStore,
)


def test_embed_chunks() -> None:
    first = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        text="def login(): pass",
        relative_path="auth.py",
        language="python",
        qualified_name="login",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=1,
        code="def login(): pass",
    )

    second = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        text="def logout(): pass",
        relative_path="auth.py",
        language="python",
        qualified_name="logout",
        symbol_kind="FUNCTION",
        start_line=3,
        end_line=3,
        code="def login(): pass",
    )

    vector_store = InMemoryVectorStore()

    use_case = EmbedChunksUseCase(
        embedding_provider=DeterministicEmbeddingProvider(
            dimensions=8,
        ),
        vector_store=vector_store,
        vector_record_mapper=VectorRecordMapper(),
    )

    result = use_case.execute(
        chunks=(
            first,
            second,
        )
    )

    assert result.embedded_chunks == 2

    first_record = vector_store.get_by_chunk_id(first.id)

    second_record = vector_store.get_by_chunk_id(second.id)

    assert first_record is not None
    assert second_record is not None

    assert len(first_record.vector) == 8
    assert len(second_record.vector) == 8

    assert first_record.vector != second_record.vector


def test_embed_chunks_accepts_empty_input() -> None:
    vector_store = InMemoryVectorStore()

    use_case = EmbedChunksUseCase(
        embedding_provider=DeterministicEmbeddingProvider(
            dimensions=8,
        ),
        vector_store=vector_store,
        vector_record_mapper=VectorRecordMapper(),
    )

    result = use_case.execute(chunks=())

    assert result.embedded_chunks == 0
