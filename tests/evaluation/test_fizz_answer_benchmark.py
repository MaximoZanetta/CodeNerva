import os

import pytest

from codenerva.application.qa.answer_repository_question import (
    AnswerRepositoryQuestionUseCase,
)
from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.infrastructure.openai_llm_provider import (
    OpenAILLMProvider,
)
from tests.evaluation.answer_benchmark import (
    AnswerBenchmarkCaseResult,
    summarize_answer_benchmark,
)
from tests.evaluation.fizz_fixture import (
    END_TO_END_QUESTION,
    INSUFFICIENT_CONTEXT_QUESTION,
    PARTIAL_EVIDENCE_QUESTION,
    STRUCTURE_QUESTION,
    TESTING_QUESTION,
    build_fizz_evaluation_fixture,
)
from tests.evaluation.llm_judge import (
    OpenAILLMJudge,
)

pytestmark = pytest.mark.llm_eval


def test_fizz_answer_benchmark() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for llm evaluation.")

    fixture = build_fizz_evaluation_fixture()

    answer_use_case = AnswerRepositoryQuestionUseCase(
        snapshot_store=fixture.snapshot_store,
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
        context_formatter=ContextFormatter(),
        llm_provider=OpenAILLMProvider(
            model="gpt-5-mini",
        ),
    )

    judge = OpenAILLMJudge(
        model="gpt-5-mini",
    )

    cases = (
        (
            "end_to_end",
            END_TO_END_QUESTION,
            (
                "post_fizz calls FizzService.create",
                "get_fizz calls FizzService.get_all",
                "FizzService.create persists a Fizz model",
                "FizzService.get_all queries Fizz rows",
                "FizzSchema is used between the API and service layers",
            ),
        ),
        (
            "structure",
            STRUCTURE_QUESTION,
            (
                "FizzService contains FizzService.create",
                "FizzService contains FizzService.get_all",
            ),
        ),
        (
            "testing",
            TESTING_QUESTION,
            (
                "The Fizz model test helper is defined in app/fizz/model_test.py",
                "The fizz test helper creates a Fizz model",
            ),
        ),
        (
            "insufficient_context",
            INSUFFICIENT_CONTEXT_QUESTION,
            (
                (
                    "The provided repository context does not contain enough "
                    "evidence to determine the authentication mechanism."
                ),
                (
                    "The provided repository context does not contain enough "
                    "evidence to determine how access tokens are validated."
                ),
            ),
        ),
        (
            "partial_evidence",
            PARTIAL_EVIDENCE_QUESTION,
            (
                "FizzService.create creates a Fizz model from FizzSchema.",
                "FizzService.create adds the Fizz model to the database session.",
                "FizzService.create commits the database session.",
                (
                    "The provided context does not establish what happens "
                    "if the database commit fails."
                ),
            ),
        ),
    )

    benchmark_results: list[AnswerBenchmarkCaseResult] = []

    for name, question, expected_facts in cases:
        result = answer_use_case.execute(
            snapshot_id=fixture.snapshot_id,
            question=question,
            top_k=4,
            max_items=8,
            max_chars=16000,
        )

        scores = judge.evaluate(
            question=question,
            answer=result.answer,
            context=result.formatted_context,
            expected_facts=expected_facts,
        )

        passed = (
            scores.correctness >= 0.80
            and scores.groundedness >= 0.85
            and scores.completeness >= 0.75
        )

        benchmark_results.append(
            AnswerBenchmarkCaseResult(
                name=name,
                scores=scores,
                passed=passed,
            )
        )

    summary = summarize_answer_benchmark(
        results=tuple(benchmark_results),
    )

    print()
    print("CodeNerva Answer Benchmark")
    print(f"Cases:               {summary.cases}")
    print(f"Passed:              {summary.passed_cases}")
    print(f"Failed:              {summary.failed_cases}")
    print(f"Pass rate:           {summary.pass_rate:.3f}")
    print()
    print(f"Mean correctness:    {summary.mean_correctness:.3f}")
    print(f"Mean groundedness:   {summary.mean_groundedness:.3f}")
    print(f"Mean completeness:   {summary.mean_completeness:.3f}")
    print(f"Mean score:          {summary.mean_score:.3f}")

    assert summary.failed_cases == 0
    assert summary.pass_rate == 1.0

    assert summary.mean_correctness >= 0.80
    assert summary.mean_groundedness >= 0.85
    assert summary.mean_completeness >= 0.75
