from codenerva.application.parsing.javascript_symbol_extractor import (
    JavaScriptSymbolExtractor,
)
from codenerva.application.parsing.python_symbol_extractor import (
    PythonSymbolExtractor,
)
from codenerva.application.parsing.symbol_extractor import SymbolExtractor
from codenerva.application.parsing.typescript_symbol_extractor import (
    TypeScriptSymbolExtractor,
)
from codenerva.domain.programming_language import ProgrammingLanguage


class SymbolExtractorNotAvailableError(Exception):
    pass


class SymbolExtractorRegistry:
    def __init__(self) -> None:
        javascript_extractor = JavaScriptSymbolExtractor()
        typescript_extractor = TypeScriptSymbolExtractor()

        self._extractors: dict[
            ProgrammingLanguage,
            SymbolExtractor,
        ] = {
            ProgrammingLanguage.PYTHON: PythonSymbolExtractor(),
            ProgrammingLanguage.JAVASCRIPT: javascript_extractor,
            ProgrammingLanguage.TYPESCRIPT: typescript_extractor,
            ProgrammingLanguage.TSX: typescript_extractor,
        }

    def get(
        self,
        language: ProgrammingLanguage,
    ) -> SymbolExtractor:
        extractor = self._extractors.get(language)

        if extractor is None:
            raise SymbolExtractorNotAvailableError(
                f"No symbol extractor available for {language.value}."
            )

        return extractor
