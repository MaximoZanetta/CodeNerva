from tests.evaluation.llm_judge import (
    OpenAILLMJudge,
)


class FakeResponses:
    def __init__(
        self,
        *,
        output_text: str,
    ) -> None:
        self._output_text = output_text

    def create(
        self,
        **kwargs,
    ):
        del kwargs

        return FakeResponse(
            output_text=self._output_text,
        )


class FakeResponse:
    def __init__(
        self,
        *,
        output_text: str,
    ) -> None:
        self.output_text = output_text


class FakeOpenAI:
    def __init__(
        self,
        *,
        output_text: str,
    ) -> None:
        self.responses = FakeResponses(
            output_text=output_text,
        )


def test_llm_judge_parses_scores() -> None:
    judge = OpenAILLMJudge(
        client=FakeOpenAI(
            output_text=(
                '{"correctness": 0.9, "groundedness": 1.0, "completeness": 0.8}'
            )
        )
    )

    scores = judge.evaluate(
        question="How does fizz work?",
        answer="The controller calls the service.",
        context="post_fizz calls FizzService.create",
        expected_facts=("post_fizz calls FizzService.create",),
    )

    assert scores.correctness == 0.9
    assert scores.groundedness == 1.0
    assert scores.completeness == 0.8
    assert scores.mean_score == 0.9
