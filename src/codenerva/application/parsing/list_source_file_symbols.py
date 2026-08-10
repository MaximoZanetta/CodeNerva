from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol import SymbolKind
from codenerva.domain.symbol_store import SymbolStore


class SourceFileNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class SymbolResult:
    id: UUID
    name: str
    qualified_name: str
    kind: SymbolKind
    start_line: int
    end_line: int
    parent_symbol_id: UUID | None


@dataclass(frozen=True, slots=True)
class ListSourceFileSymbolsResult:
    source_file_id: UUID
    symbols: tuple[SymbolResult, ...]


class ListSourceFileSymbolsUseCase:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore,
        symbol_store: SymbolStore,
    ) -> None:
        self._source_file_store = source_file_store
        self._symbol_store = symbol_store

    def execute(
        self,
        source_file_id: UUID,
    ) -> ListSourceFileSymbolsResult:
        source_file = self._source_file_store.get_by_id(source_file_id)

        if source_file is None:
            raise SourceFileNotFoundError(
                f"Source file with id {source_file_id} was not found."
            )

        symbols = self._symbol_store.list_by_source_file_id(source_file_id)

        return ListSourceFileSymbolsResult(
            source_file_id=source_file_id,
            symbols=tuple(
                SymbolResult(
                    id=symbol.id,
                    name=symbol.name,
                    qualified_name=symbol.qualified_name,
                    kind=symbol.kind,
                    start_line=symbol.start_line,
                    end_line=symbol.end_line,
                    parent_symbol_id=symbol.parent_symbol_id,
                )
                for symbol in symbols
            ),
        )
