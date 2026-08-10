from typing import Protocol
from uuid import UUID

from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import SourceFileRelation
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import SymbolRelation


class GraphRepository(Protocol):
    # ---------- Symbols ----------

    def get_symbol(
        self,
        symbol_id: UUID,
    ) -> Symbol | None: ...

    def list_outgoing_relations(
        self,
        symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]: ...

    def list_incoming_relations(
        self,
        symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]: ...

    # ---------- Files ----------

    def get_source_file(
        self,
        source_file_id: UUID,
    ) -> SourceFile | None: ...

    def list_outgoing_file_relations(
        self,
        source_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]: ...

    def list_incoming_file_relations(
        self,
        source_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]: ...
