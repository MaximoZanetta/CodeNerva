from uuid import UUID

from codenerva.domain.symbol_relation import SymbolRelation
from codenerva.domain.symbol_relation_store import (
    SymbolRelationStore,
)


class InMemorySymbolRelationStore(SymbolRelationStore):
    def __init__(self) -> None:
        self._relations: dict[UUID, SymbolRelation] = {}

    def save_many(
        self,
        relations: tuple[SymbolRelation, ...],
    ) -> None:
        for relation in relations:
            self._relations[relation.id] = relation

    def list_by_source_symbol_id(
        self,
        source_symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]:
        return tuple(
            relation
            for relation in self._relations.values()
            if relation.source_symbol_id == source_symbol_id
        )

    def list_by_target_symbol_id(
        self,
        target_symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]:
        return tuple(
            relation
            for relation in self._relations.values()
            if relation.target_symbol_id == target_symbol_id
        )
