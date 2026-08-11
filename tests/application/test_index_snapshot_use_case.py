from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.chunking.symbol_chunker import (
    SymbolChunker,
)
from codenerva.application.embeddings.embed_chunks import (
    EmbedChunksUseCase,
)
from codenerva.application.embeddings.index_snapshot import (
    IndexSnapshotUseCase,
    SnapshotNotFoundError,
)
from codenerva.application.embeddings.vector_record_mapper import (
    VectorRecordMapper,
)
from codenerva.domain.programming_language import (
    ProgrammingLanguage,
)
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.deterministic_embedding_provider import (
    DeterministicEmbeddingProvider,
)
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)
from codenerva.infrastructure.in_memory_vector_store import (
    InMemoryVectorStore,
)


def test_index_snapshot_indexes_all_analyzed_files(
    tmp_path,
) -> None:
    snapshot_store = InMemorySnapshotStore()
    source_file_store = InMemorySourceFileStore()
    symbol_store = InMemorySymbolStore()
    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    repository_id = uuid4()

    snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    snapshot_store.save(snapshot)

    repository_path = tmp_path / "repositories" / str(repository_id)

    repository_path.mkdir(parents=True)

    first_path = repository_path / "first.py"

    first_path.write_text(
        """
def first():
    return True
""",
        encoding="utf-8",
    )

    second_path = repository_path / "second.py"

    second_path.write_text(
        """
def second():
    return False
""",
        encoding="utf-8",
    )

    first_file = SourceFile.create(
        snapshot_id=snapshot.id,
        relative_path=PurePosixPath("first.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=first_path.stat().st_size,
        content_hash="a" * 64,
    )

    second_file = SourceFile.create(
        snapshot_id=snapshot.id,
        relative_path=PurePosixPath("second.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=second_path.stat().st_size,
        content_hash="b" * 64,
    )

    source_file_store.save_many(
        (
            first_file,
            second_file,
        )
    )

    first_symbol = Symbol.create(
        source_file_id=first_file.id,
        name="first",
        qualified_name="first",
        kind=SymbolKind.FUNCTION,
        start_line=2,
        end_line=3,
    )

    second_symbol = Symbol.create(
        source_file_id=second_file.id,
        name="second",
        qualified_name="second",
        kind=SymbolKind.FUNCTION,
        start_line=2,
        end_line=3,
    )

    symbol_store.save_many(
        (
            first_symbol,
            second_symbol,
        )
    )

    embed_use_case = EmbedChunksUseCase(
        embedding_provider=(
            DeterministicEmbeddingProvider(
                dimensions=8,
            )
        ),
        vector_store=vector_store,
        vector_record_mapper=VectorRecordMapper(),
    )

    use_case = IndexSnapshotUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        chunk_store=chunk_store,
        symbol_chunker=SymbolChunker(),
        embed_chunks_use_case=embed_use_case,
        storage_root=tmp_path,
    )

    result = use_case.execute(snapshot_id=snapshot.id)

    assert result.total_files == 2
    assert result.indexed_files == 2
    assert result.skipped_files == 0
    assert result.indexed_chunks == 2

    first_chunks = chunk_store.list_by_symbol_id(first_symbol.id)

    second_chunks = chunk_store.list_by_symbol_id(second_symbol.id)

    assert len(first_chunks) == 1
    assert len(second_chunks) == 1


def test_index_snapshot_requires_snapshot(
    tmp_path,
) -> None:
    use_case = IndexSnapshotUseCase(
        snapshot_store=InMemorySnapshotStore(),
        source_file_store=InMemorySourceFileStore(),
        symbol_store=InMemorySymbolStore(),
        chunk_store=InMemoryChunkStore(),
        symbol_chunker=SymbolChunker(),
        embed_chunks_use_case=EmbedChunksUseCase(
            embedding_provider=(
                DeterministicEmbeddingProvider(
                    dimensions=8,
                )
            ),
            vector_store=InMemoryVectorStore(),
            vector_record_mapper=VectorRecordMapper(),
        ),
        storage_root=tmp_path,
    )

    with pytest.raises(SnapshotNotFoundError):
        use_case.execute(snapshot_id=uuid4())
