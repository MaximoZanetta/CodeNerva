from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.domain.programming_language import ProgrammingLanguage


def print_tree(node, source: bytes, indent: int = 0) -> None:
    prefix = "  " * indent

    text = source[node.start_byte : node.end_byte].decode(
        "utf-8",
        errors="replace",
    )

    preview = text.replace("\n", " ")[:60]

    print(
        f"{prefix}{node.type} "
        f"[{node.start_point.row + 1}:{node.start_point.column}] "
        f"→ {preview!r}"
    )

    for child in node.named_children:
        print_tree(
            child,
            source,
            indent + 1,
        )


def main() -> None:
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

    result = parser.parse(
        language=ProgrammingLanguage.TYPESCRIPT,
        source=source,
    )

    print_tree(
        result.tree.root_node,
        source,
    )


if __name__ == "__main__":
    main()
