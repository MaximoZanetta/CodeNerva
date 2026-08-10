from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.domain.programming_language import ProgrammingLanguage


def test_parse_python_source() -> None:
    source = b"""
def greet(name):
    return name
"""

    source_parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    result = source_parser.parse(
        language=ProgrammingLanguage.PYTHON,
        source=source,
    )

    assert result.tree.root_node.type == "module"
    assert result.has_errors is False


def test_parse_python_function_definition() -> None:
    source = b"""
def greet(name):
    return name
"""

    source_parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    result = source_parser.parse(
        language=ProgrammingLanguage.PYTHON,
        source=source,
    )

    root = result.tree.root_node

    function_node = next(
        child for child in root.children if child.type == "function_definition"
    )

    assert function_node.type == "function_definition"


def test_parse_javascript_source() -> None:
    source = b"""
function greet(name) {
    return name;
}
"""

    source_parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    result = source_parser.parse(
        language=ProgrammingLanguage.JAVASCRIPT,
        source=source,
    )

    assert result.tree.root_node.type == "program"
    assert result.has_errors is False


def test_parse_typescript_source() -> None:
    source = b"""
function greet(name: string): string {
    return name;
}
"""

    source_parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    result = source_parser.parse(
        language=ProgrammingLanguage.TYPESCRIPT,
        source=source,
    )

    assert result.tree.root_node.type == "program"
    assert result.has_errors is False


def test_parse_tsx_source() -> None:
    source = b"""
function App() {
    return <div>Hello</div>;
}
"""

    source_parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    result = source_parser.parse(
        language=ProgrammingLanguage.TSX,
        source=source,
    )

    assert result.tree.root_node.type == "program"
    assert result.has_errors is False
