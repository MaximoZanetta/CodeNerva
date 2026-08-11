from uuid import uuid4

from codenerva.domain.vector_record import VectorRecord
from codenerva.infrastructure.in_memory_vector_store import (
    InMemoryVectorStore,
)


def test_save_and_get_vector_record() -> None:
    chunk_id = uuid4()

    record = VectorRecord(
        chunk_id=chunk_id,
        vector=(0.1, 0.2, 0.3),
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="auth.py",
        language="python",
        qualified_name="login",
        symbol_kind="FUNCTION",
    )

    store = InMemoryVectorStore()

    store.save_many((record,))

    result = store.get_by_chunk_id(chunk_id)

    assert result == record


def test_search_returns_most_similar_vector() -> None:
    store = InMemoryVectorStore()

    best = VectorRecord(
        chunk_id=uuid4(),
        vector=(1.0, 0.0),
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="best.py",
        language="python",
        qualified_name="best",
        symbol_kind="FUNCTION",
    )

    middle = VectorRecord(
        chunk_id=uuid4(),
        vector=(0.7, 0.7),
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="middle.py",
        language="python",
        qualified_name="middle",
        symbol_kind="FUNCTION",
    )

    worst = VectorRecord(
        chunk_id=uuid4(),
        vector=(-1.0, 0.0),
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="worst.py",
        language="python",
        qualified_name="worst",
        symbol_kind="FUNCTION",
    )

    store.save_many(
        (
            best,
            middle,
            worst,
        )
    )

    results = store.search(
        query_vector=(1.0, 0.0),
        top_k=2,
    )

    assert len(results) == 2

    assert results[0].record.chunk_id == best.chunk_id
    assert results[0].score == 1.0

    assert results[1].record.chunk_id == middle.chunk_id


def test_search_respects_top_k() -> None:
    store = InMemoryVectorStore()

    records = tuple(
        VectorRecord(
            chunk_id=uuid4(),
            vector=(1.0, float(index + 1)),
            snapshot_id=uuid4(),
            source_file_id=uuid4(),
            symbol_id=uuid4(),
            relative_path=f"{index}.py",
            language="python",
            qualified_name=f"symbol_{index}",
            symbol_kind="FUNCTION",
        )
        for index in range(5)
    )

    store.save_many(records)

    results = store.search(
        query_vector=(1.0, 0.0),
        top_k=3,
    )

    assert len(results) == 3
