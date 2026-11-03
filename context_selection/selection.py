
from context_selection.scoring import rank_candidates


def select_context(
    candidates,
    budget,
    feature_weights=None,
    source_weights=None
):
    """
    Select ranked context candidates within a token budget.

    Candidates that do not fit are excluded, but selection
    continues with the remaining candidates.

    Returns selected candidates, excluded candidates,
    scores, and budget usage.
    """

    if (
        isinstance(budget, bool)
        or not isinstance(budget, int)
        or budget < 0
    ):
        raise ValueError(
            "Budget must be a non-negative integer"
        )

    ranked = rank_candidates(
        candidates,
        feature_weights=feature_weights,
        source_weights=source_weights
    )

    selected = []
    excluded = []

    used_tokens = 0

    for candidate, score in ranked:
        remaining_budget = budget - used_tokens

        if candidate.token_count <= remaining_budget:
            selected.append({
                "candidate": candidate,
                "score": score
            })

            used_tokens += candidate.token_count

        else:
            excluded.append({
                "candidate": candidate,
                "score": score,
                "reason": "exceeds_remaining_budget",
                "remaining_budget": remaining_budget
            })

    return {
        "selected": selected,
        "excluded": excluded,
        "budget": budget,
        "used_tokens": used_tokens,
        "remaining_tokens": budget - used_tokens
    }
