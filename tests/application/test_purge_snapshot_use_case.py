from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.snapshots.purge_snapshot import (
    PurgeSnapshotUseCase,
    SnapshotNotFoundError,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)
from codenerva.domain.vector_record import VectorRecord
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)
from codenerva.infrastructure.in_memory_import_reference_store import (
    InMemoryImportReferenceStore,
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


def test_purge_snapshot_deletes_only_requested_snapshot() -> None:
    repository_id = uuid4()

    snapshot_a = Snapshot.create(
        repository_id=repository_id,
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    snapshot_b = Snapshot.create(
        repository_id=repository_id,
        commit_sha="b" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    snapshot_store = InMemorySnapshotStore()
    source_file_store = InMemorySourceFileStore()
    symbol_store = InMemorySymbolStore()
    symbol_relation_store = InMemorySymbolRelationStore()
    source_file_relation_store = InMemorySourceFileRelationStore()
    import_reference_store = InMemoryImportReferenceStore()
    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    snapshot_store.save(snapshot_a)
    snapshot_store.save(snapshot_b)

    source_file_a = SourceFile.create(
        snapshot_id=snapshot_a.id,
        relative_path=PurePosixPath("src/a.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    source_file_b = SourceFile.create(
        snapshot_id=snapshot_b.id,
        relative_path=PurePosixPath("src/b.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    source_file_store.save_many(
        (
            source_file_a,
            source_file_b,
        )
    )

    symbol_a = Symbol.create(
        source_file_id=source_file_a.id,
        name="function_a",
        qualified_name="function_a",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    symbol_b = Symbol.create(
        source_file_id=source_file_b.id,
        name="function_b",
        qualified_name="function_b",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    symbol_store.save_many(
        (
            symbol_a,
            symbol_b,
        )
    )

    # Internal-ish relation for snapshot A.
    second_symbol_a = Symbol.create(
        source_file_id=source_file_a.id,
        name="helper_a",
        qualified_name="helper_a",
        kind=SymbolKind.FUNCTION,
        start_line=4,
        end_line=5,
    )

    symbol_store.save_many((second_symbol_a,))

    symbol_relation_a = SymbolRelation.create(
        source_symbol_id=symbol_a.id,
        target_symbol_id=second_symbol_a.id,
        kind=SymbolRelationKind.CALLS,
    )

    symbol_relation_store.save_many((symbol_relation_a,))

    import_reference_a = ImportReference.create(
        source_file_id=source_file_a.id,
        module="example.module",
        imported_name="something",
        alias=None,
        line=1,
    )

    import_reference_store.save_many((import_reference_a,))

    # Add another source file in snapshot A so we can test
    # source-file relations too.
    target_source_file_a = SourceFile.create(
        snapshot_id=snapshot_a.id,
        relative_path=PurePosixPath("src/helper.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=50,
        content_hash="c" * 64,
    )

    source_file_store.save_many((target_source_file_a,))

    source_file_relation_a = SourceFileRelation.create(
        source_file_id=source_file_a.id,
        target_file_id=target_source_file_a.id,
        kind=SourceFileRelationKind.IMPORTS,
    )

    source_file_relation_store.save_many((source_file_relation_a,))

    chunk_a = Chunk.create(
        snapshot_id=snapshot_a.id,
        source_file_id=source_file_a.id,
        symbol_id=symbol_a.id,
        text=(
            "Language: python\n"
            "File: src/a.py\n"
            "Symbol: function_a\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "def function_a():\n"
            "    return True"
        ),
        relative_path="src/a.py",
        language="python",
        qualified_name="function_a",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=2,
        code=("def function_a():\n    return True"),
    )

    chunk_b = Chunk.create(
        snapshot_id=snapshot_b.id,
        source_file_id=source_file_b.id,
        symbol_id=symbol_b.id,
        text=(
            "Language: python\n"
            "File: src/b.py\n"
            "Symbol: function_b\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "def function_b():\n"
            "    return False"
        ),
        relative_path="src/b.py",
        language="python",
        qualified_name="function_b",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=2,
        code=("def function_b():\n    return False"),
    )

    chunk_store.save_many(
        (
            chunk_a,
            chunk_b,
        )
    )

    vector_a = VectorRecord(
        chunk_id=chunk_a.id,
        vector=(1.0, 0.0, 0.0),
        snapshot_id=snapshot_a.id,
        source_file_id=source_file_a.id,
        symbol_id=symbol_a.id,
        relative_path="src/a.py",
        language="python",
        qualified_name="function_a",
        symbol_kind="FUNCTION",
    )

    vector_b = VectorRecord(
        chunk_id=chunk_b.id,
        vector=(0.0, 1.0, 0.0),
        snapshot_id=snapshot_b.id,
        source_file_id=source_file_b.id,
        symbol_id=symbol_b.id,
        relative_path="src/b.py",
        language="python",
        qualified_name="function_b",
        symbol_kind="FUNCTION",
    )

    vector_store.save_many(
        (
            vector_a,
            vector_b,
        )
    )

    use_case = PurgeSnapshotUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
        source_file_relation_store=(source_file_relation_store),
        import_reference_store=import_reference_store,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    result = use_case.execute(snapshot_id=snapshot_a.id)

    assert result.snapshot_id == snapshot_a.id

    assert result.deleted_vectors == 1
    assert result.deleted_symbol_relations == 1
    assert result.deleted_source_file_relations == 1
    assert result.deleted_import_references == 1
    assert result.deleted_chunks == 1
    assert result.deleted_symbols == 2
    assert result.deleted_source_files == 2
    assert result.snapshot_deleted is True

    # Snapshot A is gone.
    assert snapshot_store.get_by_id(snapshot_a.id) is None

    assert source_file_store.list_by_snapshot_id(snapshot_a.id) == ()

    assert symbol_store.list_by_source_file_id(source_file_a.id) == ()

    assert chunk_store.get_by_id(chunk_a.id) is None

    assert vector_store.get_by_chunk_id(chunk_a.id) is None

    # Snapshot B must remain untouched.
    assert snapshot_store.get_by_id(snapshot_b.id) == snapshot_b

    assert source_file_store.list_by_snapshot_id(snapshot_b.id) == (source_file_b,)

    assert symbol_store.list_by_source_file_id(source_file_b.id) == (symbol_b,)

    assert chunk_store.get_by_id(chunk_b.id) == chunk_b

    assert vector_store.get_by_chunk_id(chunk_b.id) == vector_b


def test_purge_snapshot_rejects_unknown_snapshot() -> None:
    use_case = PurgeSnapshotUseCase(
        snapshot_store=InMemorySnapshotStore(),
        source_file_store=InMemorySourceFileStore(),
        symbol_store=InMemorySymbolStore(),
        symbol_relation_store=(InMemorySymbolRelationStore()),
        source_file_relation_store=(InMemorySourceFileRelationStore()),
        import_reference_store=(InMemoryImportReferenceStore()),
        chunk_store=InMemoryChunkStore(),
        vector_store=InMemoryVectorStore(),
    )

    unknown_snapshot_id = uuid4()

    try:
        use_case.execute(snapshot_id=unknown_snapshot_id)
    except SnapshotNotFoundError as exc:
        assert str(unknown_snapshot_id) in str(exc)
    else:
        raise AssertionError("Expected SnapshotNotFoundError.")
