from typing import Protocol

from tree_sitter import Tree

from codenerva.application.parsing.python_symbol_extractor import (
    ExtractedSymbol,
)


class SymbolExtractor(Protocol):
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedSymbol, ...]: ...
