import re
from dataclasses import dataclass
from uuid import UUID

from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalResult,
)
from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol import Symbol, SymbolKind


@dataclass(frozen=True, slots=True)
class RerankedSymbol:
    symbol: Symbol
    semantic_score: float | None
    semantic_rank: int | None
    graph_relations: tuple[str, ...]
    final_score: float


@dataclass(frozen=True, slots=True)
class HybridRerankResult:
    items: tuple[RerankedSymbol, ...]


class HybridReranker:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore | None = None,
        test_penalty: float = 0.12,
    ) -> None:
        self._source_file_store = source_file_store
        self._test_penalty = test_penalty

    def rerank(
        self,
        *,
        retrieval_result: HybridRetrievalResult,
        question: str = "",
    ) -> HybridRerankResult:
        items: dict[UUID, RerankedSymbol] = {}

        semantic_scores: dict[UUID, float] = {}

        for rank, hit in enumerate(
            retrieval_result.semantic_hits,
            start=1,
        ):
            semantic_scores[hit.symbol.id] = hit.score

            items[hit.symbol.id] = RerankedSymbol(
                symbol=hit.symbol,
                semantic_score=hit.score,
                semantic_rank=rank,
                graph_relations=(),
                final_score=hit.score,
            )

        for expanded in retrieval_result.expanded_symbols:
            source_score = semantic_scores.get(
                UUID(expanded.source_symbol_id),
                0.0,
            )

            relation = self._describe_relation(
                relation=expanded.relation,
                source_symbol_name=(expanded.source_symbol_name),
            )

            graph_bonus = self._graph_bonus(
                relation=expanded.relation,
                source_score=source_score,
            )

            existing = items.get(expanded.symbol.id)

            if existing is not None:
                relations = tuple(
                    dict.fromkeys(
                        (
                            *existing.graph_relations,
                            relation,
                        )
                    )
                )
                multi_relation_bonus = 0.0

                if len(relations) > 1:
                    multi_relation_bonus = 0.05 * (len(relations) - 1)

                items[expanded.symbol.id] = RerankedSymbol(
                    symbol=existing.symbol,
                    semantic_score=(existing.semantic_score),
                    semantic_rank=(existing.semantic_rank),
                    graph_relations=relations,
                    final_score=(
                        existing.final_score + graph_bonus + multi_relation_bonus
                    ),
                )

                continue

            items[expanded.symbol.id] = RerankedSymbol(
                symbol=expanded.symbol,
                semantic_score=None,
                semantic_rank=None,
                graph_relations=(relation,),
                final_score=graph_bonus,
            )

        adjusted_items = tuple(
            self._apply_contextual_adjustments(
                item=item,
                question=question,
            )
            for item in items.values()
        )

        ordered = sorted(
            adjusted_items,
            key=lambda item: item.final_score,
            reverse=True,
        )

        return HybridRerankResult(items=tuple(ordered))

    def _apply_contextual_adjustments(
        self,
        *,
        item: RerankedSymbol,
        question: str,
    ) -> RerankedSymbol:
        final_score = item.final_score

        if self._is_test_symbol(item.symbol) and not self._is_testing_question(
            question
        ):
            final_score -= self._test_penalty

        if self._is_behavioral_question(question) and item.symbol.kind in {
            SymbolKind.FUNCTION,
            SymbolKind.METHOD,
        }:
            final_score += 0.05

        return RerankedSymbol(
            symbol=item.symbol,
            semantic_score=item.semantic_score,
            semantic_rank=item.semantic_rank,
            graph_relations=item.graph_relations,
            final_score=final_score,
        )

    def _is_test_symbol(
        self,
        symbol: Symbol,
    ) -> bool:
        if self._source_file_store is None:
            return False

        source_file = self._source_file_store.get_by_id(symbol.source_file_id)

        if source_file is None:
            return False

        # path = (
        #     source_file.relative_path
        #     .as_posix()
        #     .lower()
        # )

        filename = source_file.relative_path.name.lower()

        path_parts = {part.lower() for part in source_file.relative_path.parts}

        if "test" in path_parts or "tests" in path_parts or "__tests__" in path_parts:
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
            "testing",
            "tested",
            "pytest",
            "unittest",
            "coverage",
            "fixture",
            "fixtures",
            "mock",
            "mocks",
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

    def _is_behavioral_question(
        self,
        question: str,
    ) -> bool:
        normalized = question.lower()

        behavioral_terms = {
            "how",
            "flow",
            "flows",
            "work",
            "works",
            "working",
            "call",
            "calls",
            "called",
            "request",
            "requests",
            "process",
            "processes",
            "execute",
            "executes",
            "execution",
            "handle",
            "handles",
            "handled",
            "trace",
            "traces",
        }

        words = set(
            re.findall(
                r"[a-z0-9_]+",
                normalized,
            )
        )

        return bool(words & behavioral_terms)

    def _graph_bonus(
        self,
        *,
        relation: str,
        source_score: float,
    ) -> float:
        if relation in {
            "CALLS",
            "CALLED_BY",
        }:
            return 0.15 + (source_score * 0.20)

        if relation == "CONTAINS":
            return 0.08 + (source_score * 0.10)

        return 0.05

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
