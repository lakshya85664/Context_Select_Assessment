# Topic 12 — Context Selection Assessment

## Project Overview

This project implements a deterministic context-selection pipeline for an LLM-based agent. It combines candidate memories from short-term memory, long-term memory, and simulated vector retrieval; scores and ranks them; selects candidates under a token budget; summarizes historical information; and produces inspection reports explaining selection behavior.

The implementation is intentionally self-contained and does not require an external embedding model, vector database, or LLM API. Vector retrieval is simulated using pre-scored candidates so that behavior is reproducible and testable.

## Objectives

- Define a validated, consistent context-candidate model.
- Score candidates using relevance, recency, priority, and source weighting.
- Rank candidates deterministically.
- Select candidates without exceeding a configurable token budget.
- Continue considering later candidates when a higher-ranked candidate does not fit.
- Simulate vector retrieval and summarize historical information.
- Explain selected and excluded candidates.
- Inspect budget utilization, selection rate, source distribution, and average selected score.
- Compare alternative scoring policies.

## Project Structure

```text
Context_Selection_Assessment/
├── context_selection/
│   ├── __init__.py
│   ├── models.py
│   ├── sample_data.py
│   ├── scoring.py
│   ├── selection.py
│   ├── retrieval.py
│   └── policy.py
├── tests/
│   ├── test_task1.py
│   ├── test_task2.py
│   ├── test_task3.py
│   ├── test_task4.py
│   └── test_task5.py
├── outputs/
├── README.md
├── requirements.txt
└── .gitignore
```

## Exercise 1 — Context Candidate Model

`ContextCandidate` is a dataclass containing a candidate ID, memory text, source, relevance, recency, priority, and token count. Supported sources are `short_term`, `long_term`, and `vector`.

Validation rejects empty identifiers or text, unsupported sources, feature values outside the 0–10 range, and invalid token counts. Sample candidates are deterministic to make test results repeatable.

## Exercise 2 — Scoring and Ranking

The default score is calculated as:

`(relevance × 0.50 + recency × 0.20 + priority × 0.30) × source_weight`

Default source weights are:

- Short-term: 1.00
- Long-term: 0.95
- Vector: 1.05

Feature weights are configurable and must be non-negative and sum to 1. Source weights must be positive and finite. Ranking is descending by score, then relevance, then candidate ID for deterministic tie-breaking.

## Exercise 3 — Budget-Aware Context Selection

The selector processes candidates in ranked order. A candidate is selected when its token cost fits the remaining budget. If it does not fit, it is excluded and the algorithm continues to inspect subsequent candidates. The result reports selected and excluded candidates, scores, total budget, used tokens, and remaining tokens.

With the supplied sample data and a 40-token budget, VEC001, STM001, and LTM001 are selected for a total of 38 tokens. STM002 and LTM002 are excluded.

## Exercise 4 — Retrieval and Summarization

Vector retrieval is represented by a deterministic, pre-scored vector store and a minimum relevance threshold. Historical conversation entries can be converted into a compact extractive summary candidate. The collection function combines existing candidates, qualifying vector candidates, and a summary candidate while rejecting duplicate IDs.

Selection explanations report whether each candidate was selected or excluded and explain the token-budget outcome.

## Exercise 5 — Policy Inspection and Improvements

The inspection module reports total, selected, and excluded candidate counts; token usage; remaining budget; budget utilization; selection rate; average selected score; and selected-source distribution.

Policy comparison runs the same candidate set and budget under multiple scoring configurations. In the recorded experiment:

| Policy | Selected candidates | Tokens used |
|---|---|---:|
| Default | VEC001, STM001, LTM001 | 38/40 |
| Recency-focused | STM001, STM002, VEC001 | 40/40 |

This demonstrates that policy weights influence which memories are retained while the token budget remains enforced.

## Running the Project

Open CMD and navigate to the project directory:

```cmd
E:
cd E:\Tayana_Projects\Memory_Engineering\Context_Selection_Assessment
```

Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```cmd
python -m pip install -r requirements.txt
```

Run an individual exercise:

```cmd
python -m pytest tests\test_task1.py -v
python -m pytest tests\test_task2.py -v
python -m pytest tests\test_task3.py -v
python -m pytest tests\test_task4.py -v
python -m pytest tests\test_task5.py -v
```

Run the complete suite:

```cmd
python -m pytest -v
```

## Final Test Results

| Exercise | Passed |
|---|---:|
| Exercise 1 — Candidate Model | 6 |
| Exercise 2 — Scoring and Ranking | 8 |
| Exercise 3 — Budget Selection | 8 |
| Exercise 4 — Retrieval and Summarization | 10 |
| Exercise 5 — Policy Inspection | 10 |
| **Total** | **42** |

Final verification reported:

```text
42 passed in 0.07s
```

## Limitations and Future Improvements

- Vector retrieval uses pre-scored candidates rather than real embeddings and nearest-neighbor search.
- Historical summarization is extractive and deterministic; it does not use an LLM to generate semantic summaries.
- Token counts are supplied estimates rather than tokenizer-derived counts.
- The greedy budget selector does not guarantee the globally optimal combination of candidates. A future version could compare greedy selection with a knapsack-based optimizer.
- Production systems should also consider privacy, memory expiration, duplicate or contradictory facts, source trust, and user-controlled memory deletion.

## Reflection

This assessment helped me understand that context selection is a key part of building reliable LLM-based agents. An agent may have access to a large amount of conversational history and stored information, but including everything in every prompt is inefficient. It increases token usage, can raise costs, and may distract the model with information that is not useful for the current task. A context-selection layer provides a systematic way to decide what should be included.

I began by designing a common candidate model for short-term, long-term, and vector-retrieved memories. I then implemented a configurable scoring mechanism using relevance, recency, priority, and source weights. This showed how different policies can influence ranking. The budget-aware selector added another important constraint: even a highly ranked memory must be excluded when it cannot fit in the remaining token budget. The implementation also continues evaluating later candidates rather than stopping at the first item that does not fit.

The retrieval and summarization exercise demonstrated how information from different memory sources can be combined. Historical entries were converted into a compact summary candidate, while vector retrieval was simulated with pre-scored examples. Finally, the inspection and policy-comparison functions made the system easier to evaluate by reporting token utilization, selection rate, source distribution, and selected candidates.

The most useful learning outcome was seeing how a change in scoring weights changes the final context. The default policy used 38 of 40 tokens, while the recency-focused policy used all 40 and selected a different combination of memories. The complete assessment passed 42 tests. This project strengthened my understanding of memory management, deterministic ranking, budget constraints, validation, and testing. As a next step, I would integrate a real embedding model, tokenizer-based token counting, and semantic summarization, then evaluate the quality of selected context on realistic agent tasks.
