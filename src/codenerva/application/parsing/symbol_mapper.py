from uuid import UUID

from codenerva.application.parsing.python_symbol_extractor import (
    ExtractedSymbol,
)
from codenerva.domain.symbol import Symbol, SymbolKind


class SymbolMapper:
    def map(
        self,
        *,
        source_file_id: UUID,
        extracted_symbols: tuple[ExtractedSymbol, ...],
    ) -> tuple[Symbol, ...]:
        symbols: list[Symbol] = []
        symbol_by_qualified_name: dict[str, Symbol] = {}

        for index, extracted in enumerate(extracted_symbols):
            qualified_name = (
                f"{extracted.parent_name}.{extracted.name}"
                if extracted.parent_name
                else extracted.name
            )

            kind = SymbolKind(extracted.kind)

            parent_symbol_id = None

            if extracted.parent_name is not None:
                parent = symbol_by_qualified_name.get(extracted.parent_name)

                if parent is not None:
                    parent_symbol_id = parent.id

            symbol = Symbol.create(
                source_file_id=source_file_id,
                name=extracted.name,
                qualified_name=qualified_name,
                kind=kind,
                start_line=extracted.start_line,
                end_line=extracted.end_line,
                parent_symbol_id=parent_symbol_id,
            )

            symbols.append(symbol)
            symbol_by_qualified_name[qualified_name] = symbol

        return tuple(symbols)
