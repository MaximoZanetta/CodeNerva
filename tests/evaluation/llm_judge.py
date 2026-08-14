import json
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True, slots=True)
class LLMJudgeScores:
    correctness: float
    groundedness: float
    completeness: float

    @property
    def mean_score(self) -> float:
        return (self.correctness + self.groundedness + self.completeness) / 3


class OpenAILLMJudge:
    def __init__(
        self,
        *,
        model: str = "gpt-5-mini",
        client: OpenAI | None = None,
    ) -> None:
        self._model = model
        self._client = client or OpenAI()

    def evaluate(
        self,
        *,
        question: str,
        answer: str,
        context: str,
        expected_facts: tuple[str, ...],
    ) -> LLMJudgeScores:
        expected_facts_text = "\n".join(f"- {fact}" for fact in expected_facts)

        response = self._client.responses.create(
            model=self._model,
            store=False,
            instructions=(
                "You are evaluating an answer produced by a "
                "repository question-answering system. "
                "Score three dimensions from 0.0 to 1.0. "
                "Correctness: whether the answer's claims are correct. "
                "Groundedness: whether claims are supported by the "
                "provided repository context, with no invented behavior. "
                "Completeness: whether the answer covers the important "
                "facts required to answer the question. "
                "Do not reward verbosity. "
                "Return only valid JSON with exactly these keys: "
                "correctness, groundedness, completeness."
            ),
            input=(
                f"Question:\n{question}\n\n"
                f"Repository context:\n{context}\n\n"
                f"Expected facts:\n{expected_facts_text}\n\n"
                f"Answer to evaluate:\n{answer}"
            ),
        )

        data = json.loads(response.output_text)

        return LLMJudgeScores(
            correctness=self._validate_score(data["correctness"]),
            groundedness=self._validate_score(data["groundedness"]),
            completeness=self._validate_score(data["completeness"]),
        )

    def _validate_score(
        self,
        value: object,
    ) -> float:
        if not isinstance(
            value,
            (int, float),
        ):
            raise TypeError("Judge scores must be numeric.")

        score = float(value)

        if not 0.0 <= score <= 1.0:
            raise TypeError("Judge scores must be between 0 and 1.")

        return score
