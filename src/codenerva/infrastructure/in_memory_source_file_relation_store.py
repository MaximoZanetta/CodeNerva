from uuid import UUID

from codenerva.domain.source_file_relation import SourceFileRelation
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)


class InMemorySourceFileRelationStore(SourceFileRelationStore):
    def __init__(self) -> None:
        self._relations: dict[UUID, SourceFileRelation] = {}

    def save_many(
        self,
        relations: tuple[SourceFileRelation, ...],
    ) -> None:
        for relation in relations:
            self._relations[relation.id] = relation

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]:
        return tuple(
            relation
            for relation in self._relations.values()
            if relation.source_file_id == source_file_id
        )

    def list_by_target_file_id(
        self,
        target_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]:
        return tuple(
            relation
            for relation in self._relations.values()
            if relation.target_file_id == target_file_id
        )

    def delete_by_source_file_ids(
        self,
        source_file_ids: tuple[UUID, ...],
    ) -> int:
        ids = set(source_file_ids)

        relation_ids = [
            relation_id
            for relation_id, relation in self._relations.items()
            if relation.source_file_id in ids or relation.target_file_id in ids
        ]

        for relation_id in relation_ids:
            del self._relations[relation_id]

        return len(relation_ids)
