import os

import pytest

from codenerva.infrastructure.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)


@pytest.mark.skipif(
    os.getenv("RUN_OPENAI_INTEGRATION_TESTS") != "1",
    reason="Set RUN_OPENAI_INTEGRATION_TESTS=1 to run OpenAI integration tests.",
)
def test_openai_embedding_provider() -> None:
    provider = OpenAIEmbeddingProvider()

    vectors = provider.embed(
        (
            "validate user input",
            "render application header",
        )
    )

    assert len(vectors) == 2
    assert len(vectors[0]) == provider.dimensions
    assert len(vectors[1]) == provider.dimensions
    assert vectors[0] != vectors[1]
