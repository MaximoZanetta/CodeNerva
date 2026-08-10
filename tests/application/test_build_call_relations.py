from uuid import uuid4

from codenerva.application.parsing.build_call_relations import (
    BuildCallRelationsService,
)
from codenerva.application.parsing.imported_symbol_resolver import (
    ImportedSymbolResolver,
)
from codenerva.application.parsing.python_call_extractor import (
    ExtractedCall,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import SymbolRelationKind
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)


def test_build_call_relation() -> None:
    source_file_id = uuid4()

    validate = Symbol.create(
        source_file_id=source_file_id,
        name="validate",
        qualified_name="validate",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    process = Symbol.create(
        source_file_id=source_file_id,
        name="process",
        qualified_name="process",
        kind=SymbolKind.FUNCTION,
        start_line=4,
        end_line=5,
    )

    service = BuildCallRelationsService(
        imported_symbol_resolver=ImportedSymbolResolver(
            source_file_relation_store=InMemorySourceFileRelationStore(),
            symbol_store=InMemorySymbolStore(),
        )
    )

    relations = service.build(
        calls=(
            ExtractedCall(
                caller_name="process",
                callee_name="validate",
                line=5,
            ),
        ),
        symbols=(
            validate,
            process,
        ),
        import_references=(),
    )

    assert len(relations) == 1
    assert relations[0].source_symbol_id == process.id
    assert relations[0].target_symbol_id == validate.id
    assert relations[0].kind is SymbolRelationKind.CALLS
