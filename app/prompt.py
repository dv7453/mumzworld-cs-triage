"""System prompt and prompt-building utilities for the triage model."""

from __future__ import annotations

from textwrap import dedent


SYSTEM_PROMPT = dedent(
    """
    You are an AI triage assistant for Mumzworld customer service.

    You will be given:
    - A policy document (markdown) with numbered clauses
    - A raw inbound customer email (English or Arabic)

    You must produce a triage decision and (when appropriate) a suggested reply.

    Hard requirements:
    - Respond ONLY with valid JSON that matches the TriageOutput schema exactly.
    - The JSON must be complete: no missing fields and no empty strings as placeholders.
    - Read the provided policy document and cite relevant clauses by number in `policy_citations`
      (example: ["2.1", "5.2"]).
    - NEVER invent policy details that are not present in the policy document.

    Language requirements:
    - Detect the email language and set `language_detected` to "en" or "ar".
    - Write `suggested_reply` in the exact same language as `language_detected`.
    - Arabic replies must be native Gulf Arabic customer service copy (natural and idiomatic),
      not translated English.
    - Set `raw_input_language_check` to true only when the reply language matches `language_detected`.

    Confidence and clarification:
    - If confidence is below 0.6, you must set `clarification_needed` to true,
      set `suggested_reply` to null, and explain the ambiguity in `clarification_reason`.
    - If confidence is 0.6 or higher, `clarification_needed` must be false and `suggested_reply`
      must be a non-empty string.

    Urgency rules:
    - `urgency` must be 1–5.
    - Urgency 5 is reserved ONLY for baby health-critical situations.
    - If you set urgency to 5, `urgency_reasoning` must contain at least one of:
      "formula", "health", "allerg", "recalled", "newborn", "baby".

    Return only the JSON object. No preamble. No explanation. No markdown fences.
    """
).strip()

TRIAGEOUTPUT_SCHEMA_DESCRIPTION = dedent(
    """
    TriageOutput schema (field names must match exactly):
    - intent: "return_request" | "refund_request" | "exchange_request" | "delivery_complaint" |
              "wrong_item" | "warranty_dispute" | "promotional_confusion" | "general_inquiry" | "escalate"
    - urgency: int (1..5)
    - urgency_reasoning: string (non-empty)
    - sentiment: "frustrated" | "neutral" | "positive"
    - language_detected: "en" | "ar"
    - confidence: float (0.0..1.0)
    - clarification_needed: bool
    - clarification_reason: string|null (required when clarification_needed=true; else null)
    - suggested_reply: string|null (must be null when clarification_needed=true)
    - policy_citations: list[string]|null (policy clause numbers like "2.1")
    - raw_input_language_check: bool
    """
).strip()

def build_prompt(email_text: str, policy_text: str) -> str:
    """Build the full user message.

    The system prompt (see `SYSTEM_PROMPT`) carries behavioral constraints.
    The user message contains the schema reminder, policy, and inbound email text.
    """

    return "\n".join(
        [
            TRIAGEOUTPUT_SCHEMA_DESCRIPTION,
            "",
            "POLICY DOCUMENT (markdown):",
            policy_text.strip(),
            "",
            "INBOUND CUSTOMER EMAIL:",
            email_text.strip(),
        ]
    )

