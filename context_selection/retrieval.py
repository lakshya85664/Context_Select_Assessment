
from context_selection.models import ContextCandidate


def retrieve_vector_candidates(
    query,
    vector_store,
    min_relevance=7.0
):
    """
    Simulate vector retrieval using pre-scored candidates.

    In a real vector database, relevance would come from
    embedding similarity. Here it is supplied in the data.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query cannot be empty")

    if not isinstance(min_relevance, (int, float)) or isinstance(
        min_relevance, bool
    ) or not 0 <= min_relevance <= 10:
        raise ValueError("Minimum relevance must be between 0 and 10")

    results = [
        candidate
        for candidate in vector_store
        if candidate.source == "vector"
        and candidate.relevance >= min_relevance
    ]

    return sorted(
        results,
        key=lambda candidate: (
            -candidate.relevance,
            candidate.candidate_id
        )
    )


def summarize_history(history, max_items=3):
    """
    Create a deterministic extractive summary from
    older historical memory entries.

    Keeps the first max_items high-signal entries.
    """

    if not isinstance(history, list):
        raise ValueError("History must be a list")

    if isinstance(max_items, bool) or not isinstance(max_items, int):
        raise ValueError("max_items must be an integer")

    if max_items <= 0:
        raise ValueError("max_items must be positive")

    if any(
        not isinstance(item, str) or not item.strip()
        for item in history
    ):
        raise ValueError("History entries must be non-empty strings")

    selected_items = history[:max_items]

    if not selected_items:
        return ""

    return "Historical summary: " + " | ".join(selected_items)


def create_summary_candidate(
    history,
    candidate_id="SUM001",
    max_items=3
):
    """
    Convert historical information into a compact
    long-term memory candidate.
    """

    summary = summarize_history(history, max_items)

    if not summary:
        return None

    return ContextCandidate(
        candidate_id=candidate_id,
        text=summary,
        source="long_term",
        relevance=9,
        recency=3,
        priority=9,
        token_count=max(1, len(summary.split()))
    )


def collect_context_candidates(
    existing_candidates,
    vector_store,
    history,
    query
):
    """
    Combine existing memory candidates, relevant vector
    retrieval results, and a summarized history candidate.
    """

    combined = list(existing_candidates)

    retrieved = retrieve_vector_candidates(
        query=query,
        vector_store=vector_store,
        min_relevance=7
    )

    combined.extend(retrieved)

    summary = create_summary_candidate(history)

    if summary is not None:
        combined.append(summary)

    ids = [candidate.candidate_id for candidate in combined]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate candidate IDs detected")

    return combined


def explain_selection(result):
    """
    Explain why candidates were selected or excluded.
    """

    explanations = []

    for item in result["selected"]:
        candidate = item["candidate"]

        explanations.append({
            "candidate_id": candidate.candidate_id,
            "decision": "selected",
            "score": item["score"],
            "reason": (
                "High-ranked candidate that fits within "
                "the remaining context budget."
            )
        })

    for item in result["excluded"]:
        candidate = item["candidate"]

        explanations.append({
            "candidate_id": candidate.candidate_id,
            "decision": "excluded",
            "score": item["score"],
            "reason": (
                f"Requires {candidate.token_count} tokens, "
                f"but only {item['remaining_budget']} "
                "tokens remained."
            )
        })

    return explanations
