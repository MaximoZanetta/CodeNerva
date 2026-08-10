from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.graph_repository import GraphRepository
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import SymbolRelationKind


class SymbolNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class SymbolNeighbors:
    symbol: Symbol
    contains: tuple[Symbol, ...]
    calls: tuple[Symbol, ...]
    called_by: tuple[Symbol, ...]


class GraphQueryService:
    def __init__(
        self,
        *,
        graph_repository: GraphRepository,
    ) -> None:
        self._graph_repository = graph_repository

    def get_symbol_neighbors(
        self,
        symbol_id: UUID,
    ) -> SymbolNeighbors:
        symbol = self._graph_repository.get_symbol(symbol_id)

        if symbol is None:
            raise SymbolNotFoundError(f"Symbol with id {symbol_id} was not found.")

        outgoing = self._graph_repository.list_outgoing_relations(symbol_id)

        incoming = self._graph_repository.list_incoming_relations(symbol_id)

        contains: list[Symbol] = []
        calls: list[Symbol] = []
        called_by: list[Symbol] = []

        for relation in outgoing:
            target = self._graph_repository.get_symbol(relation.target_symbol_id)

            if target is None:
                continue

            if relation.kind is SymbolRelationKind.CONTAINS:
                contains.append(target)

            elif relation.kind is SymbolRelationKind.CALLS:
                calls.append(target)

        for relation in incoming:
            if relation.kind is not SymbolRelationKind.CALLS:
                continue

            source = self._graph_repository.get_symbol(relation.source_symbol_id)

            if source is not None:
                called_by.append(source)

        return SymbolNeighbors(
            symbol=symbol,
            contains=tuple(contains),
            calls=tuple(calls),
            called_by=tuple(called_by),
        )
