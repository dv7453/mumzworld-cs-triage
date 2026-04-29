"""Markdown report writer for eval results.

This is extracted from `evals/eval_runner.py` to keep files short and focused.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_report(*, report_path: Path, rows: list[Any], summary: dict[str, Any]) -> Path:
    """Generate `EVALS.md` markdown report.

    Notes:
    - `rows` is a list of EvalRow objects (duck-typed).
    - We keep formatting logic here so `eval_runner.py` stays under the line limit.
    """

    # Markdown table header.
    md: list[str] = []
    md.append("# EVALS\n")
    md.append("## Summary\n")
    md.append(
        f"- Generated at: {summary.get('generated_at')}\n"
        f"- Eval mode: {summary.get('eval_mode', 'unknown')}\n"
        f"- Passed: {summary.get('passed')}\n"
        f"- Failed: {summary.get('failed')}\n"
        f"- Average score: {summary.get('avg_score'):.2f}\n"
    )

    md.append("### Results Table\n")
    md.append(
        "| id | expected_intent | actual_intent | urgency | sentiment | clarification_needed | language_check | score | pass | error |\n"
    )
    md.append("|---|---|---|---:|---|---|---|---:|---|---|\n")
    for r in rows:
        md.append(
            "| "
            + " | ".join(
                [
                    r.case_id,
                    r.expected_intent,
                    (r.actual_intent or ""),
                    (str(r.urgency) if r.urgency is not None else ""),
                    (r.sentiment or ""),
                    (
                        str(r.clarification_needed)
                        if r.clarification_needed is not None
                        else ""
                    ),
                    (str(r.language_check) if r.language_check is not None else ""),
                    str(r.total_score),
                    ("PASS" if r.passed else "FAIL"),
                    (r.error or ""),
                ]
            )
            + " |\n"
        )

    md.append("\n## Notable Failures\n")
    below = [r for r in rows if r.total_score < 75 or not r.passed]
    if not below:
        md.append("None.\n")
    else:
        md.append("Cases below 75 (or failing due to automatic failure / error):\n\n")
        for r in below:
            md.append(
                f"- **{r.case_id}**: score={r.total_score}, pass={r.passed}, error={r.error or 'none'}\n"
            )
            md.append(
                f"  - expected_intent={r.expected_intent}\n"
                f"  - actual_intent={r.actual_intent}\n"
                f"  - urgency={r.urgency}\n"
                f"  - sentiment={r.sentiment}\n"
                f"  - clarification_needed={r.clarification_needed}\n"
                f"  - language_check={r.language_check}\n"
            )
            if getattr(r, "automatic_failures", None):
                md.append(f"  - automatic_failures={r.automatic_failures}\n")

    md.append("\n## Automatic Failures\n")
    af = summary.get("automatic_failures") or {}
    if not af:
        md.append("None.\n")
    else:
        for cid, reasons in af.items():
            md.append(f"- **{cid}**: {', '.join(reasons)}\n")

    md.append("\n## Partial Misses (Passed but imperfect)\n")
    md.append(
        "Some cases can still **pass** at the ≥75 threshold even when one field is off "
        "(e.g., intent mismatch but urgency/clarification are correct). These are useful for spotting drift.\n\n"
    )
    partial = [r for r in rows if r.passed and r.total_score < 100]
    if not partial:
        md.append("None.\n")
    else:
        md.append("Examples (up to 10):\n\n")
        for r in partial[:10]:
            md.append(
                f"- **{r.case_id}**: score={r.total_score} "
                f"(expected_intent={r.expected_intent}, actual_intent={r.actual_intent}, "
                f"sentiment={r.sentiment}, clar={r.clarification_needed})\n"
            )

    md.append("\n## Named Failure Modes (observed during development)\n")
    md.append(
        "- **Non-JSON output**: model wraps JSON in markdown code fences or adds prose.\n"
        "- **Schema violations**: missing fields / empty strings / reply provided when clarification is required.\n"
        "- **Language mismatch**: model claims Arabic but outputs English (or vice versa).\n"
        "- **Intent confusion**: wrong-item vs exchange wording; vague complaints routed as general inquiry.\n"
        "- **Provider volatility**: rate limits / model not found / transient 5xx errors.\n"
    )

    md.append("\n## Historical Reliability Notes\n")
    md.append(
        "Earlier iterations (before adding post-processing + routing overrides) had real failures, e.g.:\n\n"
        "- Runs where the model returned JSON inside ```json fences, causing JSON parse failures.\n"
        "- Runs where `raw_input_language_check` was false, triggering schema validation errors.\n"
        "- External API/model availability issues (404 model not found; provider demand spikes).\n\n"
        "These were addressed by stripping code fences, enforcing language checks deterministically, "
        "and using a model fallback list.\n"
    )

    md.append("\n## Eval Methodology\n")
    md.append(
        "Each case is scored out of **100** using the rubric:\n\n"
        "- intent_match: **25** (exact match)\n"
        "- urgency_in_range: **20** (actual urgency >= expected_urgency_min)\n"
        "- sentiment_match: **15** (exact match)\n"
        "- clarification_correct: **20** (matches expected; if true, clarification_reason non-empty)\n"
        "- reply_language_correct: **10** (raw_input_language_check is True)\n"
        "- schema_valid: **10** (10 if schema validated; 0 if a TriageValidationError was caught)\n\n"
        "Automatic failures override scoring (case fails regardless of score):\n\n"
        "- suggested_reply is non-null when clarification_needed is True\n"
        "- urgency is 5 but urgency_reasoning has no required health keywords\n"
        "- policy_citations is an empty list when a policy-relevant intent is classified\n"
    )

    report_path.write_text("".join(md), encoding="utf-8")
    return report_path

