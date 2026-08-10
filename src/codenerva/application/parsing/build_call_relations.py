from codenerva.application.parsing.imported_symbol_resolver import (
    ImportedSymbolResolver,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)


class BuildCallRelationsService:
    def __init__(
        self,
        *,
        imported_symbol_resolver: ImportedSymbolResolver,
    ) -> None:
        self._imported_symbol_resolver = imported_symbol_resolver

    def build(
        self,
        *,
        calls: tuple,
        symbols: tuple[Symbol, ...],
        import_references: tuple[ImportReference, ...],
    ) -> tuple[SymbolRelation, ...]:
        symbols_by_name: dict[str, list[Symbol]] = {}

        for symbol in symbols:
            symbols_by_name.setdefault(
                symbol.name,
                [],
            ).append(symbol)

        relations: list[SymbolRelation] = []

        for call in calls:
            callers = symbols_by_name.get(
                call.caller_name,
                [],
            )

            if len(callers) != 1:
                continue

            caller = callers[0]

            local_callees = symbols_by_name.get(
                call.callee_name,
                [],
            )

            if len(local_callees) == 1:
                callee = local_callees[0]

                if caller.id != callee.id:
                    relations.append(
                        SymbolRelation.create(
                            source_symbol_id=caller.id,
                            target_symbol_id=callee.id,
                            kind=SymbolRelationKind.CALLS,
                        )
                    )

                continue

            imported_callee = self._resolve_imported_callee(
                import_references=import_references,
                callee_name=call.callee_name,
            )

            if imported_callee is None:
                continue

            relations.append(
                SymbolRelation.create(
                    source_symbol_id=caller.id,
                    target_symbol_id=imported_callee.id,
                    kind=SymbolRelationKind.CALLS,
                )
            )

        return tuple(relations)

    def _resolve_imported_callee(
        self,
        *,
        import_references: tuple[ImportReference, ...],
        callee_name: str,
    ) -> Symbol | None:
        for reference in import_references:
            matches_name = (
                reference.imported_name == callee_name or reference.alias == callee_name
            )

            if not matches_name:
                continue

            resolved = self._imported_symbol_resolver.resolve(
                import_reference=reference,
                callee_name=(
                    reference.imported_name
                    if reference.imported_name not in {None, "default"}
                    else callee_name
                ),
            )

            if resolved is not None:
                return resolved

        return None
