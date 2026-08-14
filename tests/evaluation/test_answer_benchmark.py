import pytest

from tests.evaluation.answer_benchmark import (
    AnswerBenchmarkCaseResult,
    summarize_answer_benchmark,
)
from tests.evaluation.llm_judge import (
    LLMJudgeScores,
)


def test_summarize_answer_benchmark() -> None:
    results = (
        AnswerBenchmarkCaseResult(
            name="end_to_end",
            scores=LLMJudgeScores(
                correctness=1.0,
                groundedness=1.0,
                completeness=0.9,
            ),
            passed=True,
        ),
        AnswerBenchmarkCaseResult(
            name="structure",
            scores=LLMJudgeScores(
                correctness=1.0,
                groundedness=1.0,
                completeness=1.0,
            ),
            passed=True,
        ),
        AnswerBenchmarkCaseResult(
            name="testing",
            scores=LLMJudgeScores(
                correctness=1.0,
                groundedness=1.0,
                completeness=1.0,
            ),
            passed=True,
        ),
    )

    summary = summarize_answer_benchmark(
        results=results,
    )

    assert summary.cases == 3

    assert summary.mean_correctness == pytest.approx(1.0)

    assert summary.mean_groundedness == pytest.approx(1.0)

    assert summary.mean_completeness == pytest.approx(0.9666666667)

    assert summary.mean_score == pytest.approx(((1.0 + 1.0 + 0.9) / 3 + 1.0 + 1.0) / 3)

    assert summary.passed_cases == 3
    assert summary.failed_cases == 0
    assert summary.pass_rate == 1.0


def test_summarize_answer_benchmark_rejects_empty_results() -> None:
    with pytest.raises(ValueError):
        summarize_answer_benchmark(results=())
