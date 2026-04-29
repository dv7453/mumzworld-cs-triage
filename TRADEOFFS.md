# TRADEOFFS

## Why this problem (email triage) vs alternatives
Mumzworld receives high-volume inbound emails in both English and Arabic. The work is repetitive (routing to the right queue) but high-impact: better triage improves response time, reduces agent back-and-forth, and prevents dangerous mistakes on baby health/safety issues. Compared to alternatives like “product recommendation” or “catalog Q&A”, triage is easier to evaluate deterministically (intent/urgency/clarification rules) and maps directly to measurable operational outcomes.
I chose this problem after reviewing public customer feedback that repeatedly highlighted breakdowns in support responsiveness and consistency, making triage quality a clear, observed pain point to address.

## Model choice reasoning (why Claude in this prototype)
This prototype uses Claude via the Anthropic API because it provided strong reliability on:
- **Strict structured JSON output** under tight constraints
- **Bilingual handling**, especially natural Gulf-style Arabic customer-service copy
- **Policy-grounded drafting** with citations and lower hallucination rates in practice

### Why not GPT‑4o / GPT‑4o‑mini (or OpenRouter free models) by default
Those models can work, but the tradeoff is operational risk:
- Smaller/cheaper models tend to degrade on **Arabic fluency** and **multi-constraint formatting** (JSON + policy citations + clarification rules).
- “Free” routing layers can be unreliable (rate limits / provider errors / model availability volatility), which is risky for a production workflow unless you implement fallbacks.

### Cost strategy in a real product (hybrid routing)
A production deployment should not use one model for every case:
- **High-risk / high-stakes** cases (health-critical, payment anomalies, escalation triggers, long multi-issue complaints) should use a higher-quality model.
- **Low-risk** cases (simple delivery updates, routine refund timing questions, basic promo confusion) can use a cheaper model.
This “hybrid router” approach reduces cost while keeping safety and Arabic quality where it matters.

## Architecture decisions

### Why RAG
The system must be grounded in policy and must cite clause numbers. Instead of stuffing the entire policy into each prompt, the pipeline retrieves only the most relevant clauses for a given email. This reduces prompt size, improves grounding, and keeps the “never invent policy” requirement realistic.

### Why ChromaDB (local)
ChromaDB provides:
- Fast local vector search
- Persistence without external infrastructure
- Simple developer experience for a small corpus (policy clauses)
This is appropriate for a take-home prototype that must run quickly on a laptop.

### Why local hashing embeddings (no embedding API)
Using a deterministic hashing-based embedding function avoids:
- Extra paid API calls
- Extra latency
- Dependency on an external embedding provider
For a small internal policy document, this is sufficient to retrieve relevant clauses.

### Why Pydantic v2 validation
The hardest requirement is “no silent failures”. Pydantic provides strict schema validation and cross-field invariants so the system can fail fast when the model output is unsafe, incomplete, or inconsistent (e.g., drafting a reply when clarification is required).

## What was cut (scope) and why
- **Multi-turn conversation memory**: kept single-shot to ensure determinism and easier evaluation.
- **CRM/order lookup integration**: would require external systems and credentials; mocked instead via clarification mode (ask for order id).
- **Agent-side actions** (create ticket, dispatch courier calls): out of scope for a prototype; represented by `escalate` intent and urgency.
- **Full policy/product catalog RAG**: policy-only RAG demonstrates the pattern without building a full enterprise search system.

## What I would build next with more time
- Add a true “agent workflow” layer: create a ticket, assign queue, store outcome, and gather human feedback for continuous improvement.
- Add automatic policy-citation verification (ensure citations actually support the claim in the reply).
- Expand evals with real anonymized historical emails (with approval), and measure:
  - misroute rate
  - time-to-first-response
  - safety escalations caught
- Implement multi-model fallback for reliability (main + two backups) and a human fallback when all fail.

## Known failure modes (and mitigations)
- **Very short / vague emails**: handled by clarification mode (no reply; ask for missing details).
- **Mixed-language or highly informal slang Arabic**: can reduce confidence; clarification is preferable to guessing.
- **Model formatting drift (code fences, missing fields)**: mitigated by post-processing and strict Pydantic validation.
- **Ambiguous “exchange” wording when the issue is wrong item**: mitigated via deterministic routing overrides (wrong-item signals win).
- **Provider/model availability errors**: mitigated by model fallback logic and (in a production setting) multi-provider redundancy.

