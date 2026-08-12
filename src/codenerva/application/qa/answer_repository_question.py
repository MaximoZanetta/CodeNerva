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
)
from codenerva.domain.llm_provider import LLMProvider
from codenerva.domain.snapshot_store import SnapshotStore


class SnapshotNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class AnswerRepositoryQuestionResult:
    answer: str
    context_items: int


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

        retrieval_result = self._hybrid_retrieval.execute(
            snapshot_id=snapshot_id,
            query=question,
            top_k=top_k,
        )
        rerank_result = self._hybrid_reranker.rerank(
            retrieval_result=retrieval_result,
        )

        context = self._context_builder.build(
            rerank_result=rerank_result,
            max_items=max_items,
            max_chars=max_chars,
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
        )
