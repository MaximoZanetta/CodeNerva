from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.application.parsing.typescript_symbol_extractor import (
    TypeScriptSymbolExtractor,
)
from codenerva.domain.programming_language import ProgrammingLanguage


def test_extract_typescript_symbols() -> None:
    source = b"""
interface User {
    id: number;
    name: string;
}

class UserService {
    findUser(id: number): User | null {
        return null;
    }
}

function createUser(name: string): User {
    return {
        id: 1,
        name,
    };
}

const validateUser = (user: User): boolean => {
    return true;
};
"""

    parser = SourceParser(
        parser_registry=ParserRegistry(),
    )

    parse_result = parser.parse(
        language=ProgrammingLanguage.TYPESCRIPT,
        source=source,
    )

    extractor = TypeScriptSymbolExtractor()

    symbols = extractor.extract(
        tree=parse_result.tree,
        source=source,
    )

    assert len(symbols) == 5

    assert symbols[0].name == "User"
    assert symbols[0].kind == "INTERFACE"

    assert symbols[1].name == "UserService"
    assert symbols[1].kind == "CLASS"

    assert symbols[2].name == "findUser"
    assert symbols[2].kind == "METHOD"
    assert symbols[2].parent_name == "UserService"

    assert symbols[3].name == "createUser"
    assert symbols[3].kind == "FUNCTION"

    assert symbols[4].name == "validateUser"
    assert symbols[4].kind == "FUNCTION"
