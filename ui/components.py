"""UI rendering components for the Streamlit app."""

from __future__ import annotations

import streamlit as st

_SENTIMENT_EMOJI = {
    "frustrated": "😤",
    "neutral": "😐",
    "positive": "😊",
}


def _intent_badge_color(intent: str, urgency: int) -> str:
    # Red: escalation or urgency 5 (ops attention).
    if intent == "escalate" or urgency == 5:
        return "mw-badge mw-badge-red"
    # Yellow: complaint-like.
    if intent in {"delivery_complaint", "wrong_item", "warranty_dispute"}:
        return "mw-badge mw-badge-yellow"
    # Green: informational/standard requests.
    return "mw-badge mw-badge-green"


def _stars(score: int) -> str:
    score = max(1, min(5, int(score)))
    return "★" * score + "☆" * (5 - score)


def render_result(output: object) -> None:
    """Render a validated `TriageOutput`-like object in the Streamlit UI."""

    st.subheader("Triage Result")

    badge_class = _intent_badge_color(getattr(output, "intent"), getattr(output, "urgency"))
    st.markdown(
        f'<span class="{badge_class}">Intent: {getattr(output, "intent")}</span>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="mw-card">', unsafe_allow_html=True)
    st.markdown(
        f"**Urgency**: {_stars(getattr(output, 'urgency'))}  \n{getattr(output, 'urgency_reasoning')}"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.2, 1.0, 1.2])
    with c1:
        sentiment = getattr(output, "sentiment")
        emoji = _SENTIMENT_EMOJI.get(sentiment, "")
        st.metric("Sentiment", f"{emoji} {sentiment}")
    with c2:
        st.metric("Language detected", getattr(output, "language_detected"))
    with c3:
        st.metric("Confidence", f"{float(getattr(output, 'confidence')):.2f}")

    st.progress(min(max(float(getattr(output, "confidence")), 0.0), 1.0))

    if getattr(output, "clarification_needed"):
        st.warning(getattr(output, "clarification_reason") or "Clarification needed.")
    else:
        reply = getattr(output, "suggested_reply")
        if reply:
            st.markdown("**Suggested reply**")
            st.markdown(f'<div class="mw-reply">{reply}</div>', unsafe_allow_html=True)
            # `st.code` includes a built-in copy button in Streamlit.
            st.code(reply)
        else:
            st.info("No reply was generated.")

    citations = getattr(output, "policy_citations")
    if citations:
        st.caption("Policy citations: " + ", ".join(citations))
    elif citations == []:
        st.caption("Policy citations: (empty list)")
    else:
        st.caption("Policy citations: none")

