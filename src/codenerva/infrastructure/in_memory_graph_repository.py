from uuid import UUID

from codenerva.domain.graph_repository import GraphRepository
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import SourceFileRelation
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)
from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import SymbolRelation
from codenerva.domain.symbol_relation_store import SymbolRelationStore
from codenerva.domain.symbol_store import SymbolStore


class InMemoryGraphRepository(GraphRepository):
    def __init__(
        self,
        *,
        symbol_store: SymbolStore,
        symbol_relation_store: SymbolRelationStore,
        source_file_store: SourceFileStore,
        source_file_relation_store: SourceFileRelationStore,
    ) -> None:
        self._symbol_store = symbol_store
        self._symbol_relation_store = symbol_relation_store
        self._source_file_store = source_file_store
        self._source_file_relation_store = source_file_relation_store

    def get_symbol(
        self,
        symbol_id: UUID,
    ) -> Symbol | None:
        return self._symbol_store.get_by_id(symbol_id)

    def list_outgoing_relations(
        self,
        symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]:
        return self._symbol_relation_store.list_by_source_symbol_id(symbol_id)

    def list_incoming_relations(
        self,
        symbol_id: UUID,
    ) -> tuple[SymbolRelation, ...]:
        return self._symbol_relation_store.list_by_target_symbol_id(symbol_id)

    def get_source_file(
        self,
        source_file_id: UUID,
    ) -> SourceFile | None:
        return self._source_file_store.get_by_id(source_file_id)

    def list_outgoing_file_relations(
        self,
        source_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]:
        return self._source_file_relation_store.list_by_source_file_id(source_file_id)

    def list_incoming_file_relations(
        self,
        source_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]:
        return self._source_file_relation_store.list_by_target_file_id(source_file_id)
