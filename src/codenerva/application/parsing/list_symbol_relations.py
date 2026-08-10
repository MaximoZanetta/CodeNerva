from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol_relation import SymbolRelationKind
from codenerva.domain.symbol_relation_store import SymbolRelationStore
from codenerva.domain.symbol_store import SymbolStore


class SourceFileNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class SymbolRelationResult:
    id: UUID
    kind: SymbolRelationKind
    source_symbol_id: UUID
    source_symbol_name: str
    target_symbol_id: UUID
    target_symbol_name: str


@dataclass(frozen=True, slots=True)
class ListSymbolRelationsResult:
    source_file_id: UUID
    relations: tuple[SymbolRelationResult, ...]


class ListSymbolRelationsUseCase:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore,
        symbol_store: SymbolStore,
        symbol_relation_store: SymbolRelationStore,
    ) -> None:
        self._source_file_store = source_file_store
        self._symbol_store = symbol_store
        self._symbol_relation_store = symbol_relation_store

    def execute(
        self,
        source_file_id: UUID,
    ) -> ListSymbolRelationsResult:
        source_file = self._source_file_store.get_by_id(source_file_id)

        if source_file is None:
            raise SourceFileNotFoundError(
                f"Source file with id {source_file_id} was not found."
            )

        symbols = self._symbol_store.list_by_source_file_id(source_file_id)

        symbol_by_id = {symbol.id: symbol for symbol in symbols}

        results: list[SymbolRelationResult] = []

        for symbol in symbols:
            relations = self._symbol_relation_store.list_by_source_symbol_id(symbol.id)

            for relation in relations:
                target_symbol = symbol_by_id.get(relation.target_symbol_id)

                if target_symbol is None:
                    continue

                results.append(
                    SymbolRelationResult(
                        id=relation.id,
                        kind=relation.kind,
                        source_symbol_id=symbol.id,
                        source_symbol_name=symbol.qualified_name,
                        target_symbol_id=target_symbol.id,
                        target_symbol_name=target_symbol.qualified_name,
                    )
                )

        return ListSymbolRelationsResult(
            source_file_id=source_file_id,
            relations=tuple(results),
        )
