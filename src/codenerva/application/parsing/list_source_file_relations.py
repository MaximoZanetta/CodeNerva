from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.source_file_relation import SourceFileRelationKind
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)
from codenerva.domain.source_file_store import SourceFileStore


class SourceFileNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class SourceFileRelationResult:
    id: UUID
    kind: SourceFileRelationKind
    target_source_file_id: UUID
    target_relative_path: str


@dataclass(frozen=True, slots=True)
class ListSourceFileRelationsResult:
    source_file_id: UUID
    relations: tuple[SourceFileRelationResult, ...]


class ListSourceFileRelationsUseCase:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore,
        source_file_relation_store: SourceFileRelationStore,
    ) -> None:
        self._source_file_store = source_file_store
        self._source_file_relation_store = source_file_relation_store

    def execute(
        self,
        source_file_id: UUID,
    ) -> ListSourceFileRelationsResult:
        source_file = self._source_file_store.get_by_id(source_file_id)

        if source_file is None:
            raise SourceFileNotFoundError(
                f"Source file with id {source_file_id} was not found."
            )

        relations = self._source_file_relation_store.list_by_source_file_id(
            source_file_id
        )

        results: list[SourceFileRelationResult] = []

        for relation in relations:
            target_file = self._source_file_store.get_by_id(relation.target_file_id)

            if target_file is None:
                continue

            results.append(
                SourceFileRelationResult(
                    id=relation.id,
                    kind=relation.kind,
                    target_source_file_id=target_file.id,
                    target_relative_path=str(target_file.relative_path),
                )
            )

        return ListSourceFileRelationsResult(
            source_file_id=source_file_id,
            relations=tuple(results),
        )
