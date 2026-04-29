"""Scoring rubric for triage outputs.

Scores each test case out of 100 points and also flags automatic failures.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dataclasses import dataclass
from typing import Any, Optional

from app.schema import TriageOutput


@dataclass(frozen=True)
class ScoreBreakdown:
    intent_match: int
    urgency_in_range: int
    sentiment_match: int
    clarification_correct: int
    reply_language_correct: int
    schema_valid: int

    @property
    def total(self) -> int:
        return (
            self.intent_match
            + self.urgency_in_range
            + self.sentiment_match
            + self.clarification_correct
            + self.reply_language_correct
            + self.schema_valid
        )


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    breakdown: ScoreBreakdown
    total_score: int
    passed: bool
    automatic_failures: list[str]
    notes: Optional[str] = None


_HEALTH_KEYWORDS = ("formula", "health", "allerg", "recalled", "newborn", "baby")
_POLICY_RELEVANT_INTENTS = {
    "return_request",
    "refund_request",
    "exchange_request",
    "delivery_complaint",
    "wrong_item",
    "warranty_dispute",
    "promotional_confusion",
}


def _has_health_keywords(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in _HEALTH_KEYWORDS)


def score_result(expected: dict[str, Any], actual: TriageOutput) -> CaseScore:
    """Score one validated model output against expectations.

    `actual` is already schema-validated upstream. This function is deterministic.
    """

    automatic_failures: list[str] = []

    # Automatic failures (hard constraints regardless of score).
    if actual.clarification_needed and actual.suggested_reply is not None:
        automatic_failures.append(
            "suggested_reply is non-null when clarification_needed is True"
        )

    if actual.urgency == 5 and not _has_health_keywords(actual.urgency_reasoning):
        automatic_failures.append(
            "urgency=5 but urgency_reasoning lacks required health keywords"
        )

    if (
        actual.intent in _POLICY_RELEVANT_INTENTS
        and isinstance(actual.policy_citations, list)
        and len(actual.policy_citations) == 0
    ):
        automatic_failures.append(
            "policy_citations is an empty list for a policy-relevant intent"
        )

    # Core rubric scoring (out of 100).
    intent_match = 25 if actual.intent == expected.get("expected_intent") else 0

    expected_urgency_min = int(expected.get("expected_urgency_min", 1))
    urgency_in_range = 20 if actual.urgency >= expected_urgency_min else 0

    sentiment_match = (
        15 if actual.sentiment == expected.get("expected_sentiment") else 0
    )

    expected_clar = bool(expected.get("expected_clarification_needed"))
    clar_ok = actual.clarification_needed == expected_clar
    clar_reason_ok = True
    if actual.clarification_needed:
        clar_reason_ok = bool((actual.clarification_reason or "").strip())
    clarification_correct = 20 if (clar_ok and clar_reason_ok) else 0

    reply_language_correct = 10 if actual.raw_input_language_check is True else 0

    # If we got here, schema validation already succeeded upstream.
    schema_valid = 10

    breakdown = ScoreBreakdown(
        intent_match=intent_match,
        urgency_in_range=urgency_in_range,
        sentiment_match=sentiment_match,
        clarification_correct=clarification_correct,
        reply_language_correct=reply_language_correct,
        schema_valid=schema_valid,
    )
    total = breakdown.total

    # Pass/fail threshold.
    passed = total >= 75 and len(automatic_failures) == 0

    return CaseScore(
        case_id=str(expected.get("id", "")),
        breakdown=breakdown,
        total_score=total,
        passed=passed,
        automatic_failures=automatic_failures,
        notes=str(expected.get("notes", "")) if expected.get("notes") is not None else None,
    )

