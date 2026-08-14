from dataclasses import dataclass
from uuid import UUID

from codenerva.application.retrieval.hybrid_reranker import (
    HybridReranker,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalUseCase,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContextBuilder,
)
from tests.evaluation.evaluation_case import (
    RetrievalEvaluationCase,
)
from tests.evaluation.retrieval_metrics import (
    RetrievalMetrics,
    evaluate_retrieval,
)


@dataclass(frozen=True, slots=True)
class RetrievalQualityChecks:
    recall_passed: bool
    precision_passed: bool
    mrr_passed: bool
    ndcg_passed: bool

    @property
    def passed(self) -> bool:
        return (
            self.recall_passed
            and self.precision_passed
            and self.mrr_passed
            and self.ndcg_passed
        )


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationResult:
    case: RetrievalEvaluationCase
    retrieved_symbols: tuple[str, ...]
    metrics: RetrievalMetrics
    quality_checks: RetrievalQualityChecks


class RetrievalEvaluationRunner:
    def __init__(
        self,
        *,
        hybrid_retrieval: HybridRetrievalUseCase,
        hybrid_reranker: HybridReranker,
        context_builder: RetrievalContextBuilder,
    ) -> None:
        self._hybrid_retrieval = hybrid_retrieval
        self._hybrid_reranker = hybrid_reranker
        self._context_builder = context_builder

    def run(
        self,
        *,
        case: RetrievalEvaluationCase,
        snapshot_id: UUID,
    ) -> RetrievalEvaluationResult:
        retrieval_result = self._hybrid_retrieval.execute(
            query=case.question,
            snapshot_id=snapshot_id,
            top_k=case.top_k,
        )

        rerank_result = self._hybrid_reranker.rerank(
            retrieval_result=retrieval_result,
            question=case.question,
        )

        context = self._context_builder.build(
            rerank_result=rerank_result,
            question=case.question,
            max_items=case.max_items,
            max_chars=case.max_chars,
        )

        retrieved_symbols = tuple(item.qualified_name for item in context.items)

        metrics = evaluate_retrieval(
            expected_symbols=case.expected_symbols,
            retrieved_symbols=retrieved_symbols,
        )

        quality_checks = evaluate_quality(
            case=case,
            metrics=metrics,
        )

        return RetrievalEvaluationResult(
            case=case,
            retrieved_symbols=retrieved_symbols,
            metrics=metrics,
            quality_checks=quality_checks,
        )


def evaluate_quality(
    *,
    case: RetrievalEvaluationCase,
    metrics: RetrievalMetrics,
) -> RetrievalQualityChecks:
    return RetrievalQualityChecks(
        recall_passed=(metrics.recall >= case.minimum_recall),
        precision_passed=(metrics.precision >= case.minimum_precision),
        mrr_passed=(metrics.mrr >= case.minimum_mrr),
        ndcg_passed=(metrics.ndcg >= case.minimum_ndcg),
    )
