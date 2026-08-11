from typing import Protocol


class EmbeddingProvider(Protocol):
    @property
    def dimensions(self) -> int: ...

    def embed(
        self,
        texts: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]: ...
