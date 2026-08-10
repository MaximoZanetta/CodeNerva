from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)


class BuildSymbolRelationsService:
    def build(
        self,
        *,
        symbols: tuple[Symbol, ...],
    ) -> tuple[SymbolRelation, ...]:
        relations: list[SymbolRelation] = []

        for symbol in symbols:
            if symbol.parent_symbol_id is None:
                continue

            relations.append(
                SymbolRelation.create(
                    source_symbol_id=symbol.parent_symbol_id,
                    target_symbol_id=symbol.id,
                    kind=SymbolRelationKind.CONTAINS,
                )
            )

        return tuple(relations)
