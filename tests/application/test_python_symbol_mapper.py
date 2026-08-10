from uuid import uuid4

from codenerva.application.parsing.python_symbol_extractor import (
    ExtractedSymbol,
)
from codenerva.application.parsing.symbol_mapper import (
    SymbolMapper,
)
from codenerva.domain.symbol import SymbolKind


def test_map_class_and_method_to_symbols() -> None:
    source_file_id = uuid4()

    extracted_symbols = (
        ExtractedSymbol(
            name="AuthService",
            kind="CLASS",
            start_line=1,
            end_line=5,
            parent_name=None,
        ),
        ExtractedSymbol(
            name="login",
            kind="METHOD",
            start_line=2,
            end_line=5,
            parent_name="AuthService",
        ),
    )

    mapper = SymbolMapper()

    symbols = mapper.map(
        source_file_id=source_file_id,
        extracted_symbols=extracted_symbols,
    )

    assert len(symbols) == 2

    class_symbol = symbols[0]
    method_symbol = symbols[1]

    assert class_symbol.kind is SymbolKind.CLASS
    assert class_symbol.qualified_name == "AuthService"

    assert method_symbol.kind is SymbolKind.METHOD
    assert method_symbol.qualified_name == "AuthService.login"
    assert method_symbol.parent_symbol_id == class_symbol.id
