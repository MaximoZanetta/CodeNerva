from dataclasses import dataclass
from uuid import UUID

from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalResult,
)
from codenerva.domain.symbol import Symbol


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
    def rerank(
        self,
        *,
        retrieval_result: HybridRetrievalResult,
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
                source_symbol_name=expanded.source_symbol_name,
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

                items[expanded.symbol.id] = RerankedSymbol(
                    symbol=existing.symbol,
                    semantic_score=existing.semantic_score,
                    semantic_rank=existing.semantic_rank,
                    graph_relations=relations,
                    final_score=(existing.final_score + graph_bonus),
                )

                continue

            items[expanded.symbol.id] = RerankedSymbol(
                symbol=expanded.symbol,
                semantic_score=None,
                semantic_rank=None,
                graph_relations=(relation,),
                final_score=graph_bonus,
            )

        ordered = sorted(
            items.values(),
            key=lambda item: item.final_score,
            reverse=True,
        )

        return HybridRerankResult(items=tuple(ordered))

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
