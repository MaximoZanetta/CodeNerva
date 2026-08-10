from typing import Protocol
from uuid import UUID

from codenerva.domain.symbol import Symbol


class SymbolStore(Protocol):
    def save_many(
        self,
        symbols: tuple[Symbol, ...],
    ) -> None: ...

    def get_by_id(
        self,
        symbol_id: UUID,
    ) -> Symbol | None: ...

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[Symbol, ...]: ...
