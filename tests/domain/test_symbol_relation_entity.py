from uuid import uuid4

import pytest

from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)


def test_create_symbol_relation() -> None:
    source_symbol_id = uuid4()
    target_symbol_id = uuid4()

    relation = SymbolRelation.create(
        source_symbol_id=source_symbol_id,
        target_symbol_id=target_symbol_id,
        kind=SymbolRelationKind.CONTAINS,
    )

    assert relation.source_symbol_id == source_symbol_id
    assert relation.target_symbol_id == target_symbol_id
    assert relation.kind is SymbolRelationKind.CONTAINS


def test_symbol_relation_id_is_deterministic() -> None:
    source_symbol_id = uuid4()
    target_symbol_id = uuid4()

    first = SymbolRelation.create(
        source_symbol_id=source_symbol_id,
        target_symbol_id=target_symbol_id,
        kind=SymbolRelationKind.CONTAINS,
    )

    second = SymbolRelation.create(
        source_symbol_id=source_symbol_id,
        target_symbol_id=target_symbol_id,
        kind=SymbolRelationKind.CONTAINS,
    )

    assert first.id == second.id


def test_symbol_cannot_relate_to_itself() -> None:
    symbol_id = uuid4()

    with pytest.raises(ValueError):
        SymbolRelation.create(
            source_symbol_id=symbol_id,
            target_symbol_id=symbol_id,
            kind=SymbolRelationKind.CONTAINS,
        )
