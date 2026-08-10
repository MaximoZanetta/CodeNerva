from uuid import uuid4

from codenerva.application.parsing.build_symbol_relations import (
    BuildSymbolRelationsService,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import SymbolRelationKind


def test_build_contains_relation() -> None:
    source_file_id = uuid4()

    class_symbol = Symbol.create(
        source_file_id=source_file_id,
        name="AuthService",
        qualified_name="AuthService",
        kind=SymbolKind.CLASS,
        start_line=1,
        end_line=10,
    )

    method_symbol = Symbol.create(
        source_file_id=source_file_id,
        name="login",
        qualified_name="AuthService.login",
        kind=SymbolKind.METHOD,
        start_line=2,
        end_line=5,
        parent_symbol_id=class_symbol.id,
    )

    service = BuildSymbolRelationsService()

    relations = service.build(
        symbols=(
            class_symbol,
            method_symbol,
        )
    )

    assert len(relations) == 1

    relation = relations[0]

    assert relation.source_symbol_id == class_symbol.id
    assert relation.target_symbol_id == method_symbol.id
    assert relation.kind is SymbolRelationKind.CONTAINS
