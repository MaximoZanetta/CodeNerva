from pathlib import PurePosixPath
from types import SimpleNamespace
from uuid import UUID, uuid4

from codenerva.application.chunking.symbol_chunker import (
    SymbolChunker,
)
from codenerva.application.parsing.analyze_source_file import (
    AnalyzeSourceFileResult,
)
from codenerva.application.snapshots.build_incremental_index_plan import (
    BuildIncrementalIndexPlanUseCase,
)
from codenerva.application.snapshots.compare_snapshots import (
    CompareSnapshotsUseCase,
)
from codenerva.application.snapshots.incremental_index_snapshot import (
    IncrementalIndexSnapshotUseCase,
)
from codenerva.application.snapshots.reuse_cross_file_relations import (
    ReuseCrossFileRelationsUseCase,
)
from codenerva.application.snapshots.reuse_unchanged_file import (
    ReuseUnchangedFileUseCase,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.programming_language import (
    ProgrammingLanguage,
)
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.vector_record import VectorRecord
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)
from codenerva.infrastructure.in_memory_symbol_relation_store import (
    InMemorySymbolRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)
from codenerva.infrastructure.in_memory_vector_store import (
    InMemoryVectorStore,
)


class FakeAnalyzeSourceFileUseCase:
    def __init__(
        self,
        *,
        source_file_store: InMemorySourceFileStore,
        symbol_store: InMemorySymbolStore,
    ) -> None:
        self._source_file_store = source_file_store
        self._symbol_store = symbol_store

    def execute(
        self,
        *,
        source_file_id: UUID,
    ) -> AnalyzeSourceFileResult:
        source_file = self._source_file_store.get_by_id(source_file_id)

        assert source_file is not None

        symbol = Symbol.create(
            source_file_id=source_file.id,
            name="added_function",
            qualified_name="added_function",
            kind=SymbolKind.FUNCTION,
            start_line=1,
            end_line=2,
        )

        self._symbol_store.save_many((symbol,))

        return AnalyzeSourceFileResult(
            source_file_id=source_file.id,
            symbols=(symbol,),
            has_parse_errors=False,
        )


class FakeEmbedChunksUseCase:
    def __init__(
        self,
        *,
        vector_store: InMemoryVectorStore,
    ) -> None:
        self._vector_store = vector_store

    def execute(
        self,
        *,
        chunks: tuple[Chunk, ...],
    ) -> SimpleNamespace:
        records = tuple(
            VectorRecord(
                chunk_id=chunk.id,
                vector=(0.9, 0.1, 0.0),
                snapshot_id=chunk.snapshot_id,
                source_file_id=chunk.source_file_id,
                symbol_id=chunk.symbol_id,
                relative_path=chunk.relative_path,
                language=chunk.language,
                qualified_name=chunk.qualified_name,
                symbol_kind=chunk.symbol_kind,
            )
            for chunk in chunks
        )

        self._vector_store.save_many(records)

        return SimpleNamespace(embedded_chunks=len(records))


def test_incremental_index_snapshot_reuses_and_indexes_changed_files(
    tmp_path,
) -> None:
    repository_id = uuid4()

    previous_snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    current_snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="b" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    previous_snapshot_id = previous_snapshot.id
    current_snapshot_id = current_snapshot.id

    snapshot_store = InMemorySnapshotStore()
    source_file_store = InMemorySourceFileStore()
    symbol_store = InMemorySymbolStore()
    symbol_relation_store = InMemorySymbolRelationStore()
    source_file_relation_store = InMemorySourceFileRelationStore()
    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    snapshot_store.save(previous_snapshot)
    snapshot_store.save(current_snapshot)

    previous_unchanged = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("src/unchanged.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    current_unchanged = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("src/unchanged.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    deleted = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("src/deleted.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=50,
        content_hash="b" * 64,
    )

    added = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("src/added.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=40,
        content_hash="c" * 64,
    )

    source_file_store.save_many(
        (
            previous_unchanged,
            current_unchanged,
            deleted,
            added,
        )
    )

    previous_symbol = Symbol.create(
        source_file_id=previous_unchanged.id,
        name="process",
        qualified_name="process",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    symbol_store.save_many((previous_symbol,))

    previous_chunk = Chunk.create(
        snapshot_id=previous_snapshot_id,
        source_file_id=previous_unchanged.id,
        symbol_id=previous_symbol.id,
        text=(
            "Language: python\n"
            "File: src/unchanged.py\n"
            "Symbol: process\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "def process():\n"
            "    return True"
        ),
        relative_path="src/unchanged.py",
        language="python",
        qualified_name="process",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=2,
        code=("def process():\n    return True"),
    )

    chunk_store.save_many((previous_chunk,))

    previous_vector = VectorRecord(
        chunk_id=previous_chunk.id,
        vector=(0.1, 0.2, 0.3),
        snapshot_id=previous_snapshot_id,
        source_file_id=previous_unchanged.id,
        symbol_id=previous_symbol.id,
        relative_path="src/unchanged.py",
        language="python",
        qualified_name="process",
        symbol_kind="FUNCTION",
    )

    vector_store.save_many((previous_vector,))

    # IncrementalIndexSnapshotUseCase reads ADDED/MODIFIED files
    # from the repository checkout.
    repository_path = tmp_path / "repositories" / str(repository_id)

    added_path = repository_path / "src" / "added.py"

    added_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    added_path.write_text(
        "def added_function():\n    return 42\n",
        encoding="utf-8",
    )

    compare_snapshots_use_case = CompareSnapshotsUseCase(
        source_file_store=source_file_store,
    )

    build_plan_use_case = BuildIncrementalIndexPlanUseCase()

    reuse_unchanged_file_use_case = ReuseUnchangedFileUseCase(
        symbol_store=symbol_store,
        symbol_relation_store=(symbol_relation_store),
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    reuse_cross_file_relations_use_case = ReuseCrossFileRelationsUseCase(
        symbol_store=symbol_store,
        symbol_relation_store=(symbol_relation_store),
        source_file_relation_store=(source_file_relation_store),
    )

    analyze_source_file_use_case = FakeAnalyzeSourceFileUseCase(
        source_file_store=source_file_store,
        symbol_store=symbol_store,
    )

    embed_chunks_use_case = FakeEmbedChunksUseCase(
        vector_store=vector_store,
    )

    use_case = IncrementalIndexSnapshotUseCase(
        source_file_store=source_file_store,
        compare_snapshots_use_case=(compare_snapshots_use_case),
        build_plan_use_case=(build_plan_use_case),
        reuse_unchanged_file_use_case=(reuse_unchanged_file_use_case),
        reuse_cross_file_relations_use_case=(reuse_cross_file_relations_use_case),
        analyze_source_file_use_case=(analyze_source_file_use_case),
        snapshot_store=snapshot_store,
        symbol_chunker=SymbolChunker(),
        chunk_store=chunk_store,
        embed_chunks_use_case=(embed_chunks_use_case),
        storage_root=tmp_path,
    )

    result = use_case.execute(
        previous_snapshot_id=previous_snapshot_id,
        current_snapshot_id=current_snapshot_id,
    )

    assert result.previous_snapshot_id == previous_snapshot_id

    assert result.current_snapshot_id == current_snapshot_id

    # Snapshot comparison / plan.
    assert result.reused_files == 1
    assert result.analyzed_files == 1
    assert result.skipped_files == 0
    assert result.deleted_files == 1

    # Intelligence reused from unchanged.py.
    assert result.reused_symbols == 1
    assert result.reused_symbol_relations == 0
    assert result.reused_source_file_relations == 0
    assert result.reused_chunks == 1
    assert result.reused_vectors == 1

    # Intelligence generated for added.py.
    assert result.indexed_chunks == 1

    current_unchanged_symbols = symbol_store.list_by_source_file_id(
        current_unchanged.id
    )

    assert len(current_unchanged_symbols) == 1

    current_unchanged_symbol = current_unchanged_symbols[0]

    assert current_unchanged_symbol.id != previous_symbol.id

    assert current_unchanged_symbol.name == "process"

    current_unchanged_chunks = chunk_store.list_by_symbol_id(
        current_unchanged_symbol.id
    )

    assert len(current_unchanged_chunks) == 1

    current_unchanged_chunk = current_unchanged_chunks[0]

    assert current_unchanged_chunk.id != previous_chunk.id

    assert current_unchanged_chunk.code == previous_chunk.code

    reused_vector = vector_store.get_by_chunk_id(current_unchanged_chunk.id)

    assert reused_vector is not None

    assert reused_vector.vector == previous_vector.vector

    assert reused_vector.snapshot_id == current_snapshot_id

    # Verify the ADDED file was actually analyzed.
    added_symbols = symbol_store.list_by_source_file_id(added.id)

    assert len(added_symbols) == 1

    added_symbol = added_symbols[0]

    assert added_symbol.name == ("added_function")

    added_chunks = chunk_store.list_by_symbol_id(added_symbol.id)

    assert len(added_chunks) == 1

    added_chunk = added_chunks[0]

    assert "def added_function()" in added_chunk.code

    added_vector = vector_store.get_by_chunk_id(added_chunk.id)

    assert added_vector is not None

    assert added_vector.snapshot_id == current_snapshot_id

    assert added_vector.source_file_id == added.id

    assert added_vector.symbol_id == added_symbol.id


def test_incremental_index_snapshot_reindexes_modified_file(
    tmp_path,
) -> None:
    repository_id = uuid4()

    previous_snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="c" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    current_snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="d" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    snapshot_store = InMemorySnapshotStore()
    source_file_store = InMemorySourceFileStore()
    symbol_store = InMemorySymbolStore()
    symbol_relation_store = InMemorySymbolRelationStore()
    source_file_relation_store = InMemorySourceFileRelationStore()
    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    snapshot_store.save(previous_snapshot)

    snapshot_store.save(current_snapshot)

    previous_file = SourceFile.create(
        snapshot_id=previous_snapshot.id,
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=30,
        content_hash="a" * 64,
    )

    current_file = SourceFile.create(
        snapshot_id=current_snapshot.id,
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=40,
        content_hash="b" * 64,
    )

    source_file_store.save_many(
        (
            previous_file,
            current_file,
        )
    )

    previous_symbol = Symbol.create(
        source_file_id=previous_file.id,
        name="old_function",
        qualified_name="old_function",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    symbol_store.save_many((previous_symbol,))

    previous_chunk = Chunk.create(
        snapshot_id=previous_snapshot.id,
        source_file_id=previous_file.id,
        symbol_id=previous_symbol.id,
        text=(
            "Language: python\n"
            "File: src/service.py\n"
            "Symbol: old_function\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "def old_function():\n"
            "    return 1"
        ),
        relative_path="src/service.py",
        language="python",
        qualified_name="old_function",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=2,
        code=("def old_function():\n    return 1"),
    )

    chunk_store.save_many((previous_chunk,))

    previous_vector = VectorRecord(
        chunk_id=previous_chunk.id,
        vector=(0.1, 0.2, 0.3),
        snapshot_id=previous_snapshot.id,
        source_file_id=previous_file.id,
        symbol_id=previous_symbol.id,
        relative_path="src/service.py",
        language="python",
        qualified_name="old_function",
        symbol_kind="FUNCTION",
    )

    vector_store.save_many((previous_vector,))

    repository_path = tmp_path / "repositories" / str(repository_id)

    current_path = repository_path / "src" / "service.py"

    current_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    current_path.write_text(
        "def added_function():\n    return 42\n",
        encoding="utf-8",
    )

    use_case = IncrementalIndexSnapshotUseCase(
        source_file_store=source_file_store,
        compare_snapshots_use_case=(
            CompareSnapshotsUseCase(
                source_file_store=source_file_store,
            )
        ),
        build_plan_use_case=(BuildIncrementalIndexPlanUseCase()),
        reuse_unchanged_file_use_case=(
            ReuseUnchangedFileUseCase(
                symbol_store=symbol_store,
                symbol_relation_store=(symbol_relation_store),
                chunk_store=chunk_store,
                vector_store=vector_store,
            )
        ),
        reuse_cross_file_relations_use_case=(
            ReuseCrossFileRelationsUseCase(
                symbol_store=symbol_store,
                symbol_relation_store=(symbol_relation_store),
                source_file_relation_store=(source_file_relation_store),
            )
        ),
        analyze_source_file_use_case=(
            FakeAnalyzeSourceFileUseCase(
                source_file_store=source_file_store,
                symbol_store=symbol_store,
            )
        ),
        snapshot_store=snapshot_store,
        symbol_chunker=SymbolChunker(),
        chunk_store=chunk_store,
        embed_chunks_use_case=(
            FakeEmbedChunksUseCase(
                vector_store=vector_store,
            )
        ),
        storage_root=tmp_path,
    )

    result = use_case.execute(
        previous_snapshot_id=previous_snapshot.id,
        current_snapshot_id=current_snapshot.id,
    )

    assert result.reused_files == 0
    assert result.analyzed_files == 1
    assert result.skipped_files == 0
    assert result.deleted_files == 0

    assert result.reused_symbols == 0
    assert result.reused_chunks == 0
    assert result.reused_vectors == 0

    assert result.indexed_chunks == 1

    current_symbols = symbol_store.list_by_source_file_id(current_file.id)

    assert len(current_symbols) == 1

    current_symbol = current_symbols[0]

    assert current_symbol.id != previous_symbol.id

    current_chunks = chunk_store.list_by_symbol_id(current_symbol.id)

    assert len(current_chunks) == 1

    current_chunk = current_chunks[0]

    current_vector = vector_store.get_by_chunk_id(current_chunk.id)

    assert current_vector is not None

    assert current_vector.snapshot_id == current_snapshot.id

    assert current_vector.source_file_id == current_file.id
