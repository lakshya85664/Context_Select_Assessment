
from dataclasses import dataclass
from typing import Literal


MemorySource = Literal[
    "short_term",
    "long_term",
    "vector"
]


@dataclass
class ContextCandidate:
    candidate_id: str
    text: str
    source: MemorySource
    relevance: float
    recency: float
    priority: float
    token_count: int

    def __post_init__(self):
        if not self.candidate_id.strip():
            raise ValueError("Candidate ID cannot be empty")

        if not self.text.strip():
            raise ValueError("Candidate text cannot be empty")

        if self.source not in (
            "short_term",
            "long_term",
            "vector"
        ):
            raise ValueError("Invalid memory source")

        for field_name in (
            "relevance",
            "recency",
            "priority"
        ):
            value = getattr(self, field_name)

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"{field_name} must be numeric"
                )

            if not 0 <= value <= 10:
                raise ValueError(
                    f"{field_name} must be between 0 and 10"
                )

        if isinstance(self.token_count, bool) or not isinstance(
            self.token_count, int
        ) or self.token_count <= 0:
            raise ValueError(
                "Token count must be a positive integer"
            )
