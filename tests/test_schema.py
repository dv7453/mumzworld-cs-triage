from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schema import TriageOutput


def _valid_payload() -> dict:
    return {
        "intent": "delivery_complaint",
        "urgency": 3,
        "urgency_reasoning": "Delivery is delayed and customer needs an update.",
        "sentiment": "neutral",
        "language_detected": "en",
        "confidence": 0.85,
        "clarification_needed": False,
        "clarification_reason": None,
        "suggested_reply": "Thanks for reaching out. Please share your order number so we can check the latest courier status.",
        "policy_citations": ["5.3", "5.4"],
        "raw_input_language_check": True,
    }


def test_valid_triageoutput_passes_validation() -> None:
    out = TriageOutput.model_validate(_valid_payload())
    assert out.intent == "delivery_complaint"


def test_clarification_needed_true_reply_must_be_null() -> None:
    payload = _valid_payload()
    payload["clarification_needed"] = True
    payload["clarification_reason"] = "Missing order number and delivery address."
    payload["suggested_reply"] = "Here is a reply even though clarification is needed."
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_clarification_needed_true_reason_must_not_be_null() -> None:
    payload = _valid_payload()
    payload["clarification_needed"] = True
    payload["suggested_reply"] = None
    payload["clarification_reason"] = None
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_confidence_ge_06_reply_must_not_be_null() -> None:
    payload = _valid_payload()
    payload["confidence"] = 0.6
    payload["suggested_reply"] = None
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_urgency_5_requires_health_keyword_in_reasoning() -> None:
    payload = _valid_payload()
    payload["urgency"] = 5
    payload["urgency_reasoning"] = "Customer is very upset and wants this fixed now."
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_urgency_5_passes_with_health_keyword_formula() -> None:
    payload = _valid_payload()
    payload["urgency"] = 5
    payload["urgency_reasoning"] = "Baby formula delivery is delayed and this impacts baby health."
    out = TriageOutput.model_validate(payload)
    assert out.urgency == 5


@pytest.mark.parametrize("urgency", [0, 6])
def test_urgency_out_of_range_raises(urgency: int) -> None:
    payload = _valid_payload()
    payload["urgency"] = urgency
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_confidence_out_of_range_raises(confidence: float) -> None:
    payload = _valid_payload()
    payload["confidence"] = confidence
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_invalid_intent_literal_raises() -> None:
    payload = _valid_payload()
    payload["intent"] = "cancel_order"
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_invalid_sentiment_literal_raises() -> None:
    payload = _valid_payload()
    payload["sentiment"] = "angry"
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_urgency_reasoning_must_not_be_empty() -> None:
    payload = _valid_payload()
    payload["urgency_reasoning"] = ""
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)


def test_raw_input_language_check_must_be_bool() -> None:
    payload = _valid_payload()
    # Pydantic accepts some truthy strings like "yes"; use a value that should not coerce.
    payload["raw_input_language_check"] = "maybe"
    with pytest.raises(ValidationError):
        TriageOutput.model_validate(payload)

