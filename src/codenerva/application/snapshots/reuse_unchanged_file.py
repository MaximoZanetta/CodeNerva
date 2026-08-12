from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.chunk import Chunk
from codenerva.domain.chunk_store import ChunkStore
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation import SymbolRelation
from codenerva.domain.symbol_relation_store import SymbolRelationStore
from codenerva.domain.symbol_store import SymbolStore
from codenerva.domain.vector_record import VectorRecord
from codenerva.domain.vector_store import VectorStore


@dataclass(frozen=True, slots=True)
class ReuseUnchangedFileResult:
    reused_symbols: int
    reused_symbol_relations: int
    reused_chunks: int
    reused_vectors: int


class ReuseUnchangedFileUseCase:
    def __init__(
        self,
        *,
        symbol_store: SymbolStore,
        symbol_relation_store: SymbolRelationStore,
        chunk_store: ChunkStore,
        vector_store: VectorStore,
    ) -> None:
        self._symbol_store = symbol_store
        self._symbol_relation_store = symbol_relation_store
        self._chunk_store = chunk_store
        self._vector_store = vector_store

    def execute(
        self,
        *,
        previous_source_file: SourceFile,
        current_source_file: SourceFile,
    ) -> ReuseUnchangedFileResult:
        if previous_source_file.content_hash != current_source_file.content_hash:
            raise ValueError("Cannot reuse intelligence for a modified source file.")

        previous_symbols = self._symbol_store.list_by_source_file_id(
            previous_source_file.id
        )

        symbol_map: dict[UUID, Symbol] = {}
        new_symbols: list[Symbol] = []

        for previous_symbol in previous_symbols:
            new_symbol = Symbol.create(
                source_file_id=current_source_file.id,
                name=previous_symbol.name,
                qualified_name=previous_symbol.qualified_name,
                kind=previous_symbol.kind,
                start_line=previous_symbol.start_line,
                end_line=previous_symbol.end_line,
                parent_symbol_id=None,
            )

            symbol_map[previous_symbol.id] = new_symbol
            new_symbols.append(new_symbol)

        # Rebuild parent references once all new symbol IDs exist.
        rebuilt_symbols: list[Symbol] = []
        rebuilt_symbol_map: dict[UUID, Symbol] = {}

        for previous_symbol in previous_symbols:
            new_symbol = symbol_map[previous_symbol.id]

            parent_symbol_id = None

            if previous_symbol.parent_symbol_id is not None:
                parent_symbol_id = symbol_map[previous_symbol.parent_symbol_id].id

            rebuilt_symbol = Symbol(
                id=new_symbol.id,
                source_file_id=new_symbol.source_file_id,
                name=new_symbol.name,
                qualified_name=new_symbol.qualified_name,
                kind=new_symbol.kind,
                start_line=new_symbol.start_line,
                end_line=new_symbol.end_line,
                parent_symbol_id=parent_symbol_id,
            )

            rebuilt_symbols.append(rebuilt_symbol)

            rebuilt_symbol_map[previous_symbol.id] = rebuilt_symbol

        self._symbol_store.save_many(tuple(rebuilt_symbols))

        # Reuse only symbol relations whose source and target
        # are both inside this unchanged source file.
        new_relations: list[SymbolRelation] = []

        previous_symbol_ids = set(rebuilt_symbol_map)

        for previous_symbol in previous_symbols:
            relations = self._symbol_relation_store.list_by_source_symbol_id(
                previous_symbol.id
            )

            for relation in relations:
                if relation.target_symbol_id not in previous_symbol_ids:
                    continue

                current_source_symbol = rebuilt_symbol_map[relation.source_symbol_id]

                current_target_symbol = rebuilt_symbol_map[relation.target_symbol_id]

                new_relations.append(
                    SymbolRelation.create(
                        source_symbol_id=(current_source_symbol.id),
                        target_symbol_id=(current_target_symbol.id),
                        kind=relation.kind,
                    )
                )

        self._symbol_relation_store.save_many(tuple(new_relations))

        reused_chunks = 0
        reused_vectors = 0

        new_chunks: list[Chunk] = []
        new_records: list[VectorRecord] = []

        for previous_symbol in previous_symbols:
            current_symbol = rebuilt_symbol_map[previous_symbol.id]

            previous_chunks = self._chunk_store.list_by_symbol_id(previous_symbol.id)

            for previous_chunk in previous_chunks:
                new_chunk = Chunk.create(
                    snapshot_id=(current_source_file.snapshot_id),
                    source_file_id=(current_source_file.id),
                    symbol_id=current_symbol.id,
                    text=previous_chunk.text,
                    relative_path=(current_source_file.relative_path.as_posix()),
                    language=previous_chunk.language,
                    qualified_name=(previous_chunk.qualified_name),
                    symbol_kind=(previous_chunk.symbol_kind),
                    start_line=(previous_chunk.start_line),
                    end_line=(previous_chunk.end_line),
                    part_index=(previous_chunk.part_index),
                    part_count=(previous_chunk.part_count),
                    code=previous_chunk.code,
                )

                new_chunks.append(new_chunk)

                reused_chunks += 1

                previous_record = self._vector_store.get_by_chunk_id(previous_chunk.id)

                if previous_record is None:
                    continue

                new_records.append(
                    VectorRecord(
                        chunk_id=new_chunk.id,
                        vector=previous_record.vector,
                        snapshot_id=(current_source_file.snapshot_id),
                        source_file_id=(current_source_file.id),
                        symbol_id=current_symbol.id,
                        relative_path=(current_source_file.relative_path.as_posix()),
                        language=(previous_record.language),
                        qualified_name=(previous_record.qualified_name),
                        symbol_kind=(previous_record.symbol_kind),
                    )
                )

                reused_vectors += 1

        self._chunk_store.save_many(tuple(new_chunks))

        self._vector_store.save_many(tuple(new_records))

        return ReuseUnchangedFileResult(
            reused_symbols=len(rebuilt_symbols),
            reused_symbol_relations=len(new_relations),
            reused_chunks=reused_chunks,
            reused_vectors=reused_vectors,
        )
