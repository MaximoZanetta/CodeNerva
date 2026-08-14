from dataclasses import dataclass
from uuid import UUID

from codenerva.application.qa.answer_repository_question import (
    AnswerRepositoryQuestionUseCase,
)
from tests.evaluation.answer_evaluation_case import (
    AnswerEvaluationCase,
)
from tests.evaluation.answer_metrics import (
    AnswerMetrics,
    evaluate_answer,
)


@dataclass(frozen=True, slots=True)
class AnswerQualityChecks:
    fact_coverage_passed: bool
    source_coverage_passed: bool

    @property
    def passed(self) -> bool:
        return self.fact_coverage_passed and self.source_coverage_passed


@dataclass(frozen=True, slots=True)
class AnswerEvaluationResult:
    case: AnswerEvaluationCase
    answer: str
    metrics: AnswerMetrics
    quality_checks: AnswerQualityChecks


class AnswerEvaluationRunner:
    def __init__(
        self,
        *,
        answer_repository_question: AnswerRepositoryQuestionUseCase,
    ) -> None:
        self._answer_repository_question = answer_repository_question

    def run(
        self,
        *,
        case: AnswerEvaluationCase,
        snapshot_id: UUID,
    ) -> AnswerEvaluationResult:
        result = self._answer_repository_question.execute(
            snapshot_id=snapshot_id,
            question=case.question,
        )

        metrics = evaluate_answer(
            answer=result.answer,
            expected_facts=case.expected_facts,
            expected_sources=case.expected_sources,
        )

        quality_checks = AnswerQualityChecks(
            fact_coverage_passed=(metrics.fact_coverage >= case.minimum_fact_coverage),
            source_coverage_passed=(
                metrics.source_coverage >= case.minimum_source_coverage
            ),
        )

        return AnswerEvaluationResult(
            case=case,
            answer=result.answer,
            metrics=metrics,
            quality_checks=quality_checks,
        )
