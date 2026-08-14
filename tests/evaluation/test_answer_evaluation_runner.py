from uuid import uuid4

from tests.evaluation.answer_evaluation_case import (
    AnswerEvaluationCase,
)
from tests.evaluation.answer_evaluation_runner import (
    AnswerEvaluationRunner,
)


class FakeAnswerRepositoryQuestionUseCase:
    def __init__(
        self,
        *,
        answer: str,
    ) -> None:
        self._answer = answer

    def execute(
        self,
        *,
        snapshot_id,
        question: str,
    ):
        del snapshot_id
        del question

        return FakeAnswerResult(
            answer=self._answer,
        )


class FakeAnswerResult:
    def __init__(
        self,
        *,
        answer: str,
    ) -> None:
        self.answer = answer


def test_answer_evaluation_runner_evaluates_answer() -> None:
    case = AnswerEvaluationCase(
        name="fizz_answer",
        question=("How does fizz creation work?"),
        expected_facts=(
            "post_fizz calls FizzService.create",
            "FizzService.create persists a Fizz model",
        ),
        expected_sources=(
            "app/fizz/controller.py",
            "app/fizz/service.py",
        ),
        minimum_fact_coverage=1.0,
        minimum_source_coverage=1.0,
    )

    use_case = FakeAnswerRepositoryQuestionUseCase(
        answer=(
            "post_fizz calls FizzService.create. "
            "FizzService.create persists a Fizz model. "
            "See app/fizz/controller.py and "
            "app/fizz/service.py."
        )
    )

    runner = AnswerEvaluationRunner(
        answer_repository_question=use_case,
    )

    result = runner.run(
        case=case,
        snapshot_id=uuid4(),
    )

    assert result.quality_checks.passed

    assert result.metrics.fact_coverage == 1.0
    assert result.metrics.source_coverage == 1.0
