from openai import OpenAI

from codenerva.domain.llm_provider import LLMProvider


class OpenAILLMProvider(LLMProvider):
    def __init__(
        self,
        *,
        model: str = "gpt-5-mini",
        client: OpenAI | None = None,
    ) -> None:
        self._model = model
        self._client = client or OpenAI()

    def generate(
        self,
        *,
        question: str,
        context: str,
    ) -> str:
        response = self._client.responses.create(
            model=self._model,
            store=False,
            instructions=(
                "You are CodeNerva, an assistant that answers "
                "questions about software repositories. "
                "Answer only from the provided repository context. "
                "If the context is insufficient, say that clearly. "
                "Do not invent files, symbols, calls, or behavior. "
                "When useful, mention symbol names and file paths."
            ),
            input=(f"Repository context:\n\n{context}\n\nQuestion:\n{question}"),
        )

        return response.output_text
