from dataclasses import dataclass

from codenerva.application.graph.graph_query_service import (
    GraphQueryService,
    SymbolNotFoundError,
)
from codenerva.application.retrieval.semantic_search import (
    SemanticSearchUseCase,
)
from codenerva.domain.symbol import Symbol


@dataclass(frozen=True, slots=True)
class HybridSemanticHit:
    symbol: Symbol
    score: float


@dataclass(frozen=True, slots=True)
class HybridExpandedSymbol:
    symbol: Symbol
    relation: str
    source_symbol_id: str
    source_symbol_name: str


@dataclass(frozen=True, slots=True)
class HybridRetrievalResult:
    semantic_hits: tuple[HybridSemanticHit, ...]
    expanded_symbols: tuple[HybridExpandedSymbol, ...]


class HybridRetrievalUseCase:
    def __init__(
        self,
        *,
        semantic_search: SemanticSearchUseCase,
        graph_query_service: GraphQueryService,
    ) -> None:
        self._semantic_search = semantic_search
        self._graph_query_service = graph_query_service

    def execute(
        self,
        *,
        query: str,
        top_k: int = 5,
    ) -> HybridRetrievalResult:
        semantic_result = self._semantic_search.execute(
            query=query,
            top_k=top_k,
        )

        semantic_hits: list[HybridSemanticHit] = []
        expanded_symbols: list[HybridExpandedSymbol] = []

        seen_semantic_symbols: set[str] = set()
        seen_expanded: set[tuple[str, str, str]] = set()

        for item in semantic_result.results:
            symbol_id = item.record.symbol_id

            try:
                neighbors = self._graph_query_service.get_symbol_neighbors(symbol_id)
            except SymbolNotFoundError:
                continue

            symbol_key = str(neighbors.symbol.id)

            if symbol_key not in seen_semantic_symbols:
                semantic_hits.append(
                    HybridSemanticHit(
                        symbol=neighbors.symbol,
                        score=item.score,
                    )
                )
                seen_semantic_symbols.add(symbol_key)

            self._append_neighbors(
                source_symbol=neighbors.symbol,
                relation="CALLS",
                symbols=neighbors.calls,
                target=expanded_symbols,
                seen=seen_expanded,
            )

            self._append_neighbors(
                source_symbol=neighbors.symbol,
                relation="CALLED_BY",
                symbols=neighbors.called_by,
                target=expanded_symbols,
                seen=seen_expanded,
            )

            self._append_neighbors(
                source_symbol=neighbors.symbol,
                relation="CONTAINS",
                symbols=neighbors.contains,
                target=expanded_symbols,
                seen=seen_expanded,
            )

        return HybridRetrievalResult(
            semantic_hits=tuple(semantic_hits),
            expanded_symbols=tuple(expanded_symbols),
        )

    def _append_neighbors(
        self,
        *,
        source_symbol: Symbol,
        relation: str,
        symbols: tuple[Symbol, ...],
        target: list[HybridExpandedSymbol],
        seen: set[tuple[str, str, str]],
    ) -> None:
        for symbol in symbols:
            key = (
                str(source_symbol.id),
                relation,
                str(symbol.id),
            )

            if key in seen:
                continue

            target.append(
                HybridExpandedSymbol(
                    symbol=symbol,
                    relation=relation,
                    source_symbol_id=str(source_symbol.id),
                    source_symbol_name=source_symbol.qualified_name,
                )
            )

            seen.add(key)
