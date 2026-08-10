from codenerva.domain.import_reference import ImportReference
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_store import SymbolStore


class ImportedSymbolResolver:
    def __init__(
        self,
        *,
        source_file_relation_store: SourceFileRelationStore,
        symbol_store: SymbolStore,
    ) -> None:
        self._source_file_relation_store = source_file_relation_store
        self._symbol_store = symbol_store

    def resolve(
        self,
        *,
        import_reference: ImportReference,
        callee_name: str,
    ) -> Symbol | None:
        relations = self._source_file_relation_store.list_by_source_file_id(
            import_reference.source_file_id
        )

        if not relations:
            return None

        for relation in relations:
            target_symbols = self._symbol_store.list_by_source_file_id(
                relation.target_file_id
            )

            matches = [
                symbol for symbol in target_symbols if symbol.name == callee_name
            ]

            if len(matches) == 1:
                return matches[0]

        return None
