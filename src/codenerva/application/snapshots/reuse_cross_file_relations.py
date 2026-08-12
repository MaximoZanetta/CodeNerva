from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
)
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import SymbolRelation
from codenerva.domain.symbol_relation_store import (
    SymbolRelationStore,
)
from codenerva.domain.symbol_store import SymbolStore


@dataclass(frozen=True, slots=True)
class ReuseCrossFileRelationsResult:
    reused_source_file_relations: int
    reused_symbol_relations: int


class ReuseCrossFileRelationsUseCase:
    def __init__(
        self,
        *,
        symbol_store: SymbolStore,
        symbol_relation_store: SymbolRelationStore,
        source_file_relation_store: SourceFileRelationStore,
    ) -> None:
        self._symbol_store = symbol_store
        self._symbol_relation_store = symbol_relation_store
        self._source_file_relation_store = source_file_relation_store

    def execute(
        self,
        *,
        file_pairs: tuple[tuple[SourceFile, SourceFile], ...],
    ) -> ReuseCrossFileRelationsResult:
        if not file_pairs:
            return ReuseCrossFileRelationsResult(
                reused_source_file_relations=0,
                reused_symbol_relations=0,
            )

        previous_to_current_file: dict[
            UUID,
            SourceFile,
        ] = {previous.id: current for previous, current in file_pairs}

        previous_to_current_symbol: dict[
            UUID,
            Symbol,
        ] = {}

        for previous_file, current_file in file_pairs:
            previous_symbols = self._symbol_store.list_by_source_file_id(
                previous_file.id
            )

            current_symbols = self._symbol_store.list_by_source_file_id(current_file.id)

            current_by_identity = {
                self._symbol_identity(symbol): symbol for symbol in current_symbols
            }

            for previous_symbol in previous_symbols:
                identity = self._symbol_identity(previous_symbol)

                current_symbol = current_by_identity.get(identity)

                if current_symbol is None:
                    continue

                previous_to_current_symbol[previous_symbol.id] = current_symbol

        new_file_relations: list[SourceFileRelation] = []

        seen_file_relation_ids: set[UUID] = set()

        for previous_file, _ in file_pairs:
            relations = self._source_file_relation_store.list_by_source_file_id(
                previous_file.id
            )

            for relation in relations:
                current_source_file = previous_to_current_file.get(
                    relation.source_file_id
                )

                current_target_file = previous_to_current_file.get(
                    relation.target_file_id
                )

                if current_source_file is None or current_target_file is None:
                    continue

                new_relation = SourceFileRelation.create(
                    source_file_id=(current_source_file.id),
                    target_file_id=(current_target_file.id),
                    kind=relation.kind,
                )

                if new_relation.id in seen_file_relation_ids:
                    continue

                seen_file_relation_ids.add(new_relation.id)

                new_file_relations.append(new_relation)

        self._source_file_relation_store.save_many(tuple(new_file_relations))

        new_symbol_relations: list[SymbolRelation] = []

        seen_symbol_relation_ids: set[UUID] = set()

        for previous_symbol_id in previous_to_current_symbol:
            relations = self._symbol_relation_store.list_by_source_symbol_id(
                previous_symbol_id
            )

            for relation in relations:
                current_source_symbol = previous_to_current_symbol.get(
                    relation.source_symbol_id
                )

                current_target_symbol = previous_to_current_symbol.get(
                    relation.target_symbol_id
                )

                if current_source_symbol is None or current_target_symbol is None:
                    continue

                # Internal relations were already copied by
                # ReuseUnchangedFileUseCase.
                if (
                    current_source_symbol.source_file_id
                    == current_target_symbol.source_file_id
                ):
                    continue

                new_relation = SymbolRelation.create(
                    source_symbol_id=(current_source_symbol.id),
                    target_symbol_id=(current_target_symbol.id),
                    kind=relation.kind,
                )

                if new_relation.id in seen_symbol_relation_ids:
                    continue

                seen_symbol_relation_ids.add(new_relation.id)

                new_symbol_relations.append(new_relation)

        self._symbol_relation_store.save_many(tuple(new_symbol_relations))

        return ReuseCrossFileRelationsResult(
            reused_source_file_relations=len(new_file_relations),
            reused_symbol_relations=len(new_symbol_relations),
        )

    def _symbol_identity(
        self,
        symbol: Symbol,
    ) -> tuple[
        str,
        str,
        int,
        int,
    ]:
        return (
            symbol.qualified_name,
            symbol.kind.value,
            symbol.start_line,
            symbol.end_line,
        )
