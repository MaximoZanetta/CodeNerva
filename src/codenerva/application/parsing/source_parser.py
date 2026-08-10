from dataclasses import dataclass

from tree_sitter import Tree

from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.domain.programming_language import ProgrammingLanguage


@dataclass(frozen=True, slots=True)
class ParseResult:
    tree: Tree
    has_errors: bool


class SourceParser:
    def __init__(
        self,
        *,
        parser_registry: ParserRegistry,
    ) -> None:
        self._parser_registry = parser_registry

    def parse(
        self,
        *,
        language: ProgrammingLanguage,
        source: bytes,
    ) -> ParseResult:
        parser = self._parser_registry.get(language)

        tree = parser.parse(source)

        return ParseResult(
            tree=tree,
            has_errors=tree.root_node.has_error,
        )
