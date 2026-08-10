from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.graph_repository import GraphRepository
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import SymbolRelationKind


class SymbolNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class TraversalNode:
    symbol: Symbol
    depth: int


@dataclass(frozen=True, slots=True)
class GraphTraversalResult:
    root: Symbol
    nodes: tuple[TraversalNode, ...]


class GraphTraversalService:
    def __init__(
        self,
        *,
        graph_repository: GraphRepository,
    ) -> None:
        self._graph_repository = graph_repository

    def walk_calls(
        self,
        *,
        symbol_id: UUID,
        max_depth: int,
    ) -> GraphTraversalResult:
        if max_depth < 0:
            raise ValueError("max_depth cannot be negative.")

        root = self._graph_repository.get_symbol(symbol_id)

        if root is None:
            raise SymbolNotFoundError(f"Symbol with id {symbol_id} was not found.")

        visited: set[UUID] = {root.id}

        queue: list[tuple[Symbol, int]] = [(root, 0)]

        result: list[TraversalNode] = []

        while queue:
            current, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            relations = self._graph_repository.list_outgoing_relations(current.id)

            for relation in relations:
                if relation.kind is not SymbolRelationKind.CALLS:
                    continue

                target = self._graph_repository.get_symbol(relation.target_symbol_id)

                if target is None:
                    continue

                if target.id in visited:
                    continue

                target_depth = depth + 1

                visited.add(target.id)

                result.append(
                    TraversalNode(
                        symbol=target,
                        depth=target_depth,
                    )
                )

                queue.append(
                    (
                        target,
                        target_depth,
                    )
                )

        return GraphTraversalResult(
            root=root,
            nodes=tuple(result),
        )
