from codenerva.application.qa.answer_repository_question import (
    AnswerRepositoryQuestionUseCase,
)
from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.infrastructure.fake_llm_provider import (
    FakeLLMProvider,
)
from tests.evaluation.answer_evaluation_case import (
    AnswerEvaluationCase,
)
from tests.evaluation.answer_evaluation_runner import (
    AnswerEvaluationRunner,
)
from tests.evaluation.fizz_fixture import (
    END_TO_END_QUESTION,
    build_fizz_evaluation_fixture,
)


def test_fizz_end_to_end_answer_evaluation() -> None:
    fixture = build_fizz_evaluation_fixture()

    llm_provider = FakeLLMProvider(
        answer=(
            "post_fizz calls FizzService.create. "
            "FizzService.create persists a Fizz model. "
            "get_fizz calls FizzService.get_all. "
            "FizzService.get_all queries Fizz rows. "
            "FizzSchema is used between the API and service layers. "
            "See app/fizz/controller.py, app/fizz/service.py, "
            "app/fizz/model.py and app/fizz/schema.py."
        )
    )

    answer_use_case = AnswerRepositoryQuestionUseCase(
        snapshot_store=fixture.snapshot_store,
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
        context_formatter=ContextFormatter(),
        llm_provider=llm_provider,
    )

    case = AnswerEvaluationCase(
        name="fizz_end_to_end_answer",
        question=END_TO_END_QUESTION,
        expected_facts=(
            "post_fizz calls FizzService.create",
            "FizzService.create persists a Fizz model",
            "get_fizz calls FizzService.get_all",
            "FizzService.get_all queries Fizz rows",
            "FizzSchema is used between the API and service layers",
        ),
        expected_sources=(
            "app/fizz/controller.py",
            "app/fizz/service.py",
            "app/fizz/model.py",
            "app/fizz/schema.py",
        ),
        minimum_fact_coverage=1.0,
        minimum_source_coverage=1.0,
    )

    runner = AnswerEvaluationRunner(
        answer_repository_question=answer_use_case,
    )

    result = runner.run(
        case=case,
        snapshot_id=fixture.snapshot_id,
    )

    assert result.quality_checks.passed

    assert result.metrics.fact_coverage == 1.0
    assert result.metrics.source_coverage == 1.0
