from dataclasses import dataclass

from tests.evaluation.retrieval_evaluation_runner import (
    RetrievalEvaluationResult,
)


@dataclass(frozen=True, slots=True)
class RetrievalBenchmarkSummary:
    cases: int

    mean_recall: float
    mean_precision: float
    mean_hit_rate: float
    mean_mrr: float
    mean_ndcg: float

    passed_cases: int
    failed_cases: int

    @property
    def pass_rate(self) -> float:
        if self.cases == 0:
            return 0.0

        return self.passed_cases / self.cases


def summarize_retrieval_benchmark(
    *,
    results: tuple[RetrievalEvaluationResult, ...],
) -> RetrievalBenchmarkSummary:
    if not results:
        raise ValueError("results cannot be empty.")

    cases = len(results)

    passed_cases = sum(1 for result in results if result.quality_checks.passed)

    return RetrievalBenchmarkSummary(
        cases=cases,
        mean_recall=(sum(result.metrics.recall for result in results) / cases),
        mean_precision=(sum(result.metrics.precision for result in results) / cases),
        mean_hit_rate=(sum(result.metrics.hit_rate for result in results) / cases),
        mean_mrr=(sum(result.metrics.mrr for result in results) / cases),
        mean_ndcg=(sum(result.metrics.ndcg for result in results) / cases),
        passed_cases=passed_cases,
        failed_cases=(cases - passed_cases),
    )
