import pytest

from tests.evaluation.answer_metrics import (
    evaluate_answer,
)


def test_answer_metrics_full_coverage() -> None:
    answer = (
        "post_fizz calls FizzService.create. "
        "FizzService.create persists a Fizz model. "
        "See app/fizz/controller.py and "
        "app/fizz/service.py."
    )

    metrics = evaluate_answer(
        answer=answer,
        expected_facts=(
            "post_fizz calls FizzService.create",
            "FizzService.create persists a Fizz model",
        ),
        expected_sources=(
            "app/fizz/controller.py",
            "app/fizz/service.py",
        ),
    )

    assert metrics.fact_coverage == 1.0
    assert metrics.source_coverage == 1.0

    assert metrics.matched_fact_count == 2
    assert metrics.matched_source_count == 2


def test_answer_metrics_partial_coverage() -> None:
    answer = "post_fizz calls FizzService.create. See app/fizz/controller.py."

    metrics = evaluate_answer(
        answer=answer,
        expected_facts=(
            "post_fizz calls FizzService.create",
            "FizzService.create persists a Fizz model",
        ),
        expected_sources=(
            "app/fizz/controller.py",
            "app/fizz/service.py",
        ),
    )

    assert metrics.fact_coverage == pytest.approx(0.5)

    assert metrics.source_coverage == pytest.approx(0.5)


def test_answer_metrics_rejects_empty_expected_facts() -> None:
    with pytest.raises(ValueError):
        evaluate_answer(
            answer="Anything",
            expected_facts=(),
            expected_sources=(),
        )
