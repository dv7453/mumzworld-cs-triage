"""Pydantic v2 schema for the triage system.

Phase 2: implement the validated output schema + cross-field invariants.
"""

from __future__ import annotations

from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, model_validator


IntentLiteral = Literal[
    "return_request",
    "refund_request",
    "exchange_request",
    "delivery_complaint",
    "wrong_item",
    "warranty_dispute",
    "promotional_confusion",
    "general_inquiry",
    "escalate",
]


class TriageOutput(BaseModel):
    """Validated JSON output for one inbound email."""

    intent: IntentLiteral
    urgency: Annotated[int, Field(ge=1, le=5)]
    urgency_reasoning: Annotated[str, Field(min_length=1)]
    sentiment: Literal["frustrated", "neutral", "positive"]
    language_detected: Literal["en", "ar"]
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    clarification_needed: bool
    clarification_reason: Optional[Annotated[str, Field(min_length=1)]] = Field(
        default=None,
        description="Required when clarification_needed is true; otherwise must be null.",
    )
    suggested_reply: Optional[Annotated[str, Field(min_length=1)]] = Field(
        default=None,
        description="Must be null when clarification_needed is true.",
    )
    policy_citations: Optional[list[str]] = Field(
        default=None,
        description="List of cited policy clauses (e.g., '2.1', '4.3') or null.",
    )
    raw_input_language_check: bool = Field(
        description="True if suggested_reply language matches language_detected.",
    )

    @model_validator(mode="after")
    def validate_clarification_consistency(self) -> "TriageOutput":
        if self.clarification_needed is True and self.suggested_reply is not None:
            raise ValueError("clarification_needed is true, but suggested_reply is not null")
        if self.clarification_needed is True and self.clarification_reason is None:
            raise ValueError("clarification_needed is true, but clarification_reason is null")
        return self

    @model_validator(mode="after")
    def validate_confidence_reply_consistency(self) -> "TriageOutput":
        if (
            self.confidence >= 0.6
            and self.suggested_reply is None
            and self.clarification_needed is False
        ):
            raise ValueError("confidence >= 0.6, but suggested_reply is null")
        return self

    @model_validator(mode="after")
    def validate_urgency_5_keywords(self) -> "TriageOutput":
        if self.urgency == 5:
            reasoning_lower = self.urgency_reasoning.lower()
            required_markers = ("formula", "health", "allerg", "recalled", "newborn", "baby")
            if not any(m in reasoning_lower for m in required_markers):
                raise ValueError(
                    "urgency is 5, but urgency_reasoning lacks a baby health-critical marker"
                )
        return self

    @model_validator(mode="after")
    def validate_language_reply_match(self) -> "TriageOutput":
        if self.raw_input_language_check is False:
            raise ValueError("Reply language does not match detected input language")
        return self

