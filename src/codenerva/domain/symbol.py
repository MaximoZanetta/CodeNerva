from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid5

SYMBOL_NAMESPACE = UUID("7a4cc4be-2a21-4f4d-b4c1-72123e06f0d6")


class SymbolKind(StrEnum):
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    INTERFACE = "INTERFACE"


@dataclass(frozen=True, slots=True)
class Symbol:
    id: UUID
    source_file_id: UUID
    name: str
    qualified_name: str
    kind: SymbolKind
    start_line: int
    end_line: int
    parent_symbol_id: UUID | None

    @classmethod
    def create(
        cls,
        *,
        source_file_id: UUID,
        name: str,
        qualified_name: str,
        kind: SymbolKind,
        start_line: int,
        end_line: int,
        parent_symbol_id: UUID | None = None,
    ) -> "Symbol":
        normalized_name = name.strip()
        normalized_qualified_name = qualified_name.strip()

        if not normalized_name:
            raise ValueError("Symbol name cannot be empty.")

        if not normalized_qualified_name:
            raise ValueError("Qualified symbol name cannot be empty.")

        if start_line <= 0:
            raise ValueError("Symbol start line must be positive.")

        if end_line < start_line:
            raise ValueError("Symbol end line cannot be before start line.")

        symbol_id = uuid5(
            SYMBOL_NAMESPACE,
            (
                f"{source_file_id}:"
                f"{kind.value}:"
                f"{normalized_qualified_name}:"
                f"{start_line}:"
                f"{end_line}"
            ),
        )

        return cls(
            id=symbol_id,
            source_file_id=source_file_id,
            name=normalized_name,
            qualified_name=normalized_qualified_name,
            kind=kind,
            start_line=start_line,
            end_line=end_line,
            parent_symbol_id=parent_symbol_id,
        )
