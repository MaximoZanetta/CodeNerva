from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.snapshots.reuse_unchanged_file import (
    ReuseUnchangedFileUseCase,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)
from codenerva.domain.vector_record import VectorRecord
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
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


def test_reuse_unchanged_file_reuses_symbols_relations_chunks_and_vectors() -> None:
    previous_snapshot_id = uuid4()
    current_snapshot_id = uuid4()

    previous_source_file = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    current_source_file = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    caller = Symbol.create(
        source_file_id=previous_source_file.id,
        name="caller",
        qualified_name="caller",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    callee = Symbol.create(
        source_file_id=previous_source_file.id,
        name="callee",
        qualified_name="callee",
        kind=SymbolKind.FUNCTION,
        start_line=5,
        end_line=7,
    )

    relation = SymbolRelation.create(
        source_symbol_id=caller.id,
        target_symbol_id=callee.id,
        kind=SymbolRelationKind.CALLS,
    )

    caller_chunk = Chunk.create(
        snapshot_id=previous_snapshot_id,
        source_file_id=previous_source_file.id,
        symbol_id=caller.id,
        text=(
            "Language: python\n"
            "File: src/service.py\n"
            "Symbol: caller\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "def caller():\n"
            "    callee()"
        ),
        relative_path="src/service.py",
        language="python",
        qualified_name="caller",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=2,
        code=("def caller():\n    callee()"),
    )

    callee_chunk = Chunk.create(
        snapshot_id=previous_snapshot_id,
        source_file_id=previous_source_file.id,
        symbol_id=callee.id,
        text=(
            "Language: python\n"
            "File: src/service.py\n"
            "Symbol: callee\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "def callee():\n"
            "    return True"
        ),
        relative_path="src/service.py",
        language="python",
        qualified_name="callee",
        symbol_kind="FUNCTION",
        start_line=5,
        end_line=6,
        code=("def callee():\n    return True"),
    )

    caller_vector = VectorRecord(
        chunk_id=caller_chunk.id,
        vector=(0.1, 0.2, 0.3),
        snapshot_id=previous_snapshot_id,
        source_file_id=previous_source_file.id,
        symbol_id=caller.id,
        relative_path="src/service.py",
        language="python",
        qualified_name="caller",
        symbol_kind="FUNCTION",
    )

    callee_vector = VectorRecord(
        chunk_id=callee_chunk.id,
        vector=(0.4, 0.5, 0.6),
        snapshot_id=previous_snapshot_id,
        source_file_id=previous_source_file.id,
        symbol_id=callee.id,
        relative_path="src/service.py",
        language="python",
        qualified_name="callee",
        symbol_kind="FUNCTION",
    )

    symbol_store = InMemorySymbolStore()
    symbol_relation_store = InMemorySymbolRelationStore()
    chunk_store = InMemoryChunkStore()
    vector_store = InMemoryVectorStore()

    symbol_store.save_many(
        (
            caller,
            callee,
        )
    )

    symbol_relation_store.save_many((relation,))

    chunk_store.save_many(
        (
            caller_chunk,
            callee_chunk,
        )
    )

    vector_store.save_many(
        (
            caller_vector,
            callee_vector,
        )
    )

    use_case = ReuseUnchangedFileUseCase(
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )

    result = use_case.execute(
        previous_source_file=previous_source_file,
        current_source_file=current_source_file,
    )

    assert result.reused_symbols == 2
    assert result.reused_symbol_relations == 1
    assert result.reused_chunks == 2
    assert result.reused_vectors == 2

    current_symbols = symbol_store.list_by_source_file_id(current_source_file.id)

    assert len(current_symbols) == 2

    current_by_name = {symbol.name: symbol for symbol in current_symbols}

    current_caller = current_by_name["caller"]
    current_callee = current_by_name["callee"]

    assert current_caller.id != caller.id
    assert current_callee.id != callee.id

    assert current_caller.qualified_name == caller.qualified_name
    assert current_callee.qualified_name == callee.qualified_name

    current_relations = symbol_relation_store.list_by_source_symbol_id(
        current_caller.id
    )

    assert len(current_relations) == 1

    current_relation = current_relations[0]

    assert current_relation.id != relation.id
    assert current_relation.source_symbol_id == current_caller.id
    assert current_relation.target_symbol_id == current_callee.id
    assert current_relation.kind == SymbolRelationKind.CALLS

    current_caller_chunks = chunk_store.list_by_symbol_id(current_caller.id)

    current_callee_chunks = chunk_store.list_by_symbol_id(current_callee.id)

    assert len(current_caller_chunks) == 1
    assert len(current_callee_chunks) == 1

    current_caller_chunk = current_caller_chunks[0]

    current_callee_chunk = current_callee_chunks[0]

    assert current_caller_chunk.id != caller_chunk.id

    assert current_callee_chunk.id != callee_chunk.id

    assert current_caller_chunk.code == caller_chunk.code

    assert current_callee_chunk.code == callee_chunk.code

    current_caller_vector = vector_store.get_by_chunk_id(current_caller_chunk.id)

    current_callee_vector = vector_store.get_by_chunk_id(current_callee_chunk.id)

    assert current_caller_vector is not None
    assert current_callee_vector is not None

    assert current_caller_vector.vector == caller_vector.vector

    assert current_callee_vector.vector == callee_vector.vector

    assert current_caller_vector.snapshot_id == current_snapshot_id

    assert current_callee_vector.snapshot_id == current_snapshot_id

    assert current_caller_vector.source_file_id == current_source_file.id

    assert current_callee_vector.source_file_id == current_source_file.id

    assert current_caller_vector.symbol_id == current_caller.id

    assert current_callee_vector.symbol_id == current_callee.id


def test_reuse_unchanged_file_rejects_modified_file() -> None:
    previous_source_file = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    current_source_file = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    use_case = ReuseUnchangedFileUseCase(
        symbol_store=InMemorySymbolStore(),
        symbol_relation_store=(InMemorySymbolRelationStore()),
        chunk_store=InMemoryChunkStore(),
        vector_store=InMemoryVectorStore(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            previous_source_file=(previous_source_file),
            current_source_file=(current_source_file),
        )
