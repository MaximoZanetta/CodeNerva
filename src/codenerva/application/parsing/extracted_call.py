from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedCall:
    caller_name: str
    callee_name: str
    line: int
    owner_name: str | None = None
