import pytest

from tests.evaluation.evaluation_case import (
    RetrievalEvaluationCase,
)
from tests.evaluation.retrieval_benchmark import (
    summarize_retrieval_benchmark,
)
from tests.evaluation.retrieval_evaluation_runner import (
    RetrievalEvaluationResult,
    RetrievalQualityChecks,
)
from tests.evaluation.retrieval_metrics import (
    RetrievalMetrics,
)


def test_summarize_retrieval_benchmark() -> None:
    case_a = RetrievalEvaluationCase(
        name="case_a",
        question="Question A",
        expected_symbols=("a",),
    )

    case_b = RetrievalEvaluationCase(
        name="case_b",
        question="Question B",
        expected_symbols=("b",),
    )

    result_a = RetrievalEvaluationResult(
        case=case_a,
        retrieved_symbols=("a",),
        metrics=RetrievalMetrics(
            recall=1.0,
            precision=1.0,
            hit_rate=1.0,
            mrr=1.0,
            ndcg=1.0,
            expected_count=1,
            retrieved_count=1,
            relevant_retrieved_count=1,
        ),
        quality_checks=RetrievalQualityChecks(
            recall_passed=True,
            precision_passed=True,
            mrr_passed=True,
            ndcg_passed=True,
        ),
    )

    result_b = RetrievalEvaluationResult(
        case=case_b,
        retrieved_symbols=(
            "unrelated",
            "b",
        ),
        metrics=RetrievalMetrics(
            recall=0.5,
            precision=0.5,
            hit_rate=1.0,
            mrr=0.5,
            ndcg=0.6,
            expected_count=2,
            retrieved_count=2,
            relevant_retrieved_count=1,
        ),
        quality_checks=RetrievalQualityChecks(
            recall_passed=False,
            precision_passed=True,
            mrr_passed=True,
            ndcg_passed=False,
        ),
    )

    summary = summarize_retrieval_benchmark(
        results=(
            result_a,
            result_b,
        )
    )

    assert summary.cases == 2

    assert summary.mean_recall == pytest.approx(0.75)

    assert summary.mean_precision == pytest.approx(0.75)

    assert summary.mean_hit_rate == 1.0

    assert summary.mean_mrr == pytest.approx(0.75)

    assert summary.mean_ndcg == pytest.approx(0.8)

    assert summary.passed_cases == 1
    assert summary.failed_cases == 1

    assert summary.pass_rate == pytest.approx(0.5)


def test_summarize_retrieval_benchmark_rejects_empty_results() -> None:
    with pytest.raises(ValueError):
        summarize_retrieval_benchmark(results=())
