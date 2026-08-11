from dataclasses import dataclass

from codenerva.domain.embedding_provider import EmbeddingProvider
from codenerva.domain.vector_search_result import VectorSearchResult
from codenerva.domain.vector_store import VectorStore


@dataclass(frozen=True, slots=True)
class SemanticSearchResult:
    results: tuple[VectorSearchResult, ...]


class SemanticSearchUseCase:
    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def execute(
        self,
        *,
        query: str,
        top_k: int = 5,
    ) -> SemanticSearchResult:
        if not query.strip():
            raise ValueError("query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        vectors = self._embedding_provider.embed((query,))

        query_vector = vectors[0]

        results = self._vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

        return SemanticSearchResult(
            results=results,
        )
