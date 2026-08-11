from codenerva.infrastructure.deterministic_embedding_provider import (
    DeterministicEmbeddingProvider,
)


def test_embedding_is_deterministic() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=8)

    first = provider.embed(("hello",))

    second = provider.embed(("hello",))

    assert first == second
    assert len(first[0]) == 8


def test_different_texts_produce_different_vectors() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=8)

    first, second = provider.embed(
        (
            "hello",
            "world",
        )
    )

    assert first != second
