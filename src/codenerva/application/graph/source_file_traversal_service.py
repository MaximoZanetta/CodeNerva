from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.graph_repository import GraphRepository
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelationKind,
)


class SourceFileNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class FileTraversalNode:
    source_file: SourceFile
    depth: int


@dataclass(frozen=True, slots=True)
class SourceFileTraversalResult:
    root: SourceFile
    nodes: tuple[FileTraversalNode, ...]


class SourceFileTraversalService:
    def __init__(
        self,
        *,
        graph_repository: GraphRepository,
    ) -> None:
        self._graph_repository = graph_repository

    def walk_imports(
        self,
        *,
        source_file_id: UUID,
        max_depth: int,
    ) -> SourceFileTraversalResult:
        if max_depth < 0:
            raise ValueError("max_depth cannot be negative.")

        root = self._graph_repository.get_source_file(source_file_id)

        if root is None:
            raise SourceFileNotFoundError(
                f"Source file with id {source_file_id} was not found."
            )

        visited: set[UUID] = {root.id}

        queue: list[tuple[SourceFile, int]] = [(root, 0)]

        result: list[FileTraversalNode] = []

        while queue:
            current, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            relations = self._graph_repository.list_outgoing_file_relations(current.id)

            for relation in relations:
                if relation.kind is not SourceFileRelationKind.IMPORTS:
                    continue

                target = self._graph_repository.get_source_file(relation.target_file_id)

                if target is None:
                    continue

                if target.id in visited:
                    continue

                target_depth = depth + 1

                visited.add(target.id)

                result.append(
                    FileTraversalNode(
                        source_file=target,
                        depth=target_depth,
                    )
                )

                queue.append(
                    (
                        target,
                        target_depth,
                    )
                )

        return SourceFileTraversalResult(
            root=root,
            nodes=tuple(result),
        )
