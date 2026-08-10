from codenerva.application.parsing.javascript_symbol_extractor import (
    JavaScriptSymbolExtractor,
)
from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.domain.programming_language import ProgrammingLanguage


def test_extract_javascript_symbols() -> None:
    source = b"""
class AuthService {
    login(email) {
        return email;
    }
}

function greet(name) {
    return name;
}

const add = (a, b) => {
    return a + b;
};
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.JAVASCRIPT,
        source=source,
    )

    extractor = JavaScriptSymbolExtractor()

    symbols = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(symbols) == 4

    assert symbols[0].name == "AuthService"
    assert symbols[0].kind == "CLASS"

    assert symbols[1].name == "login"
    assert symbols[1].kind == "METHOD"
    assert symbols[1].parent_name == "AuthService"

    assert symbols[2].name == "greet"
    assert symbols[2].kind == "FUNCTION"

    assert symbols[3].name == "add"
    assert symbols[3].kind == "FUNCTION"
