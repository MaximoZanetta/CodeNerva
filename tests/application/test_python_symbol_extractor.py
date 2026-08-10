from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.python_symbol_extractor import (
    PythonSymbolExtractor,
)
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.domain.programming_language import ProgrammingLanguage


def test_extract_python_function() -> None:
    source = b"""
def greet(name):
    return name
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.PYTHON,
        source=source,
    )

    extractor = PythonSymbolExtractor()

    symbols = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(symbols) == 1
    assert symbols[0].name == "greet"
    assert symbols[0].kind == "FUNCTION"
    assert symbols[0].parent_name is None


def test_extract_class_and_method() -> None:
    source = b"""
class AuthService:
    def login(self, email):
        return email
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.PYTHON,
        source=source,
    )

    extractor = PythonSymbolExtractor()

    symbols = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(symbols) == 2

    assert symbols[0].name == "AuthService"
    assert symbols[0].kind == "CLASS"
    assert symbols[0].parent_name is None

    assert symbols[1].name == "login"
    assert symbols[1].kind == "METHOD"
    assert symbols[1].parent_name == "AuthService"


def test_nested_function_inside_method_is_not_a_method() -> None:
    source = b"""
class AuthService:
    def login(self):
        def validate():
            return True

        return validate()
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.PYTHON,
        source=source,
    )

    extractor = PythonSymbolExtractor()

    symbols = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(symbols) == 3

    assert symbols[0].name == "AuthService"
    assert symbols[0].kind == "CLASS"

    assert symbols[1].name == "login"
    assert symbols[1].kind == "METHOD"
    assert symbols[1].parent_name == "AuthService"

    assert symbols[2].name == "validate"
    assert symbols[2].kind == "FUNCTION"
