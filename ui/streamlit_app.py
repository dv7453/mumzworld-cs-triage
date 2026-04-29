"""Streamlit UI for the Mumzworld CS triage prototype."""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import os

import streamlit as st
from dotenv import load_dotenv

from app.triage import TriageValidationError, triage
from ui.components import render_result
from ui.demo_queue import demo_items
from ui.queue_db import QueueItem, get_item, list_items, upsert_item, utc_now_iso


def _inject_styles() -> None:
    # Minimal, professional styling using Streamlit markdown + CSS.
    st.markdown(
        """
<style>
  .mw-subtitle { color: rgba(49, 51, 63, 0.75); margin-top: -6px; }
  .mw-badge {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid rgba(49, 51, 63, 0.15);
    background: rgba(49, 51, 63, 0.04);
  }
  .mw-badge-red    { background: rgba(220, 38, 38, 0.08); border-color: rgba(220, 38, 38, 0.25); color: rgb(153, 27, 27); }
  .mw-badge-yellow { background: rgba(245, 158, 11, 0.10); border-color: rgba(245, 158, 11, 0.30); color: rgb(146, 64, 14); }
  .mw-badge-green  { background: rgba(16, 185, 129, 0.10); border-color: rgba(16, 185, 129, 0.30); color: rgb(6, 95, 70); }
  .mw-card {
    border: 1px solid rgba(49, 51, 63, 0.15);
    border-radius: 12px;
    padding: 14px 14px;
    background: rgba(255, 255, 255, 0.70);
  }
  .mw-reply {
    border-left: 4px solid rgba(16, 185, 129, 0.55);
    background: rgba(16, 185, 129, 0.06);
    padding: 12px 12px;
    border-radius: 10px;
    white-space: pre-wrap;
    line-height: 1.55;
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def _sample_emails() -> list[tuple[str, str]]:
    return [
        (
            "EN — complaint",
            "Hi Mumzworld,\n\nMy order MW-900771 is delayed and tracking hasn't updated since dispatch. "
            "It contains Pampers size 3 and wipes. Please update me.\n\nThanks,\nSarah",
        ),
        (
            "AR — formula urgency",
            "هلا Mumzworld،\n\nطلب حليب الطفل (formula) متأخر يومين وما عندي غير علبة تكفي الليلة. "
            "رقم الطلب MW-995001. الموضوع مهم لصحة baby.\n\nتكفون ساعدوني.",
        ),
        (
            "Ambiguous",
            "Hello,\n\nThis is unacceptable. Please fix it ASAP.",
        ),
    ]


def main() -> None:
    load_dotenv()

    api_key_present = bool(os.getenv("ANTHROPIC_API_KEY"))
    st.set_page_config(page_title="Mumzworld CS Triage — AI Email Assistant", layout="centered")
    _inject_styles()

    st.title("Mumzworld CS Triage — AI Email Assistant")
    st.markdown(
        '<div class="mw-subtitle">'
        "Paste a customer email below to triage it instantly<br/>"
        "الصق بريد العميل أدناه لتصنيفه فوراً"
        "</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.header("Samples")
    st.sidebar.caption("Click to auto-fill.")
    for label, sample in _sample_emails():
        if st.sidebar.button(label, use_container_width=True):
            st.session_state["email_text"] = sample

    if not api_key_present:
        st.sidebar.warning("Missing `ANTHROPIC_API_KEY`. Copy `.env.example` → `.env` and set your key.")

    st.sidebar.divider()
    translate_ar = st.sidebar.toggle(
        "Translate Arabic → English",
        value=True,
        help="Uses a separate non-LLM translator for readability. If it fails, the app will still work.",
    )

    st.sidebar.divider()
    page = st.sidebar.radio("Mode", ["Live Triage", "Queue Dashboard"], index=0)

    st.divider()

    if page == "Queue Dashboard":
        st.subheader("Queue Dashboard")
        st.caption("Sorted by urgency (highest priority on top).")

        items = list_items()
        if not items:
            for d in demo_items():
                tj = d["triage_json"]
                upsert_item(
                    item=QueueItem(
                        id=d["id"],
                        created_at=d["created_at"],
                        urgency=int(tj["urgency"]),
                        intent=str(tj["intent"]),
                        language=str(tj["language_detected"]),
                        sentiment=str(tj["sentiment"]),
                        email_text=str(d["email_text"]),
                        triage_json=tj,
                        debug_trace=d["debug_trace"],
                    )
                )
            items = list_items()

        with st.expander("Add to queue", expanded=False):
            new_email = st.text_area("Email text to add", height=140, placeholder="Paste any email here…")
            preset = st.selectbox(
                "Pick a demo output template",
                [
                    "Use urgent formula template",
                    "Use refund template",
                    "Use clarification template",
                    "Use Arabic wrong-item template",
                ],
            )
            if st.button("Add to queue", type="primary"):
                if not new_email.strip():
                    st.warning("Paste an email first.")
                else:
                    templates = demo_items()
                    chosen = templates[0]
                    if preset.startswith("Use refund"):
                        chosen = templates[1]
                    elif preset.startswith("Use clarification"):
                        chosen = templates[2]
                    elif preset.startswith("Use Arabic"):
                        chosen = templates[3]

                    triage_json = dict(chosen["triage_json"])
                    dbg = dict(chosen["debug_trace"])
                    dbg["note"] = "Added via dashboard form."
                    item_id = f"demo_added_{utc_now_iso().replace(':','').replace('-','')}"
                    upsert_item(
                        item=QueueItem(
                            id=item_id,
                            created_at=utc_now_iso(),
                            urgency=int(triage_json["urgency"]),
                            intent=str(triage_json["intent"]),
                            language=str(triage_json["language_detected"]),
                            sentiment=str(triage_json["sentiment"]),
                            email_text=new_email.strip(),
                            triage_json=triage_json,
                            debug_trace=dbg,
                        )
                    )
                    st.success(f"Added to queue: {item_id}")
                    st.rerun()

        items = list_items()
        labels = [f"{i.urgency}★  {i.id}  ({i.intent}, {i.language})" for i in items]
        selected_label = st.selectbox("Queue (click an item)", labels)
        selected_id = selected_label.split("  ")[1]
        item = get_item(item_id=selected_id)
        if item is None:
            st.error("Selected item not found.")
            return

        st.markdown("**Inbound email**")
        st.code(item.email_text)

        st.markdown("**Validated JSON output**")
        st.json(item.triage_json)

        st.markdown("**Pipeline trace**")
        st.json(item.debug_trace)

        if translate_ar and item.language == "ar":
            try:
                from deep_translator import GoogleTranslator

                tr = GoogleTranslator(source="ar", target="en")
                st.markdown("**Arabic → English (display-only)**")
                if item.triage_json.get("clarification_needed"):
                    txt = item.triage_json.get("clarification_reason") or ""
                    if str(txt).strip():
                        st.info(tr.translate(str(txt)))
                else:
                    txt = item.triage_json.get("suggested_reply") or ""
                    if str(txt).strip():
                        st.markdown(tr.translate(str(txt)))
            except Exception as e:
                st.caption(f"Translation unavailable: {e}")

        return

    placeholder = (
        "Example (EN):\n"
        "Hi, my order MW-123456 is delayed and I need an update.\n\n"
        "مثال (AR):\n"
        "هلا، طلبي MW-123456 متأخر.. ممكن تحديث؟"
    )
    email_text = st.text_area(
        "Customer email / بريد العميل",
        key="email_text",
        height=280,
        placeholder=placeholder,
    )

    submit = st.button(
        "Triage Email",
        type="primary",
        use_container_width=True,
        disabled=not api_key_present,
    )

    if submit:
        if not (email_text or "").strip():
            st.warning("Please paste an email first.")
            return

        try:
            with st.spinner("Triaging…"):
                output = triage(email_text)

            st.markdown("**Raw JSON output (validated)**")
            st.json(output.model_dump(mode="json"))

            render_result(output)

            if translate_ar and getattr(output, "language_detected", None) == "ar":
                try:
                    from deep_translator import GoogleTranslator

                    tr = GoogleTranslator(source="ar", target="en")
                    st.markdown("**Arabic → English (non-LLM translation)**")
                    if getattr(output, "clarification_needed", False):
                        txt = getattr(output, "clarification_reason") or ""
                        if txt.strip():
                            st.info(tr.translate(txt))
                    else:
                        txt = getattr(output, "suggested_reply") or ""
                        if txt.strip():
                            st.markdown(tr.translate(txt))
                except Exception as e:
                    st.caption(f"Translation unavailable: {e}")

        except TriageValidationError as e:
            st.error("TriageValidationError: model output failed schema validation.")
            if e.validation_error is not None:
                st.code(str(e.validation_error))
            st.markdown("**Raw model output**")
            st.code(e.raw_response_text)
        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()

