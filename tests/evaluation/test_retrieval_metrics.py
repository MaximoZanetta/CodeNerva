import pytest

from tests.evaluation.retrieval_metrics import (
    evaluate_retrieval,
)


def test_evaluate_retrieval_perfect_recall() -> None:
    metrics = evaluate_retrieval(
        expected_symbols=(
            "post_fizz",
            "FizzService.create",
            "Fizz",
        ),
        retrieved_symbols=(
            "post_fizz",
            "FizzService.create",
            "Fizz",
            "FizzService",
        ),
    )

    assert metrics.recall == 1.0

    assert metrics.precision == pytest.approx(0.75)

    assert metrics.hit_rate == 1.0

    assert metrics.expected_count == 3
    assert metrics.retrieved_count == 4
    assert metrics.relevant_retrieved_count == 3


def test_evaluate_retrieval_partial_recall() -> None:
    metrics = evaluate_retrieval(
        expected_symbols=(
            "post_fizz",
            "FizzService.create",
            "Fizz",
        ),
        retrieved_symbols=(
            "post_fizz",
            "FizzService",
        ),
    )

    assert metrics.recall == pytest.approx(1 / 3)

    assert metrics.precision == pytest.approx(0.5)

    assert metrics.hit_rate == 1.0

    assert metrics.mrr == 1.0

    assert metrics.ndcg == pytest.approx(0.6131471927654584)


def test_evaluate_retrieval_no_hits() -> None:
    metrics = evaluate_retrieval(
        expected_symbols=(
            "post_fizz",
            "FizzService.create",
        ),
        retrieved_symbols=("unrelated",),
    )

    assert metrics.recall == 0.0
    assert metrics.precision == 0.0
    assert metrics.hit_rate == 0.0


def test_evaluate_retrieval_rejects_empty_expected_symbols() -> None:
    with pytest.raises(ValueError):
        evaluate_retrieval(
            expected_symbols=(),
            retrieved_symbols=("post_fizz",),
        )


def test_evaluate_retrieval_rewards_better_ranking() -> None:
    expected = (
        "post_fizz",
        "FizzService.create",
    )

    better = evaluate_retrieval(
        expected_symbols=expected,
        retrieved_symbols=(
            "post_fizz",
            "FizzService.create",
            "unrelated",
        ),
    )

    worse = evaluate_retrieval(
        expected_symbols=expected,
        retrieved_symbols=(
            "unrelated",
            "post_fizz",
            "FizzService.create",
        ),
    )

    assert better.recall == worse.recall
    assert better.precision == worse.precision

    assert better.mrr > worse.mrr
    assert better.ndcg > worse.ndcg
