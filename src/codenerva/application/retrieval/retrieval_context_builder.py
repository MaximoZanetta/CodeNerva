from dataclasses import dataclass
from uuid import UUID

from codenerva.application.retrieval.hybrid_reranker import HybridRerankResult
from codenerva.domain.chunk import Chunk
from codenerva.domain.chunk_store import ChunkStore


@dataclass(frozen=True, slots=True)
class RetrievalContextItem:
    symbol_id: UUID
    qualified_name: str
    chunk: Chunk
    semantic_score: float | None
    semantic_rank: int | None
    graph_relations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RetrievalContext:
    items: tuple[RetrievalContextItem, ...]


class RetrievalContextBuilder:
    def __init__(
        self,
        *,
        chunk_store: ChunkStore,
    ) -> None:
        self._chunk_store = chunk_store

    def build(
        self,
        *,
        rerank_result: HybridRerankResult,
        max_items: int = 6,
        max_chars: int = 12000,
    ) -> RetrievalContext:
        if max_items < 1:
            raise ValueError("max_items must be greater than zero.")

        if max_chars < 1:
            raise ValueError("max_chars must be greater than zero.")

        items: list[RetrievalContextItem] = []

        for reranked in rerank_result.items:
            chunks = self._chunk_store.list_by_symbol_id(reranked.symbol.id)

            if not chunks:
                continue

            items.append(
                RetrievalContextItem(
                    symbol_id=reranked.symbol.id,
                    qualified_name=(reranked.symbol.qualified_name),
                    chunk=chunks[0],
                    semantic_score=(reranked.semantic_score),
                    semantic_rank=(reranked.semantic_rank),
                    graph_relations=(reranked.graph_relations),
                )
            )

        budgeted_items = self._apply_budget(
            items=tuple(items),
            max_items=max_items,
            max_chars=max_chars,
        )

        return RetrievalContext(
            items=budgeted_items,
        )

    def _describe_relation(
        self,
        *,
        relation: str,
        source_symbol_name: str,
    ) -> str:
        if relation == "CALLS":
            return f"CALLED_BY:{source_symbol_name}"

        if relation == "CALLED_BY":
            return f"CALLS:{source_symbol_name}"

        if relation == "CONTAINS":
            return f"CONTAINED_BY:{source_symbol_name}"

        return f"{relation}:{source_symbol_name}"

    def _apply_budget(
        self,
        *,
        items: tuple[RetrievalContextItem, ...],
        max_items: int,
        max_chars: int,
    ) -> tuple[RetrievalContextItem, ...]:
        selected: list[RetrievalContextItem] = []
        used_chars = 0

        for item in items:
            if len(selected) >= max_items:
                break

            item_size = len(item.chunk.code)

            if used_chars + item_size > max_chars:
                continue

            selected.append(item)
            used_chars += item_size

        return tuple(selected)
