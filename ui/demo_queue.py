"""Sample queue items for the dashboard."""

from __future__ import annotations

from typing import Any


def demo_items() -> list[dict[str, Any]]:
    return [
        {
            "id": "demo_urgent_001",
            "created_at": "2026-04-29T00:00:10Z",
            "email_text": (
                "Hi Mumzworld team,\n\n"
                "My baby formula order MW-900771 was supposed to arrive 2 days ago and the tracking hasn’t moved. "
                "We are completely out tonight and this is urgent for my baby’s health.\n\n"
                "Please help immediately."
            ),
            "triage_json": {
                "intent": "delivery_complaint",
                "urgency": 5,
                "urgency_reasoning": "Baby formula is delayed; customer is out tonight. Health-critical (formula/health/baby).",
                "sentiment": "frustrated",
                "language_detected": "en",
                "confidence": 0.95,
                "clarification_needed": False,
                "clarification_reason": None,
                "suggested_reply": (
                    "Hi,\n\n"
                    "Thank you for reaching out — we understand how urgent a baby formula delay is.\n\n"
                    "Please confirm your delivery city and a reachable phone number so we can coordinate with the courier immediately. "
                    "We are escalating order MW-900771 as a health-critical case and will update you as a priority.\n\n"
                    "Warm regards,\nMumzworld Customer Care"
                ),
                "policy_citations": ["7.1", "5.1", "5.2"],
                "raw_input_language_check": True,
            },
            "debug_trace": {
                "mode": "pipeline_trace",
                "retrieved_policy": ["5.1", "5.2", "7.1"],
                "prompt_summary": "Policy-grounded triage + reply (English).",
                "raw_model_output": "(raw JSON output)",
                "post_processing": ["language_check"],
            },
        },
        {
            "id": "demo_normal_001",
            "created_at": "2026-04-29T00:00:40Z",
            "email_text": (
                "Hi,\n\n"
                "I returned my item from order MW-120009 last week. When should the refund appear back on my card?\n\n"
                "Thanks,\nAisha"
            ),
            "triage_json": {
                "intent": "refund_request",
                "urgency": 2,
                "urgency_reasoning": "Refund status inquiry; no safety risk.",
                "sentiment": "neutral",
                "language_detected": "en",
                "confidence": 0.9,
                "clarification_needed": False,
                "clarification_reason": None,
                "suggested_reply": (
                    "Hi Aisha,\n\n"
                    "Thanks for reaching out. Refunds are typically processed within 5–7 business days back to the original payment method. "
                    "If it has been longer than that, please share the return confirmation date and we’ll investigate.\n\n"
                    "Warm regards,\nMumzworld Customer Care"
                ),
                "policy_citations": ["3.1"],
                "raw_input_language_check": True,
            },
            "debug_trace": {
                "mode": "pipeline_trace",
                "retrieved_policy": ["3.1"],
                "prompt_summary": "Refund timeline grounded in policy.",
                "raw_model_output": "(raw JSON output)",
                "post_processing": ["language_check"],
            },
        },
        {
            "id": "demo_ambiguous_001",
            "created_at": "2026-04-29T00:01:10Z",
            "email_text": "Hello,\n\nWhere is my order?",
            "triage_json": {
                "intent": "delivery_complaint",
                "urgency": 2,
                "urgency_reasoning": "Delivery status question; missing order details.",
                "sentiment": "neutral",
                "language_detected": "en",
                "confidence": 0.4,
                "clarification_needed": True,
                "clarification_reason": "Please share your order number (MW-xxxxxx), delivery city, and phone number so we can check tracking.",
                "suggested_reply": None,
                "policy_citations": ["5.1", "5.2"],
                "raw_input_language_check": True,
            },
            "debug_trace": {
                "mode": "pipeline_trace",
                "retrieved_policy": ["5.1", "5.2"],
                "prompt_summary": "Clarification mode; no reply drafted.",
                "raw_model_output": "(raw JSON output)",
                "post_processing": ["language_check"],
            },
        },
        {
            "id": "demo_arabic_001",
            "created_at": "2026-04-29T00:01:40Z",
            "email_text": (
                "هلا Mumzworld،\n\n"
                "وصلتني حفاضات Pampers مقاس 4 وأنا طالبة مقاس 3. الكرتون عليه اسمي بس المنتج غلط. "
                "رقم الطلب MW-221905. أبي استبدال بأسرع وقت.\n\n"
                "تحياتي،\nأم راشد"
            ),
            "triage_json": {
                "intent": "wrong_item",
                "urgency": 3,
                "urgency_reasoning": "Wrong item received; customer needs correction soon.",
                "sentiment": "frustrated",
                "language_detected": "ar",
                "confidence": 0.9,
                "clarification_needed": False,
                "clarification_reason": None,
                "suggested_reply": (
                    "هلا أم راشد،\n\n"
                    "نعتذر لك عن الخطأ. بما إن المنتج اللي وصلك مختلف عن اللي طلبتيه، نقدر نساعدك بترتيب استبدال. "
                    "فضلاً أرسلي لنا صورة للمنتج والباركود/الملصق على الكرتون للتأكيد، وبننسق معك أقرب موعد للاستلام.\n\n"
                    "فريق خدمة عملاء Mumzworld"
                ),
                "policy_citations": ["4.1", "4.2"],
                "raw_input_language_check": True,
            },
            "debug_trace": {
                "mode": "pipeline_trace",
                "retrieved_policy": ["4.1", "4.2"],
                "prompt_summary": "Arabic wrong-item handling + policy citations.",
                "raw_model_output": "(raw JSON output)",
                "post_processing": ["language_check"],
            },
        },
    ]

