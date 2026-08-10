from typing import Protocol

from tree_sitter import Tree

from codenerva.application.parsing.python_import_extractor import (
    ExtractedImport,
)


class ImportExtractor(Protocol):
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedImport, ...]: ...
