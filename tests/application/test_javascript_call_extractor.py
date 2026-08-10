from codenerva.application.parsing.javascript_call_extractor import (
    JavaScriptCallExtractor,
)
from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.domain.programming_language import ProgrammingLanguage


def test_extract_javascript_calls() -> None:
    source = b"""
function validate() {
    return true;
}

const handleClick = () => {
    validate();
};
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.JAVASCRIPT,
        source=source,
    )

    extractor = JavaScriptCallExtractor()

    calls = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(calls) == 1
    assert calls[0].caller_name == "handleClick"
    assert calls[0].callee_name == "validate"
