import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_typescript
from tree_sitter import Language, Parser

from codenerva.domain.programming_language import ProgrammingLanguage


class ParserNotAvailableError(Exception):
    pass


class ParserRegistry:
    def __init__(self) -> None:
        self._languages: dict[
            ProgrammingLanguage,
            Language,
        ] = {
            ProgrammingLanguage.PYTHON: Language(tree_sitter_python.language()),
            ProgrammingLanguage.JAVASCRIPT: Language(tree_sitter_javascript.language()),
            ProgrammingLanguage.TYPESCRIPT: Language(
                tree_sitter_typescript.language_typescript()
            ),
            ProgrammingLanguage.TSX: Language(tree_sitter_typescript.language_tsx()),
        }

    def get(
        self,
        language: ProgrammingLanguage,
    ) -> Parser:
        tree_sitter_language = self._languages.get(language)

        if tree_sitter_language is None:
            raise ParserNotAvailableError(
                f"No parser available for language: {language.value}"
            )

        return Parser(tree_sitter_language)
