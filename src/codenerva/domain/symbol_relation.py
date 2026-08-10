from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid5

SYMBOL_RELATION_NAMESPACE = UUID("cb7bc2cf-7759-4f67-9b9b-827576c19136")


class SymbolRelationKind(StrEnum):
    CONTAINS = "CONTAINS"
    CALLS = "CALLS"


@dataclass(frozen=True, slots=True)
class SymbolRelation:
    id: UUID
    source_symbol_id: UUID
    target_symbol_id: UUID
    kind: SymbolRelationKind

    @classmethod
    def create(
        cls,
        *,
        source_symbol_id: UUID,
        target_symbol_id: UUID,
        kind: SymbolRelationKind,
    ) -> "SymbolRelation":
        if source_symbol_id == target_symbol_id:
            raise ValueError("A symbol cannot have a relation to itself.")

        relation_id = uuid5(
            SYMBOL_RELATION_NAMESPACE,
            (f"{source_symbol_id}:{kind.value}:{target_symbol_id}"),
        )

        return cls(
            id=relation_id,
            source_symbol_id=source_symbol_id,
            target_symbol_id=target_symbol_id,
            kind=kind,
        )
