from dataclasses import dataclass
from uuid import UUID

from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.application.retrieval.hybrid_reranker import (
    HybridReranker,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalUseCase,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContextBuilder,
    RetrievalOrigin,
)
from codenerva.domain.llm_provider import LLMProvider
from codenerva.domain.snapshot import SnapshotStatus
from codenerva.domain.snapshot_store import SnapshotStore


class SnapshotNotFoundError(Exception):
    pass


class SnapshotNotReadyError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class RepositoryAnswerSource:
    relative_path: str
    qualified_name: str
    symbol_kind: str
    language: str
    start_line: int
    end_line: int
    semantic_score: float | None
    semantic_rank: int | None
    graph_relations: tuple[str, ...]
    retrieval_origin: RetrievalOrigin
    final_score: float


@dataclass(frozen=True, slots=True)
class RetrievalDiagnostics:
    semantic_sources: int
    graph_sources: int
    both_sources: int
    final_context_items: int


@dataclass(frozen=True, slots=True)
class AnswerRepositoryQuestionResult:
    answer: str
    context_items: int
    formatted_context: str
    sources: tuple[RepositoryAnswerSource, ...]
    retrieval_diagnostics: RetrievalDiagnostics


class AnswerRepositoryQuestionUseCase:
    def __init__(
        self,
        *,
        hybrid_retrieval: HybridRetrievalUseCase,
        context_builder: RetrievalContextBuilder,
        context_formatter: ContextFormatter,
        llm_provider: LLMProvider,
        hybrid_reranker: HybridReranker,
        snapshot_store: SnapshotStore,
    ) -> None:
        self._hybrid_retrieval = hybrid_retrieval
        self._context_builder = context_builder
        self._context_formatter = context_formatter
        self._llm_provider = llm_provider
        self._hybrid_reranker = hybrid_reranker
        self._snapshot_store = snapshot_store

    def execute(
        self,
        *,
        snapshot_id: UUID,
        question: str,
        top_k: int = 3,
        max_items: int = 6,
        max_chars: int = 12000,
    ) -> AnswerRepositoryQuestionResult:
        if not question.strip():
            raise ValueError("question cannot be empty.")
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            raise SnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        if snapshot.status is not SnapshotStatus.READY:
            raise SnapshotNotReadyError(
                f"Snapshot with id {snapshot_id} is not ready for questions. "
                f"Current status: {snapshot.status.value}."
            )

        retrieval_result = self._hybrid_retrieval.execute(
            snapshot_id=snapshot_id,
            query=question,
            top_k=top_k,
        )
        rerank_result = self._hybrid_reranker.rerank(
            retrieval_result=retrieval_result,
            question=question,
        )

        context = self._context_builder.build(
            rerank_result=rerank_result,
            question=question,
            max_items=max_items,
            max_chars=max_chars,
        )

        sources = tuple(
            RepositoryAnswerSource(
                relative_path=item.chunk.relative_path,
                qualified_name=item.qualified_name,
                symbol_kind=item.chunk.symbol_kind,
                language=item.chunk.language,
                start_line=item.chunk.start_line,
                end_line=item.chunk.end_line,
                semantic_score=item.semantic_score,
                semantic_rank=item.semantic_rank,
                graph_relations=item.graph_relations,
                retrieval_origin=item.retrieval_origin,
                final_score=item.final_score,
            )
            for item in context.items
        )
        retrieval_diagnostics = RetrievalDiagnostics(
            semantic_sources=sum(
                1
                for source in sources
                if source.retrieval_origin == RetrievalOrigin.SEMANTIC
            ),
            graph_sources=sum(
                1
                for source in sources
                if source.retrieval_origin == RetrievalOrigin.GRAPH
            ),
            both_sources=sum(
                1
                for source in sources
                if source.retrieval_origin == RetrievalOrigin.BOTH
            ),
            final_context_items=len(sources),
        )

        formatted_context = self._context_formatter.format(
            context=context,
        )

        answer = self._llm_provider.generate(
            question=question,
            context=formatted_context,
        )

        return AnswerRepositoryQuestionResult(
            answer=answer,
            context_items=len(context.items),
            formatted_context=formatted_context,
            sources=sources,
            retrieval_diagnostics=retrieval_diagnostics,
        )
