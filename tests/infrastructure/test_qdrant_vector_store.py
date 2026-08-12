from uuid import uuid4

from qdrant_client import QdrantClient

from codenerva.domain.vector_record import (
    VectorRecord,
)
from codenerva.infrastructure.qdrant_vector_store import (
    QdrantVectorStore,
)


def test_qdrant_vector_store_save_get_and_search(
    tmp_path,
) -> None:
    client = QdrantClient(path=str(tmp_path / "qdrant"))
    snapshot_id = uuid4()
    store = QdrantVectorStore(
        client=client,
        collection_name="test_vectors",
        dimensions=3,
    )

    best = VectorRecord(
        chunk_id=uuid4(),
        vector=(1.0, 0.0, 0.0),
        snapshot_id=snapshot_id,
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="best.py",
        language="python",
        qualified_name="best",
        symbol_kind="FUNCTION",
    )

    second = VectorRecord(
        chunk_id=uuid4(),
        vector=(0.7, 0.7, 0.0),
        snapshot_id=snapshot_id,
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="second.py",
        language="python",
        qualified_name="second",
        symbol_kind="FUNCTION",
    )

    store.save_many(
        (
            best,
            second,
        )
    )

    retrieved = store.get_by_chunk_id(best.chunk_id)

    assert retrieved is not None
    assert retrieved.chunk_id == best.chunk_id
    assert retrieved.symbol_id == best.symbol_id

    results = store.search(
        snapshot_id=best.snapshot_id,
        query_vector=(1.0, 0.0, 0.0),
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].record.chunk_id == best.chunk_id


def test_delete_by_snapshot_id() -> None:
    client = QdrantClient(":memory:")

    store = QdrantVectorStore(
        client=client,
        collection_name="test_chunks",
        dimensions=3,
    )

    first_snapshot_id = uuid4()
    second_snapshot_id = uuid4()

    first = VectorRecord(
        chunk_id=uuid4(),
        vector=(1.0, 0.0, 0.0),
        snapshot_id=first_snapshot_id,
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="first.py",
        language="python",
        qualified_name="first",
        symbol_kind="FUNCTION",
    )

    second = VectorRecord(
        chunk_id=uuid4(),
        vector=(0.0, 1.0, 0.0),
        snapshot_id=second_snapshot_id,
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        relative_path="second.py",
        language="python",
        qualified_name="second",
        symbol_kind="FUNCTION",
    )

    store.save_many(
        (
            first,
            second,
        )
    )

    deleted = store.delete_by_snapshot_id(first_snapshot_id)

    assert deleted == 1

    assert store.get_by_chunk_id(first.chunk_id) is None

    assert store.get_by_chunk_id(second.chunk_id) is not None
