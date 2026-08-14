from uuid import UUID

from codenerva.application.retrieval.semantic_search import (
    SemanticSearchResult,
)


class FakeSemanticSearchUseCase:
    def __init__(
        self,
        *,
        results_by_query: dict[str, SemanticSearchResult],
    ) -> None:
        self._results_by_query = results_by_query

    def execute(
        self,
        *,
        query: str,
        snapshot_id: UUID,
        top_k: int = 5,
    ) -> SemanticSearchResult:
        del snapshot_id
        del top_k

        result = self._results_by_query.get(query)

        if result is None:
            raise ValueError(f"No fake semantic result configured for query: {query}")

        return result
