import re
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from codenerva.application.retrieval.hybrid_reranker import (
    HybridRerankResult,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.chunk_store import ChunkStore


class RetrievalOrigin(StrEnum):
    SEMANTIC = "SEMANTIC"
    GRAPH = "GRAPH"
    BOTH = "BOTH"


@dataclass(frozen=True, slots=True)
class RetrievalContextItem:
    symbol_id: UUID
    qualified_name: str
    chunk: Chunk
    semantic_score: float | None
    semantic_rank: int | None
    graph_relations: tuple[str, ...]
    retrieval_origin: RetrievalOrigin
    final_score: float


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
        question: str = "",
        max_items: int = 6,
        max_chars: int = 12000,
        minimum_final_score: float = 0.20,
    ) -> RetrievalContext:
        if max_items < 1:
            raise ValueError("max_items must be greater than zero.")

        if max_chars < 1:
            raise ValueError("max_chars must be greater than zero.")

        if minimum_final_score < 0:
            raise ValueError("minimum_final_score cannot be negative.")

        items: list[RetrievalContextItem] = []

        for reranked in rerank_result.items:
            if reranked.final_score < minimum_final_score:
                continue

            chunks = self._chunk_store.list_by_symbol_id(reranked.symbol.id)

            if not chunks:
                continue

            retrieval_origin = self._get_retrieval_origin(
                semantic_score=reranked.semantic_score,
                semantic_rank=reranked.semantic_rank,
                graph_relations=reranked.graph_relations,
            )

            items.append(
                RetrievalContextItem(
                    symbol_id=reranked.symbol.id,
                    qualified_name=(reranked.symbol.qualified_name),
                    chunk=chunks[0],
                    semantic_score=(reranked.semantic_score),
                    semantic_rank=(reranked.semantic_rank),
                    graph_relations=(reranked.graph_relations),
                    retrieval_origin=retrieval_origin,
                    final_score=reranked.final_score,
                )
            )

        budgeted_items = self._apply_budget(
            items=tuple(items),
            question=question,
            max_items=max_items,
            max_chars=max_chars,
        )

        return RetrievalContext(
            items=budgeted_items,
        )

    def _get_retrieval_origin(
        self,
        *,
        semantic_score: float | None,
        semantic_rank: int | None,
        graph_relations: tuple[str, ...],
    ) -> RetrievalOrigin:
        has_semantic = semantic_score is not None or semantic_rank is not None

        has_graph = bool(graph_relations)

        if has_semantic and has_graph:
            return RetrievalOrigin.BOTH

        if has_graph:
            return RetrievalOrigin.GRAPH

        return RetrievalOrigin.SEMANTIC

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
        question: str,
        max_items: int,
        max_chars: int,
    ) -> tuple[RetrievalContextItem, ...]:
        if self._is_testing_question(question):
            return self._select_with_budget(
                items=items,
                max_items=max_items,
                max_chars=max_chars,
            )

        production_items = tuple(item for item in items if not self._is_test_item(item))

        return self._select_with_budget(
            items=production_items,
            max_items=max_items,
            max_chars=max_chars,
        )

    def _select_with_budget(
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

    def _is_test_item(
        self,
        item: RetrievalContextItem,
    ) -> bool:
        path = item.chunk.relative_path.lower()

        parts = {
            part.lower()
            for part in path.replace(
                "\\",
                "/",
            ).split("/")
        }

        filename = path.replace(
            "\\",
            "/",
        ).split("/")[-1]

        if {
            "test",
            "tests",
            "__tests__",
        } & parts:
            return True

        return (
            filename.startswith("test_")
            or filename.endswith("_test.py")
            or ".test." in filename
            or ".spec." in filename
        )

    def _is_testing_question(
        self,
        question: str,
    ) -> bool:
        normalized = question.lower()

        testing_terms = {
            "test",
            "tests",
            "tested",
            "testing",
            "pytest",
            "unittest",
            "coverage",
            "fixture",
            "fixtures",
            "mock",
            "mocks",
            "mocked",
            "mocking",
            "spec",
            "specs",
        }

        words = set(
            re.findall(
                r"[a-z0-9_]+",
                normalized,
            )
        )

        return bool(words & testing_terms)
