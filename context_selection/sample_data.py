
from context_selection.models import ContextCandidate


def create_sample_candidates():
    """
    Create deterministic candidates from all
    three supported memory sources.
    """

    return [
        ContextCandidate(
            candidate_id="STM001",
            text="User is currently learning Python.",
            source="short_term",
            relevance=9,
            recency=10,
            priority=8,
            token_count=12
        ),

        ContextCandidate(
            candidate_id="LTM001",
            text="User prefers backend development.",
            source="long_term",
            relevance=8,
            recency=6,
            priority=9,
            token_count=11
        ),

        ContextCandidate(
            candidate_id="VEC001",
            text="Python programming concepts and examples.",
            source="vector",
            relevance=10,
            recency=7,
            priority=7,
            token_count=15
        ),

        ContextCandidate(
            candidate_id="STM002",
            text="User recently completed a coding exercise.",
            source="short_term",
            relevance=7,
            recency=9,
            priority=6,
            token_count=13
        ),

        ContextCandidate(
            candidate_id="LTM002",
            text="User has experience with machine learning.",
            source="long_term",
            relevance=8,
            recency=5,
            priority=8,
            token_count=14
        )
    ]
