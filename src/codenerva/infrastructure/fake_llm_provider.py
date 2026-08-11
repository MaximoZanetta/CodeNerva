from codenerva.domain.llm_provider import LLMProvider


class FakeLLMProvider(LLMProvider):
    def __init__(
        self,
        *,
        answer: str = "Test answer.",
    ) -> None:
        self._answer = answer
        self.last_question: str | None = None
        self.last_context: str | None = None

    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str:
        self.last_question = question
        self.last_context = context

        return self._answer
