from typing import Protocol

from tree_sitter import Tree

from codenerva.application.parsing.python_call_extractor import ExtractedCall


class CallExtractor(Protocol):
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedCall, ...]: ...
