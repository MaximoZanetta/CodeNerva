from uuid import uuid4

import pytest

from codenerva.application.retrieval.semantic_search import (
    SemanticSearchUseCase,
)
from codenerva.domain.vector_record import VectorRecord
from codenerva.infrastructure.deterministic_embedding_provider import (
    DeterministicEmbeddingProvider,
)
from codenerva.infrastructure.in_memory_vector_store import (
    InMemoryVectorStore,
)


def test_semantic_search_returns_results() -> None:
    embedding_provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    vector_store = InMemoryVectorStore()

    texts = (
        "validate user input",
        "send message",
        "render header",
    )
    snapshot_id = uuid4()
    vectors = embedding_provider.embed(texts)

    records = tuple(
        VectorRecord(
            chunk_id=uuid4(),
            vector=vector,
            snapshot_id=snapshot_id,
            source_file_id=uuid4(),
            symbol_id=uuid4(),
            relative_path=f"{index}.js",
            language="javascript",
            qualified_name=text.replace(" ", "_"),
            symbol_kind="FUNCTION",
        )
        for index, (text, vector) in enumerate(
            zip(
                texts,
                vectors,
                strict=True,
            )
        )
    )

    vector_store.save_many(records)

    use_case = SemanticSearchUseCase(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    result = use_case.execute(
        query="validate user input",
        snapshot_id=snapshot_id,
        top_k=2,
    )

    assert len(result.results) == 2

    assert result.results[0].record.qualified_name == "validate_user_input"

    assert result.results[0].score == pytest.approx(1.0)


def test_semantic_search_rejects_empty_query() -> None:
    use_case = SemanticSearchUseCase(
        embedding_provider=(
            DeterministicEmbeddingProvider(
                dimensions=8,
            )
        ),
        vector_store=InMemoryVectorStore(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            snapshot_id=uuid4(),
            query="   ",
        )


def test_semantic_search_rejects_invalid_top_k() -> None:
    use_case = SemanticSearchUseCase(
        embedding_provider=(
            DeterministicEmbeddingProvider(
                dimensions=8,
            )
        ),
        vector_store=InMemoryVectorStore(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            snapshot_id=uuid4(),
            query="login",
            top_k=0,
        )
