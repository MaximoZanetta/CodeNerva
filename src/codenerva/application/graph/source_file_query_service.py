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
class SourceFileNeighbors:
    source_file: SourceFile
    imports: tuple[SourceFile, ...]
    imported_by: tuple[SourceFile, ...]


class SourceFileQueryService:
    def __init__(
        self,
        *,
        graph_repository: GraphRepository,
    ) -> None:
        self._graph_repository = graph_repository

    def get_source_file_neighbors(
        self,
        source_file_id: UUID,
    ) -> SourceFileNeighbors:
        source_file = self._graph_repository.get_source_file(source_file_id)

        if source_file is None:
            raise SourceFileNotFoundError(
                f"Source file with id {source_file_id} was not found."
            )

        outgoing = self._graph_repository.list_outgoing_file_relations(source_file_id)

        incoming = self._graph_repository.list_incoming_file_relations(source_file_id)

        imports: list[SourceFile] = []
        imported_by: list[SourceFile] = []

        for relation in outgoing:
            if relation.kind is not SourceFileRelationKind.IMPORTS:
                continue

            target = self._graph_repository.get_source_file(relation.target_file_id)

            if target is not None:
                imports.append(target)

        for relation in incoming:
            if relation.kind is not SourceFileRelationKind.IMPORTS:
                continue

            source = self._graph_repository.get_source_file(relation.source_file_id)

            if source is not None:
                imported_by.append(source)

        return SourceFileNeighbors(
            source_file=source_file,
            imports=tuple(imports),
            imported_by=tuple(imported_by),
        )
