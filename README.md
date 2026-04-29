# Mumzworld AI Email Triage (Prototype)

## Overview

This prototype helps Mumzworld customer support teams triage inbound emails in English and Arabic by classifying intent, urgency, and sentiment, and drafting policy-grounded replies when appropriate. It’s built for internal ops: faster routing, more consistent responses, and safer handling of health-critical and high-risk edge cases across a high-volume inbox.

## Setup

```bash
git clone https://github.com/dv7453/mumzworld-cs-triage.git
cd mumzworld-cs-triage
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables:

```bash
cp .env.example .env
```

Open `.env` and set:

- `ANTHROPIC_API_KEY=<your_key>`

Run the Streamlit UI:

```bash
python -m streamlit run ui/streamlit_app.py
```

Run evals:

```bash
python evals/eval_runner.py
```

Run unit tests:

```bash
pytest -q
```

## Evals

See `EVALS.md` for the latest evaluation report. The rubric scores each case out of 100 across intent match, urgency minimum threshold, sentiment, clarification behavior, reply language check, and schema validity; cases pass at **≥ 75** and must also avoid any automatic-failure rules (e.g., replying when clarification is required). The goal is to prove the system is both useful and safe under realistic email variability.

## Tradeoffs

- **Why this problem**: Email triage is a high-volume, high-friction workflow where small improvements compound (faster first response, fewer misroutes, more consistent policy adherence) and bilingual coverage is essential for GCC operations.
- **Why Claude Sonnet over smaller/cheaper models**: Higher reliability on structured JSON, nuanced intent separation, and natural Arabic customer-service copy reduced failure rates during iteration; smaller models tended to degrade on bilingual + policy-grounded constraints.
- **Why Streamlit**: Fastest path to a usable internal ops UI with minimal frontend overhead, ideal for prototyping and stakeholder feedback.
- **What was cut**: Voice input, full RAG over a product catalog/CRM, and multi-turn conversation memory (this prototype is single-email, single-shot).
- **Known failure modes**: Very long mixed-language emails, highly informal Arabic slang, and ambiguous multi-intent threads can reduce confidence and force clarification.
- **Next steps with more time**: Add stronger policy clause retrieval/citation checks, expand synthetic + real-world eval sets, implement safe escalation workflows, and integrate with ticketing (Zendesk/Freshdesk) + order lookup.

### Future Scope: Hybrid Model Routing

Not every message needs the same model or the same speed. For high-impact, real-time channels like live chat or instant messaging, health-critical situations (urgency 5) such as a newborn formula delay, an allergic reaction report, or a recalled product inquiry should be routed immediately to the strongest available model (e.g., Claude Sonnet or GPT-4o) because the customer is actively waiting and a 1–3 hour delay is unacceptable. The routing signals already exist in this pipeline today: the urgency score and the intent classification.

For low-impact, asynchronous channels like email or ticket queues, many standard cases (delayed non-essential items, refund status, promo confusion, general inquiries) can tolerate a slower response window. These can be routed through a cheaper or free-tier model (for example via OpenRouter). To manage provider volatility, a production setup should use a three-model fallback chain (main → backup → second backup), and if all fail, notify a human agent with the original email and error attached. The result is premium AI where urgency demands it, and near-zero cost where it doesn’t, without changing the schema or downstream workflow.

For a longer-form discussion, see `TRADEOFFS.md`.

## Tooling

- **Claude Sonnet (Anthropic API)** — triage inference, bilingual reply generation, policy-grounded structured output(GPT-4o or Gemini 2.0 Flash would be preferred in production for cost efficiency — used Claude here as I had remaining tokens)
- **Cursor**  — project scaffolding, boilerplate, rapid iteration on schema and pipeline wiring
- **What Cursor generated vs what was written manually**: Cursor generated the initial scaffolding and iterative stubs; core schema constraints, rubric rules, and policy text were refined manually to match the assessment requirements.
- **Prompts that shaped the system prompt**: Explicit “JSON-only”, “cite numbered policy clauses”, bilingual output constraints, and hard rules around confidence/clarification and urgency 5.
- **Where I overruled the agent**: Tightened schema invariants and eval constraints to prevent “looks-correct” but unsafe outputs (e.g., drafting a reply when clarification is required).

The Streamlit app also includes an optional **Queue Dashboard (Demo)** backed by a local SQLite file. This is designed for demos and does not require LLM calls if you use demo mode.

