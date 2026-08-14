from dataclasses import dataclass

from tests.evaluation.llm_judge import (
    LLMJudgeScores,
)


@dataclass(frozen=True, slots=True)
class AnswerBenchmarkSummary:
    cases: int

    mean_correctness: float
    mean_groundedness: float
    mean_completeness: float
    mean_score: float

    passed_cases: int
    failed_cases: int

    @property
    def pass_rate(self) -> float:
        if self.cases == 0:
            return 0.0

        return self.passed_cases / self.cases


@dataclass(frozen=True, slots=True)
class AnswerBenchmarkCaseResult:
    name: str
    scores: LLMJudgeScores
    passed: bool


def summarize_answer_benchmark(
    *,
    results: tuple[AnswerBenchmarkCaseResult, ...],
) -> AnswerBenchmarkSummary:
    if not results:
        raise ValueError("results cannot be empty.")

    cases = len(results)

    passed_cases = sum(1 for result in results if result.passed)

    return AnswerBenchmarkSummary(
        cases=cases,
        mean_correctness=(sum(result.scores.correctness for result in results) / cases),
        mean_groundedness=(
            sum(result.scores.groundedness for result in results) / cases
        ),
        mean_completeness=(
            sum(result.scores.completeness for result in results) / cases
        ),
        mean_score=(sum(result.scores.mean_score for result in results) / cases),
        passed_cases=passed_cases,
        failed_cases=(cases - passed_cases),
    )
