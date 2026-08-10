from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.python_import_extractor import (
    PythonImportExtractor,
)
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.domain.programming_language import ProgrammingLanguage


def test_extract_python_imports() -> None:
    source = b"""
import os
import numpy as np

from flask import Flask
from .service import UserService
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.PYTHON,
        source=source,
    )

    extractor = PythonImportExtractor()

    imports = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(imports) == 4

    assert imports[0].module == "os"
    assert imports[0].imported_name is None

    assert imports[1].module == "numpy"
    assert imports[1].alias == "np"

    assert imports[2].module == "flask"
    assert imports[2].imported_name == "Flask"

    assert imports[3].module == ".service"
    assert imports[3].imported_name == "UserService"
