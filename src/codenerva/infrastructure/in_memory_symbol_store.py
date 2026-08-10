from uuid import UUID

from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_store import SymbolStore


class InMemorySymbolStore(SymbolStore):
    def __init__(self) -> None:
        self._symbols: dict[UUID, Symbol] = {}

    def save_many(
        self,
        symbols: tuple[Symbol, ...],
    ) -> None:
        for symbol in symbols:
            self._symbols[symbol.id] = symbol

    def get_by_id(
        self,
        symbol_id: UUID,
    ) -> Symbol | None:
        return self._symbols.get(symbol_id)

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[Symbol, ...]:
        symbols = (
            symbol
            for symbol in self._symbols.values()
            if symbol.source_file_id == source_file_id
        )

        return tuple(
            sorted(
                symbols,
                key=lambda symbol: (
                    symbol.start_line,
                    symbol.qualified_name,
                ),
            )
        )
