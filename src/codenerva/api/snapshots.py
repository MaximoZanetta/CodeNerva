from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from codenerva.api.dependencies import (
    chunk_store,
    import_reference_store,
    snapshot_store,
    source_file_relation_store,
    source_file_store,
    storage_root,
    symbol_relation_store,
    symbol_store,
    vector_store,
)
from codenerva.application.chunking.symbol_chunker import SymbolChunker
from codenerva.application.embeddings.embed_chunks import EmbedChunksUseCase
from codenerva.application.embeddings.index_snapshot import (
    IndexSnapshotUseCase,
)
from codenerva.application.embeddings.index_snapshot import (
    SnapshotNotFoundError as IndexSnapshotNotFoundError,
)
from codenerva.application.embeddings.vector_record_mapper import (
    VectorRecordMapper,
)
from codenerva.application.graph.graph_query_service import (
    GraphQueryService,
)
from codenerva.application.graph.graph_traversal_service import (
    GraphTraversalService,
)
from codenerva.application.graph.graph_traversal_service import (
    SymbolNotFoundError as TraversalSymbolNotFoundError,
)
from codenerva.application.graph.source_file_traversal_service import (
    SourceFileNotFoundError as TraversalSourceFileNotFoundError,
)
from codenerva.application.graph.source_file_traversal_service import (
    SourceFileTraversalService,
)
from codenerva.application.parsing.analyze_snapshot import (
    AnalyzeSnapshotUseCase,
)
from codenerva.application.parsing.analyze_snapshot import (
    SnapshotNotFoundError as AnalyzeSnapshotNotFoundError,
)
from codenerva.application.parsing.analyze_source_file import (
    AnalyzeSourceFileUseCase,
    SourceFileNotFoundError,
    SymbolAnalysisNotAvailableError,
)
from codenerva.application.parsing.build_call_relations import (
    BuildCallRelationsService,
)
from codenerva.application.parsing.build_source_file_relations import (
    BuildSourceFileRelationsService,
)
from codenerva.application.parsing.build_symbol_relations import (
    BuildSymbolRelationsService,
)
from codenerva.application.parsing.call_extractor_registry import (
    CallExtractorRegistry,
)
from codenerva.application.parsing.import_extractor_registry import (
    ImportExtractorRegistry,
)
from codenerva.application.parsing.import_reference_mapper import ImportReferenceMapper
from codenerva.application.parsing.imported_symbol_resolver import (
    ImportedSymbolResolver,
)
from codenerva.application.parsing.list_source_file_imports import (
    ListSourceFileImportsUseCase,
)
from codenerva.application.parsing.list_source_file_imports import (
    SourceFileNotFoundError as ListImportsSourceFileNotFoundError,
)
from codenerva.application.parsing.list_source_file_relations import (
    ListSourceFileRelationsUseCase,
)
from codenerva.application.parsing.list_source_file_relations import (
    SourceFileNotFoundError as ListRelationsSourceFileNotFoundError,
)
from codenerva.application.parsing.list_source_file_symbols import (
    ListSourceFileSymbolsUseCase,
)
from codenerva.application.parsing.list_source_file_symbols import (
    SourceFileNotFoundError as ListSymbolsSourceFileNotFoundError,
)
from codenerva.application.parsing.list_symbol_relations import (
    ListSymbolRelationsUseCase,
)
from codenerva.application.parsing.list_symbol_relations import (
    SourceFileNotFoundError as ListSymbolRelationsSourceFileNotFoundError,
)
from codenerva.application.parsing.local_import_resolver import LocalImportResolver
from codenerva.application.parsing.parser_registry import (
    ParserRegistry,
)
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.application.parsing.symbol_extractor_registry import (
    SymbolExtractorRegistry,
)

# from codenerva.application.parsing.python_symbol_extractor import (
#     PythonSymbolExtractor,
# )
from codenerva.application.parsing.symbol_mapper import (
    SymbolMapper,
)
from codenerva.application.parsing.typescript_path_alias_resolver import (
    TypeScriptPathAliasResolver,
)
from codenerva.application.qa.answer_repository_question import (
    AnswerRepositoryQuestionUseCase,
    SnapshotNotFoundError,
    SnapshotNotReadyError,
)
from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.application.retrieval.hybrid_reranker import HybridReranker
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalUseCase,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContextBuilder,
)
from codenerva.application.retrieval.semantic_search import (
    SemanticSearchUseCase,
)
from codenerva.application.snapshots.build_incremental_index_plan import (
    BuildIncrementalIndexPlanUseCase,
)
from codenerva.application.snapshots.compare_snapshots import CompareSnapshotsUseCase
from codenerva.application.snapshots.incremental_index_snapshot import (
    IncrementalIndexSnapshotUseCase,
)
from codenerva.application.snapshots.purge_snapshot import (
    PurgeSnapshotUseCase,
)
from codenerva.application.snapshots.purge_snapshot import (
    SnapshotNotFoundError as PurgeSnapshotNotFoundError,
)
from codenerva.application.snapshots.reuse_cross_file_relations import (
    ReuseCrossFileRelationsUseCase,
)
from codenerva.application.snapshots.reuse_unchanged_file import (
    ReuseUnchangedFileUseCase,
)
from codenerva.application.source.discover_snapshot_files import (
    DiscoverSnapshotFilesUseCase,
)
from codenerva.application.source.discover_snapshot_files import (
    SnapshotNotFoundError as DiscoverSnapshotNotFoundError,
)
from codenerva.application.source.file_discovery import FileDiscoveryService
from codenerva.application.source.language_detector import LanguageDetector
from codenerva.application.source.list_snapshot_files import (
    ListSnapshotFilesUseCase,
)
from codenerva.application.source.list_snapshot_files import (
    SnapshotNotFoundError as ListSnapshotNotFoundError,
)
from codenerva.infrastructure.in_memory_graph_repository import (
    InMemoryGraphRepository,
)
from codenerva.infrastructure.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from codenerva.infrastructure.openai_llm_provider import (
    OpenAILLMProvider,
)

router = APIRouter(
    prefix="/api/v1/snapshots",
    tags=["snapshots"],
)


class LanguageSummaryResponse(BaseModel):
    language: str
    file_count: int
    total_bytes: int


class DiscoverSnapshotFilesResponse(BaseModel):
    snapshot_id: str
    total_files: int
    ignored_count: int
    languages: list[LanguageSummaryResponse]


class SourceFileResponse(BaseModel):
    id: str
    relative_path: str
    language: str
    size_bytes: int
    content_hash: str


class ListSnapshotFilesResponse(BaseModel):
    snapshot_id: str
    files: list[SourceFileResponse]


class SymbolResponse(BaseModel):
    id: str
    name: str
    qualified_name: str
    kind: str
    start_line: int
    end_line: int
    parent_symbol_id: str | None


class AnalyzeSourceFileResponse(BaseModel):
    source_file_id: str
    has_parse_errors: bool
    symbols: list[SymbolResponse]


class ListSourceFileSymbolsResponse(BaseModel):
    source_file_id: str
    symbols: list[SymbolResponse]


class AnalyzeSnapshotResponse(BaseModel):
    snapshot_id: str
    total_files: int
    analyzed_files: int
    skipped_files: int
    files_with_parse_errors: int
    total_symbols: int


class ImportResponse(BaseModel):
    id: str
    module: str
    imported_name: str | None
    alias: str | None
    line: int
    resolved_source_file_id: str | None
    resolved_relative_path: str | None


class ListSourceFileImportsResponse(BaseModel):
    source_file_id: str
    imports: list[ImportResponse]


class SourceFileRelationResponse(BaseModel):
    id: str
    kind: str
    target_source_file_id: str
    target_relative_path: str


class ListSourceFileRelationsResponse(BaseModel):
    source_file_id: str
    relations: list[SourceFileRelationResponse]


class SymbolRelationResponse(BaseModel):
    id: str
    kind: str
    source_symbol_id: str
    source_symbol_name: str
    target_symbol_id: str
    target_symbol_name: str


class ListSymbolRelationsResponse(BaseModel):
    source_file_id: str
    relations: list[SymbolRelationResponse]


class TraversalNodeResponse(BaseModel):
    symbol_id: str
    symbol_name: str
    depth: int


class CallTraversalResponse(BaseModel):
    root_symbol_id: str
    root_symbol_name: str
    nodes: list[TraversalNodeResponse]


class FileTraversalNodeResponse(BaseModel):
    source_file_id: str
    relative_path: str
    depth: int


class ImportTraversalResponse(BaseModel):
    root_source_file_id: str
    root_relative_path: str
    nodes: list[FileTraversalNodeResponse]


class ChunkResponse(BaseModel):
    id: str
    symbol_id: str
    qualified_name: str
    symbol_kind: str
    relative_path: str
    language: str
    start_line: int
    end_line: int
    part_index: int
    part_count: int
    text: str


class ListChunksResponse(BaseModel):
    source_file_id: str
    chunks: list[ChunkResponse]


class IndexSourceFileResponse(BaseModel):
    source_file_id: str
    indexed_chunks: int


class SemanticSearchItemResponse(BaseModel):
    chunk_id: str
    symbol_id: str
    qualified_name: str
    relative_path: str
    language: str
    symbol_kind: str
    score: float


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchItemResponse]


class HybridSemanticHitResponse(BaseModel):
    symbol_id: str
    qualified_name: str
    kind: str
    score: float


class HybridExpandedSymbolResponse(BaseModel):
    symbol_id: str
    qualified_name: str
    kind: str
    relation: str
    source_symbol_id: str


class HybridSearchResponse(BaseModel):
    query: str
    semantic_hits: list[HybridSemanticHitResponse]
    expanded_symbols: list[HybridExpandedSymbolResponse]


class RetrievalContextItemResponse(BaseModel):
    symbol_id: str
    qualified_name: str
    relative_path: str
    language: str
    symbol_kind: str
    semantic_score: float | None
    semantic_rank: int | None
    graph_relations: list[str]
    text: str


class HybridContextResponse(BaseModel):
    query: str
    items: list[RetrievalContextItemResponse]
    formatted_context: str


class AskRepositoryRequest(BaseModel):
    snapshot_id: UUID
    question: str
    top_k: int = 3
    max_items: int = 6
    max_chars: int = 12000


class AskRepositorySourceResponse(BaseModel):
    relative_path: str
    qualified_name: str
    symbol_kind: str
    language: str
    start_line: int
    end_line: int
    semantic_score: float | None
    semantic_rank: int | None
    graph_relations: list[str]
    retrieval_origin: str
    final_score: float


class RetrievalDiagnosticsResponse(BaseModel):
    semantic_sources: int
    graph_sources: int
    both_sources: int
    final_context_items: int


class AskRepositoryResponse(BaseModel):
    snapshot_id: str
    question: str
    answer: str
    context_items: int
    sources: list[AskRepositorySourceResponse]
    retrieval_diagnostics: RetrievalDiagnosticsResponse


class IndexSnapshotResponse(BaseModel):
    snapshot_id: str
    total_files: int
    indexed_files: int
    skipped_files: int
    indexed_chunks: int


class IncrementalIndexSnapshotRequest(BaseModel):
    previous_snapshot_id: UUID
    current_snapshot_id: UUID


class IncrementalIndexSnapshotResponse(BaseModel):
    previous_snapshot_id: str
    current_snapshot_id: str
    reused_files: int
    analyzed_files: int
    skipped_files: int
    deleted_files: int
    reused_symbols: int
    reused_symbol_relations: int
    reused_source_file_relations: int
    reused_chunks: int
    reused_vectors: int
    indexed_chunks: int


class PurgeSnapshotResponse(BaseModel):
    snapshot_id: str
    deleted_vectors: int
    deleted_symbol_relations: int
    deleted_source_file_relations: int
    deleted_import_references: int
    deleted_chunks: int
    deleted_symbols: int
    deleted_source_files: int
    snapshot_deleted: bool


class SnapshotResponse(BaseModel):
    id: str
    repository_id: str
    commit_sha: str
    branch: str | None
    remote_url: str
    status: str


def get_discover_snapshot_files_use_case() -> DiscoverSnapshotFilesUseCase:
    return DiscoverSnapshotFilesUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        file_discovery_service=FileDiscoveryService(
            language_detector=LanguageDetector(),
        ),
        storage_root=storage_root,
    )


def get_list_snapshot_files_use_case() -> ListSnapshotFilesUseCase:
    return ListSnapshotFilesUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
    )


def get_analyze_source_file_use_case() -> AnalyzeSourceFileUseCase:
    return AnalyzeSourceFileUseCase(
        source_file_store=source_file_store,
        snapshot_store=snapshot_store,
        symbol_store=symbol_store,
        source_parser=SourceParser(
            parser_registry=ParserRegistry(),
        ),
        symbol_extractor_registry=SymbolExtractorRegistry(),
        symbol_mapper=SymbolMapper(),
        storage_root=storage_root,
        symbol_relation_store=symbol_relation_store,
        build_symbol_relations_service=BuildSymbolRelationsService(),
        import_reference_store=import_reference_store,
        import_extractor_registry=ImportExtractorRegistry(),
        import_reference_mapper=ImportReferenceMapper(),
        source_file_relation_store=source_file_relation_store,
        build_source_file_relations_service=BuildSourceFileRelationsService(
            local_import_resolver=LocalImportResolver(),
            typescript_path_alias_resolver=TypeScriptPathAliasResolver(),
        ),
        call_extractor_registry=CallExtractorRegistry(),
        build_call_relations_service=BuildCallRelationsService(
            imported_symbol_resolver=ImportedSymbolResolver(
                source_file_relation_store=source_file_relation_store,
                symbol_store=symbol_store,
            )
        ),
    )


def get_list_source_file_symbols_use_case() -> ListSourceFileSymbolsUseCase:
    return ListSourceFileSymbolsUseCase(
        source_file_store=source_file_store,
        symbol_store=symbol_store,
    )


def get_analyze_snapshot_use_case() -> AnalyzeSnapshotUseCase:
    return AnalyzeSnapshotUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        source_parser=SourceParser(
            parser_registry=ParserRegistry(),
        ),
        symbol_extractor_registry=SymbolExtractorRegistry(),
        symbol_mapper=SymbolMapper(),
        storage_root=storage_root,
        symbol_relation_store=symbol_relation_store,
        build_symbol_relations_service=BuildSymbolRelationsService(),
        import_reference_store=import_reference_store,
        import_extractor_registry=ImportExtractorRegistry(),
        import_reference_mapper=ImportReferenceMapper(),
        source_file_relation_store=source_file_relation_store,
        build_source_file_relations_service=BuildSourceFileRelationsService(
            local_import_resolver=LocalImportResolver(),
            typescript_path_alias_resolver=TypeScriptPathAliasResolver(),
        ),
        call_extractor_registry=CallExtractorRegistry(),
        build_call_relations_service=BuildCallRelationsService(
            imported_symbol_resolver=ImportedSymbolResolver(
                source_file_relation_store=source_file_relation_store,
                symbol_store=symbol_store,
            ),
        ),
    )


def get_list_source_file_imports_use_case() -> ListSourceFileImportsUseCase:
    return ListSourceFileImportsUseCase(
        source_file_store=source_file_store,
        import_reference_store=import_reference_store,
        source_file_relation_store=source_file_relation_store,
    )


def get_list_source_file_relations_use_case() -> ListSourceFileRelationsUseCase:
    return ListSourceFileRelationsUseCase(
        source_file_store=source_file_store,
        source_file_relation_store=source_file_relation_store,
    )


def get_list_symbol_relations_use_case() -> ListSymbolRelationsUseCase:
    return ListSymbolRelationsUseCase(
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
    )


def get_graph_traversal_service() -> GraphTraversalService:
    graph_repository = InMemoryGraphRepository(
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
        source_file_store=source_file_store,
        source_file_relation_store=source_file_relation_store,
    )

    return GraphTraversalService(
        graph_repository=graph_repository,
    )


def get_source_file_traversal_service() -> SourceFileTraversalService:
    graph_repository = InMemoryGraphRepository(
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
        source_file_store=source_file_store,
        source_file_relation_store=source_file_relation_store,
    )

    return SourceFileTraversalService(
        graph_repository=graph_repository,
    )


def get_hybrid_retrieval_use_case() -> HybridRetrievalUseCase:
    graph_repository = InMemoryGraphRepository(
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
        source_file_store=source_file_store,
        source_file_relation_store=source_file_relation_store,
    )

    semantic_search = SemanticSearchUseCase(
        embedding_provider=OpenAIEmbeddingProvider(),
        vector_store=vector_store,
    )

    graph_query_service = GraphQueryService(
        graph_repository=graph_repository,
    )

    return HybridRetrievalUseCase(
        semantic_search=semantic_search,
        graph_query_service=graph_query_service,
    )


def get_retrieval_context_builder() -> RetrievalContextBuilder:
    return RetrievalContextBuilder(
        chunk_store=chunk_store,
    )


def get_answer_repository_question_use_case() -> AnswerRepositoryQuestionUseCase:
    return AnswerRepositoryQuestionUseCase(
        hybrid_retrieval=get_hybrid_retrieval_use_case(),
        hybrid_reranker=HybridReranker(
            source_file_store=source_file_store,
        ),
        context_builder=RetrievalContextBuilder(
            chunk_store=chunk_store,
        ),
        context_formatter=ContextFormatter(),
        llm_provider=OpenAILLMProvider(),
        snapshot_store=snapshot_store,
    )


def get_index_snapshot_use_case() -> IndexSnapshotUseCase:
    embed_chunks_use_case = EmbedChunksUseCase(
        embedding_provider=OpenAIEmbeddingProvider(),
        vector_store=vector_store,
        vector_record_mapper=VectorRecordMapper(),
    )

    return IndexSnapshotUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        chunk_store=chunk_store,
        symbol_chunker=SymbolChunker(),
        embed_chunks_use_case=embed_chunks_use_case,
        storage_root=storage_root,
    )


def get_incremental_index_snapshot_use_case() -> IncrementalIndexSnapshotUseCase:
    embed_chunks_use_case = EmbedChunksUseCase(
        embedding_provider=OpenAIEmbeddingProvider(),
        vector_store=vector_store,
        vector_record_mapper=VectorRecordMapper(),
    )

    return IncrementalIndexSnapshotUseCase(
        source_file_store=source_file_store,
        compare_snapshots_use_case=CompareSnapshotsUseCase(
            source_file_store=source_file_store,
        ),
        build_plan_use_case=BuildIncrementalIndexPlanUseCase(),
        reuse_unchanged_file_use_case=ReuseUnchangedFileUseCase(
            symbol_store=symbol_store,
            symbol_relation_store=symbol_relation_store,
            chunk_store=chunk_store,
            vector_store=vector_store,
        ),
        reuse_cross_file_relations_use_case=ReuseCrossFileRelationsUseCase(
            symbol_store=symbol_store,
            symbol_relation_store=symbol_relation_store,
            source_file_relation_store=source_file_relation_store,
        ),
        analyze_source_file_use_case=get_analyze_source_file_use_case(),
        snapshot_store=snapshot_store,
        symbol_chunker=SymbolChunker(),
        chunk_store=chunk_store,
        embed_chunks_use_case=embed_chunks_use_case,
        storage_root=storage_root,
    )


def get_purge_snapshot_use_case() -> PurgeSnapshotUseCase:
    return PurgeSnapshotUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
        source_file_relation_store=source_file_relation_store,
        import_reference_store=import_reference_store,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )


@router.get(
    "/{snapshot_id}",
    response_model=SnapshotResponse,
)
def get_snapshot(
    snapshot_id: UUID,
) -> SnapshotResponse:
    snapshot = snapshot_store.get_by_id(snapshot_id)

    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Snapshot with id {snapshot_id} was not found."),
        )

    return SnapshotResponse(
        id=str(snapshot.id),
        repository_id=str(snapshot.repository_id),
        commit_sha=snapshot.commit_sha,
        branch=snapshot.branch,
        remote_url=snapshot.remote_url,
        status=snapshot.status.value,
    )


@router.post(
    "/{snapshot_id}/discover-files",
    response_model=DiscoverSnapshotFilesResponse,
    status_code=status.HTTP_200_OK,
)
def discover_snapshot_files(
    snapshot_id: UUID,
    use_case: Annotated[
        DiscoverSnapshotFilesUseCase,
        Depends(get_discover_snapshot_files_use_case),
    ],
) -> DiscoverSnapshotFilesResponse:
    try:
        result = use_case.execute(snapshot_id)
    except DiscoverSnapshotNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return DiscoverSnapshotFilesResponse(
        snapshot_id=str(result.snapshot_id),
        total_files=result.total_files,
        ignored_count=result.ignored_count,
        languages=[
            LanguageSummaryResponse(
                language=summary.language.value,
                file_count=summary.file_count,
                total_bytes=summary.total_bytes,
            )
            for summary in result.languages
        ],
    )


@router.get(
    "/{snapshot_id}/files",
    response_model=ListSnapshotFilesResponse,
)
def list_snapshot_files(
    snapshot_id: UUID,
    use_case: Annotated[
        ListSnapshotFilesUseCase,
        Depends(get_list_snapshot_files_use_case),
    ],
) -> ListSnapshotFilesResponse:
    try:
        result = use_case.execute(snapshot_id)
    except ListSnapshotNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ListSnapshotFilesResponse(
        snapshot_id=str(result.snapshot_id),
        files=[
            SourceFileResponse(
                id=str(source_file.id),
                relative_path=source_file.relative_path,
                language=source_file.language.value,
                size_bytes=source_file.size_bytes,
                content_hash=source_file.content_hash,
            )
            for source_file in result.files
        ],
    )


@router.post(
    "/files/{source_file_id}/analyze",
    response_model=AnalyzeSourceFileResponse,
)
def analyze_source_file(
    source_file_id: UUID,
    use_case: Annotated[
        AnalyzeSourceFileUseCase,
        Depends(get_analyze_source_file_use_case),
    ],
) -> AnalyzeSourceFileResponse:
    try:
        result = use_case.execute(
            source_file_id=source_file_id,
        )
    except SourceFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except SymbolAnalysisNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return AnalyzeSourceFileResponse(
        source_file_id=str(result.source_file_id),
        has_parse_errors=result.has_parse_errors,
        symbols=[
            SymbolResponse(
                id=str(symbol.id),
                name=symbol.name,
                qualified_name=symbol.qualified_name,
                kind=symbol.kind.value,
                start_line=symbol.start_line,
                end_line=symbol.end_line,
                parent_symbol_id=(
                    str(symbol.parent_symbol_id) if symbol.parent_symbol_id else None
                ),
            )
            for symbol in result.symbols
        ],
    )


@router.get(
    "/files/{source_file_id}/symbols",
    response_model=ListSourceFileSymbolsResponse,
)
def list_source_file_symbols(
    source_file_id: UUID,
    use_case: Annotated[
        ListSourceFileSymbolsUseCase,
        Depends(get_list_source_file_symbols_use_case),
    ],
) -> ListSourceFileSymbolsResponse:
    try:
        result = use_case.execute(source_file_id)
    except ListSymbolsSourceFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ListSourceFileSymbolsResponse(
        source_file_id=str(result.source_file_id),
        symbols=[
            SymbolResponse(
                id=str(symbol.id),
                name=symbol.name,
                qualified_name=symbol.qualified_name,
                kind=symbol.kind.value,
                start_line=symbol.start_line,
                end_line=symbol.end_line,
                parent_symbol_id=(
                    str(symbol.parent_symbol_id) if symbol.parent_symbol_id else None
                ),
            )
            for symbol in result.symbols
        ],
    )


@router.post(
    "/{snapshot_id}/analyze",
    response_model=AnalyzeSnapshotResponse,
)
def analyze_snapshot(
    snapshot_id: UUID,
    use_case: Annotated[
        AnalyzeSnapshotUseCase,
        Depends(get_analyze_snapshot_use_case),
    ],
) -> AnalyzeSnapshotResponse:
    try:
        result = use_case.execute(snapshot_id)
    except AnalyzeSnapshotNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return AnalyzeSnapshotResponse(
        snapshot_id=str(result.snapshot_id),
        total_files=result.total_files,
        analyzed_files=result.analyzed_files,
        skipped_files=result.skipped_files,
        files_with_parse_errors=result.files_with_parse_errors,
        total_symbols=result.total_symbols,
    )


@router.get(
    "/files/{source_file_id}/imports",
    response_model=ListSourceFileImportsResponse,
)
def list_source_file_imports(
    source_file_id: UUID,
    use_case: Annotated[
        ListSourceFileImportsUseCase,
        Depends(get_list_source_file_imports_use_case),
    ],
) -> ListSourceFileImportsResponse:
    try:
        result = use_case.execute(source_file_id)
    except ListImportsSourceFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ListSourceFileImportsResponse(
        source_file_id=str(result.source_file_id),
        imports=[
            ImportResponse(
                id=str(item.id),
                module=item.module,
                imported_name=item.imported_name,
                alias=item.alias,
                line=item.line,
                resolved_source_file_id=(
                    str(item.resolved_source_file_id)
                    if item.resolved_source_file_id
                    else None
                ),
                resolved_relative_path=item.resolved_relative_path,
            )
            for item in result.imports
        ],
    )


@router.get(
    "/files/{source_file_id}/relations",
    response_model=ListSourceFileRelationsResponse,
)
def list_source_file_relations(
    source_file_id: UUID,
    use_case: Annotated[
        ListSourceFileRelationsUseCase,
        Depends(get_list_source_file_relations_use_case),
    ],
) -> ListSourceFileRelationsResponse:
    try:
        result = use_case.execute(source_file_id)
    except ListRelationsSourceFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ListSourceFileRelationsResponse(
        source_file_id=str(result.source_file_id),
        relations=[
            SourceFileRelationResponse(
                id=str(relation.id),
                kind=relation.kind.value,
                target_source_file_id=str(relation.target_source_file_id),
                target_relative_path=relation.target_relative_path,
            )
            for relation in result.relations
        ],
    )


@router.get(
    "/files/{source_file_id}/symbol-relations",
    response_model=ListSymbolRelationsResponse,
)
def list_symbol_relations(
    source_file_id: UUID,
    use_case: Annotated[
        ListSymbolRelationsUseCase,
        Depends(get_list_symbol_relations_use_case),
    ],
) -> ListSymbolRelationsResponse:
    try:
        result = use_case.execute(source_file_id)
    except ListSymbolRelationsSourceFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ListSymbolRelationsResponse(
        source_file_id=str(result.source_file_id),
        relations=[
            SymbolRelationResponse(
                id=str(relation.id),
                kind=relation.kind.value,
                source_symbol_id=str(relation.source_symbol_id),
                source_symbol_name=relation.source_symbol_name,
                target_symbol_id=str(relation.target_symbol_id),
                target_symbol_name=relation.target_symbol_name,
            )
            for relation in result.relations
        ],
    )


@router.get(
    "/symbols/{symbol_id}/calls",
    response_model=CallTraversalResponse,
)
def traverse_symbol_calls(
    symbol_id: UUID,
    max_depth: int = 3,
    service: Annotated[
        GraphTraversalService,
        Depends(get_graph_traversal_service),
    ] = None,
) -> CallTraversalResponse:
    try:
        result = service.walk_calls(
            symbol_id=symbol_id,
            max_depth=max_depth,
        )
    except TraversalSymbolNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return CallTraversalResponse(
        root_symbol_id=str(result.root.id),
        root_symbol_name=result.root.qualified_name,
        nodes=[
            TraversalNodeResponse(
                symbol_id=str(node.symbol.id),
                symbol_name=node.symbol.qualified_name,
                depth=node.depth,
            )
            for node in result.nodes
        ],
    )


@router.get(
    "/files/{source_file_id}/import-tree",
    response_model=ImportTraversalResponse,
)
def traverse_source_file_imports(
    source_file_id: UUID,
    service: Annotated[
        SourceFileTraversalService,
        Depends(get_source_file_traversal_service),
    ],
    max_depth: int = 3,
) -> ImportTraversalResponse:
    try:
        result = service.walk_imports(
            source_file_id=source_file_id,
            max_depth=max_depth,
        )
    except TraversalSourceFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ImportTraversalResponse(
        root_source_file_id=str(result.root.id),
        root_relative_path=str(result.root.relative_path),
        nodes=[
            FileTraversalNodeResponse(
                source_file_id=str(node.source_file.id),
                relative_path=str(node.source_file.relative_path),
                depth=node.depth,
            )
            for node in result.nodes
        ],
    )


@router.get(
    "/files/{source_file_id}/chunks",
    response_model=ListChunksResponse,
)
def list_source_file_chunks(
    source_file_id: UUID,
) -> ListChunksResponse:
    source_file = source_file_store.get_by_id(source_file_id)

    if source_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source file with id {source_file_id} was not found.",
        )

    snapshot = snapshot_store.get_by_id(source_file.snapshot_id)

    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"Snapshot with id {source_file.snapshot_id} was not found."),
        )

    symbols = symbol_store.list_by_source_file_id(source_file.id)

    file_path = (
        storage_root
        / "repositories"
        / str(snapshot.repository_id)
        / Path(source_file.relative_path.as_posix())
    )

    source = file_path.read_text(encoding="utf-8")

    chunks = SymbolChunker().chunk(
        source_file=source_file,
        symbols=symbols,
        source=source,
    )

    return ListChunksResponse(
        source_file_id=str(source_file.id),
        chunks=[
            ChunkResponse(
                id=str(chunk.id),
                symbol_id=str(chunk.symbol_id),
                qualified_name=chunk.qualified_name,
                symbol_kind=chunk.symbol_kind,
                relative_path=chunk.relative_path,
                language=chunk.language,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                part_index=chunk.part_index,
                part_count=chunk.part_count,
                text=chunk.text,
            )
            for chunk in chunks
        ],
    )


@router.post(
    "/files/{source_file_id}/index",
    response_model=IndexSourceFileResponse,
)
def index_source_file(
    source_file_id: UUID,
) -> IndexSourceFileResponse:
    source_file = source_file_store.get_by_id(source_file_id)

    if source_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source file with id {source_file_id} was not found.",
        )

    snapshot = snapshot_store.get_by_id(source_file.snapshot_id)

    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot with id {source_file.snapshot_id} was not found.",
        )

    symbols = symbol_store.list_by_source_file_id(source_file.id)

    file_path = (
        storage_root
        / "repositories"
        / str(snapshot.repository_id)
        / Path(source_file.relative_path.as_posix())
    )

    source = file_path.read_text(encoding="utf-8")

    chunks = SymbolChunker().chunk(
        source_file=source_file,
        symbols=symbols,
        source=source,
    )
    chunk_store.save_many(chunks)

    use_case = EmbedChunksUseCase(
        embedding_provider=OpenAIEmbeddingProvider(),
        vector_store=vector_store,
        vector_record_mapper=VectorRecordMapper(),
    )

    result = use_case.execute(chunks=chunks)

    return IndexSourceFileResponse(
        source_file_id=str(source_file.id),
        indexed_chunks=result.embedded_chunks,
    )


@router.get(
    "/semantic-search",
    response_model=SemanticSearchResponse,
)
def semantic_search(
    query: str,
    top_k: int = 5,
) -> SemanticSearchResponse:
    use_case = SemanticSearchUseCase(
        embedding_provider=OpenAIEmbeddingProvider(),
        vector_store=vector_store,
    )

    try:
        result = use_case.execute(
            query=query,
            top_k=top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return SemanticSearchResponse(
        query=query,
        results=[
            SemanticSearchItemResponse(
                chunk_id=str(item.record.chunk_id),
                symbol_id=str(item.record.symbol_id),
                qualified_name=item.record.qualified_name,
                relative_path=item.record.relative_path,
                language=item.record.language,
                symbol_kind=item.record.symbol_kind,
                score=item.score,
            )
            for item in result.results
        ],
    )


@router.get(
    "/hybrid-search",
    response_model=HybridSearchResponse,
)
def hybrid_search(
    query: str,
    snapshot_id: UUID,
    use_case: Annotated[
        HybridRetrievalUseCase,
        Depends(get_hybrid_retrieval_use_case),
    ],
    top_k: int = 5,
) -> HybridSearchResponse:
    try:
        result = use_case.execute(
            snapshot_id=snapshot_id,
            query=query,
            top_k=top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return HybridSearchResponse(
        query=query,
        semantic_hits=[
            HybridSemanticHitResponse(
                symbol_id=str(hit.symbol.id),
                qualified_name=hit.symbol.qualified_name,
                kind=hit.symbol.kind.value,
                score=hit.score,
            )
            for hit in result.semantic_hits
        ],
        expanded_symbols=[
            HybridExpandedSymbolResponse(
                symbol_id=str(item.symbol.id),
                qualified_name=item.symbol.qualified_name,
                kind=item.symbol.kind.value,
                relation=item.relation,
                source_symbol_id=item.source_symbol_id,
            )
            for item in result.expanded_symbols
        ],
    )


@router.get(
    "/hybrid-context",
    response_model=HybridContextResponse,
)
def hybrid_context(
    snapshot_id: UUID,
    query: str,
    hybrid_retrieval: Annotated[
        HybridRetrievalUseCase,
        Depends(get_hybrid_retrieval_use_case),
    ],
    context_builder: Annotated[
        RetrievalContextBuilder,
        Depends(get_retrieval_context_builder),
    ],
    top_k: int = 3,
) -> HybridContextResponse:
    try:
        retrieval_result = hybrid_retrieval.execute(
            query=query,
            snapshot_id=snapshot_id,
            top_k=top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    context = context_builder.build(
        retrieval_result=retrieval_result,
    )
    formatted_context = ContextFormatter().format(
        context=context,
    )

    return HybridContextResponse(
        query=query,
        items=[
            RetrievalContextItemResponse(
                symbol_id=str(item.symbol_id),
                qualified_name=item.qualified_name,
                relative_path=item.chunk.relative_path,
                language=item.chunk.language,
                symbol_kind=item.chunk.symbol_kind,
                semantic_score=item.semantic_score,
                semantic_rank=item.semantic_rank,
                graph_relations=list(item.graph_relations),
                text=item.chunk.text,
            )
            for item in context.items
        ],
        formatted_context=formatted_context,
    )


@router.post(
    "/ask",
    response_model=AskRepositoryResponse,
)
def ask_repository(
    request: AskRepositoryRequest,
    use_case: Annotated[
        AnswerRepositoryQuestionUseCase,
        Depends(get_answer_repository_question_use_case),
    ],
) -> AskRepositoryResponse:
    try:
        result = use_case.execute(
            snapshot_id=request.snapshot_id,
            question=request.question,
            top_k=request.top_k,
            max_items=request.max_items,
            max_chars=request.max_chars,
        )
    except SnapshotNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except SnapshotNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return AskRepositoryResponse(
        snapshot_id=str(request.snapshot_id),
        question=request.question,
        answer=result.answer,
        context_items=result.context_items,
        sources=[
            AskRepositorySourceResponse(
                relative_path=source.relative_path,
                qualified_name=source.qualified_name,
                symbol_kind=source.symbol_kind,
                language=source.language,
                start_line=source.start_line,
                end_line=source.end_line,
                semantic_score=source.semantic_score,
                semantic_rank=source.semantic_rank,
                graph_relations=list(source.graph_relations),
                retrieval_origin=source.retrieval_origin.value,
                final_score=source.final_score,
            )
            for source in result.sources
        ],
        retrieval_diagnostics=RetrievalDiagnosticsResponse(
            semantic_sources=(result.retrieval_diagnostics.semantic_sources),
            graph_sources=(result.retrieval_diagnostics.graph_sources),
            both_sources=(result.retrieval_diagnostics.both_sources),
            final_context_items=(result.retrieval_diagnostics.final_context_items),
        ),
    )


@router.post(
    "/{snapshot_id}/index",
    response_model=IndexSnapshotResponse,
)
def index_snapshot(
    snapshot_id: UUID,
    use_case: Annotated[
        IndexSnapshotUseCase,
        Depends(get_index_snapshot_use_case),
    ],
) -> IndexSnapshotResponse:
    try:
        result = use_case.execute(
            snapshot_id=snapshot_id,
        )
    except IndexSnapshotNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return IndexSnapshotResponse(
        snapshot_id=str(result.snapshot_id),
        total_files=result.total_files,
        indexed_files=result.indexed_files,
        skipped_files=result.skipped_files,
        indexed_chunks=result.indexed_chunks,
    )


@router.post(
    "/incremental-index",
    response_model=IncrementalIndexSnapshotResponse,
)
def incremental_index_snapshot(
    request: IncrementalIndexSnapshotRequest,
    use_case: Annotated[
        IncrementalIndexSnapshotUseCase,
        Depends(get_incremental_index_snapshot_use_case),
    ],
) -> IncrementalIndexSnapshotResponse:
    result = use_case.execute(
        previous_snapshot_id=request.previous_snapshot_id,
        current_snapshot_id=request.current_snapshot_id,
    )

    return IncrementalIndexSnapshotResponse(
        previous_snapshot_id=str(result.previous_snapshot_id),
        current_snapshot_id=str(result.current_snapshot_id),
        reused_files=result.reused_files,
        analyzed_files=result.analyzed_files,
        skipped_files=result.skipped_files,
        deleted_files=result.deleted_files,
        reused_symbols=result.reused_symbols,
        reused_symbol_relations=(result.reused_symbol_relations),
        reused_source_file_relations=(result.reused_source_file_relations),
        reused_chunks=result.reused_chunks,
        reused_vectors=result.reused_vectors,
        indexed_chunks=result.indexed_chunks,
    )


@router.delete(
    "/{snapshot_id}",
    response_model=PurgeSnapshotResponse,
)
def purge_snapshot(
    snapshot_id: UUID,
    use_case: Annotated[
        PurgeSnapshotUseCase,
        Depends(get_purge_snapshot_use_case),
    ],
) -> PurgeSnapshotResponse:
    try:
        result = use_case.execute(
            snapshot_id=snapshot_id,
        )
    except PurgeSnapshotNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return PurgeSnapshotResponse(
        snapshot_id=str(result.snapshot_id),
        deleted_vectors=result.deleted_vectors,
        deleted_symbol_relations=(result.deleted_symbol_relations),
        deleted_source_file_relations=(result.deleted_source_file_relations),
        deleted_import_references=(result.deleted_import_references),
        deleted_chunks=result.deleted_chunks,
        deleted_symbols=result.deleted_symbols,
        deleted_source_files=(result.deleted_source_files),
        snapshot_deleted=result.snapshot_deleted,
    )
