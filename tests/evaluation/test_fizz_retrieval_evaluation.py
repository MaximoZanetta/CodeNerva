from tests.evaluation.evaluation_case import (
    RetrievalEvaluationCase,
)
from tests.evaluation.fizz_fixture import (
    build_fizz_evaluation_fixture,
)
from tests.evaluation.retrieval_evaluation_runner import (
    RetrievalEvaluationRunner,
)


def test_fizz_end_to_end_retrieval_evaluation() -> None:
    fixture = build_fizz_evaluation_fixture()

    case = RetrievalEvaluationCase(
        name="fizz_end_to_end_flow",
        question=(
            "How does the fizz feature work from the API route "
            "through the service and model layers?"
        ),
        expected_symbols=(
            "post_fizz",
            "get_fizz",
            "FizzService.create",
            "FizzService.get_all",
        ),
        minimum_recall=1.0,
        minimum_precision=0.50,
        minimum_mrr=0.50,
        minimum_ndcg=0.70,
    )

    runner = RetrievalEvaluationRunner(
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
    )

    result = runner.run(
        case=case,
        snapshot_id=fixture.snapshot_id,
    )

    assert result.quality_checks.passed
    assert "fizz" not in result.retrieved_symbols


def test_fizz_service_structure_retrieval_evaluation() -> None:
    fixture = build_fizz_evaluation_fixture()

    case = RetrievalEvaluationCase(
        name="fizz_service_structure",
        question="What methods belong to FizzService?",
        expected_symbols=(
            "FizzService.create",
            "FizzService.get_all",
        ),
        minimum_recall=1.0,
        minimum_precision=0.40,
        minimum_mrr=0.50,
        minimum_ndcg=0.70,
    )

    runner = RetrievalEvaluationRunner(
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
    )

    result = runner.run(
        case=case,
        snapshot_id=fixture.snapshot_id,
    )

    assert result.quality_checks.passed


def test_fizz_testing_retrieval_evaluation() -> None:
    fixture = build_fizz_evaluation_fixture()

    case = RetrievalEvaluationCase(
        name="fizz_testing",
        question="How is the Fizz model tested?",
        expected_symbols=("fizz",),
        minimum_recall=1.0,
        minimum_precision=0.20,
        minimum_mrr=0.25,
        minimum_ndcg=0.50,
    )

    runner = RetrievalEvaluationRunner(
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
    )

    result = runner.run(
        case=case,
        snapshot_id=fixture.snapshot_id,
    )

    assert result.quality_checks.passed
