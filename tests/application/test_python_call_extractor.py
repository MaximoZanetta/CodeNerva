from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.python_call_extractor import (
    PythonCallExtractor,
)
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.domain.programming_language import ProgrammingLanguage


def test_extract_python_calls() -> None:
    source = b"""
def validate():
    return True

def process():
    validate()
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.PYTHON,
        source=source,
    )

    extractor = PythonCallExtractor()

    calls = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(calls) == 1
    assert calls[0].caller_name == "process"
    assert calls[0].callee_name == "validate"


def test_extracts_method_call_owner() -> None:
    source = b"""
async def post_fizz(fizz, session):
    return await FizzService.create(fizz, session)
"""

    tree = object()

    extractor = PythonCallExtractor()

    result = extractor.extract(
        tree=tree,
        source=source,
    )

    assert len(result) == 1

    call = result[0]

    assert call.caller_name == "post_fizz"
    assert call.callee_name == "create"
    assert call.owner_name == "FizzService"
