from typing import Protocol
from uuid import UUID

from codenerva.domain.symbol_relation import SymbolRelation


class SymbolRelationStore(Protocol):
    def save_many(
        self,
        relations: tuple[SymbolRelation, ...],
    ) -> None: ...

    def list_by_source_symbol_id(
        self,
        source_symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]: ...

    def list_by_target_symbol_id(
        self,
        target_symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]: ...
