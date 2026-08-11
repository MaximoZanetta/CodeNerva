import hashlib

from codenerva.domain.embedding_provider import EmbeddingProvider


class DeterministicEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        *,
        dimensions: int = 8,
    ) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive.")

        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        return tuple(self._embed_text(text) for text in texts)

    def _embed_text(
        self,
        text: str,
    ) -> tuple[float, ...]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()

        values: list[float] = []

        for index in range(self._dimensions):
            byte = digest[index % len(digest)]

            value = (byte / 255.0) * 2.0 - 1.0

            values.append(value)

        return tuple(values)
