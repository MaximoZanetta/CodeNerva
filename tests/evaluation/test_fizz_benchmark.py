from tests.evaluation.fizz_cases import (
    FIZZ_RETRIEVAL_CASES,
)
from tests.evaluation.fizz_fixture import (
    build_fizz_evaluation_fixture,
)
from tests.evaluation.retrieval_benchmark import (
    summarize_retrieval_benchmark,
)
from tests.evaluation.retrieval_evaluation_runner import (
    RetrievalEvaluationRunner,
)


def test_fizz_retrieval_benchmark() -> None:
    fixture = build_fizz_evaluation_fixture()

    runner = RetrievalEvaluationRunner(
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
    )

    results = tuple(
        runner.run(
            case=case,
            snapshot_id=fixture.snapshot_id,
        )
        for case in FIZZ_RETRIEVAL_CASES
    )

    summary = summarize_retrieval_benchmark(
        results=results,
    )

    assert summary.cases == 3
    assert summary.failed_cases == 0
    assert summary.passed_cases == 3
    assert summary.pass_rate == 1.0

    assert summary.mean_recall >= 0.95
    assert summary.mean_precision >= 0.40
    assert summary.mean_mrr >= 0.50
    assert summary.mean_ndcg >= 0.70
