from openai import OpenAI

from codenerva.domain.embedding_provider import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        *,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
        client: OpenAI | None = None,
    ) -> None:
        self._model = model
        self._dimensions = dimensions
        self._client = client or OpenAI()

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        if not texts:
            return ()

        response = self._client.embeddings.create(
            model=self._model,
            input=list(texts),
        )

        ordered = sorted(
            response.data,
            key=lambda item: item.index,
        )

        vectors = tuple(
            tuple(float(value) for value in item.embedding) for item in ordered
        )

        for vector in vectors:
            if len(vector) != self._dimensions:
                raise RuntimeError(
                    "Embedding dimension does not match "
                    f"configured dimensions: "
                    f"{len(vector)} != {self._dimensions}"
                )

        return vectors
