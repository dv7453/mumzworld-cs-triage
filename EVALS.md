# EVALS
## Summary
- Eval mode: live (Anthropic API)
- Dataset at time of run: `data/test_emails.json` (50 synthetic EN/AR cases)
- Passed: 50
- Failed: 2
- Average score: 89.80

### Results Table
| id | expected_intent | actual_intent | urgency | sentiment | clarification_needed | language_check | score | pass | error |
|---|---|---|---:|---|---|---|---:|---|---|
| test_001 | delivery_complaint | delivery_complaint | 2 | neutral | True | True | 100 | PASS |  |
| test_002 | wrong_item | wrong_item | 4 | neutral | False | True | 85 | PASS |  |
| test_003 | return_request | return_request | 1 | neutral | False | True | 80 | PASS |  |
| test_004 | delivery_complaint | return_request | 4 | neutral | False | True | 75 | PASS |  |
| test_005 | delivery_complaint | delivery_complaint | 5 | frustrated | False | True | 100 | PASS |  |
| test_006 | warranty_dispute | return_request | 5 | frustrated | False | True | 75 | PASS |  |
| test_007 | general_inquiry | general_inquiry | 5 | frustrated | False | True | 85 | PASS |  |
| test_008 | general_inquiry | general_inquiry | 1 | positive | False | True | 100 | PASS |  |
| test_009 | promotional_confusion | promotional_confusion | 2 | neutral | False | True | 100 | PASS |  |
| test_010 | escalate | escalate | 2 | frustrated | True | True | 80 | PASS |  |
| test_011 | delivery_complaint | delivery_complaint | 2 | neutral | False | True | 80 | PASS |  |
| test_012 | wrong_item | wrong_item | 5 | frustrated | False | True | 100 | PASS |  |
| test_013 | return_request | return_request | 2 | neutral | False | True | 100 | PASS |  |
| test_014 | delivery_complaint | escalate | 5 | frustrated | False | True | 75 | PASS |  |
| test_015 | warranty_dispute | escalate | 5 | frustrated | False | True | 75 | PASS |  |
| test_016 | general_inquiry | escalate | 5 | neutral | False | True | 75 | PASS |  |
| test_017 | escalate | escalate | 4 | frustrated | False | True | 100 | PASS |  |
| test_018 | general_inquiry | general_inquiry | 1 | neutral | False | True | 100 | PASS |  |
| test_019 | escalate | general_inquiry | 1 | neutral | False | True | 75 | PASS |  |
| test_020 | general_inquiry | general_inquiry | 1 | positive | False | True | 100 | PASS |  |
| test_021 | return_request | return_request | 2 | neutral | False | True | 100 | PASS |  |
| test_022 | delivery_complaint | delivery_complaint | 3 | neutral | False | True | 85 | PASS |  |
| test_023 | refund_request | refund_request | 2 | neutral | False | True | 100 | PASS |  |
| test_024 | exchange_request | exchange_request | 2 | neutral | False | True | 100 | PASS |  |
| test_025 | general_inquiry | promotional_confusion | 2 | neutral | False | True | 75 | PASS |  |
| test_026 | promotional_confusion | promotional_confusion | 1 | neutral | False | True | 80 | PASS |  |
| test_027 | escalate | escalate | 5 | frustrated | False | True | 100 | PASS |  |
| test_028 | refund_request | refund_request | 2 | neutral | True | True | 100 | PASS |  |
| test_029 | escalate | escalate | 3 | frustrated | False | True | 80 | PASS |  |
| test_030 | wrong_item | wrong_item | 3 | neutral | False | True | 85 | PASS |  |
| test_031 | return_request | return_request | 2 | neutral | False | True | 100 | PASS |  |
| test_032 | escalate | escalate | 3 | frustrated | False | True | 80 | PASS |  |
| test_033 | refund_request | refund_request | 2 | neutral | False | True | 100 | PASS |  |
| test_034 | wrong_item | wrong_item | 3 | neutral | False | True | 100 | PASS |  |
| test_035 | exchange_request | exchange_request | 2 | neutral | False | True | 100 | PASS |  |
| test_036 | promotional_confusion | promotional_confusion | 2 | neutral | False | True | 100 | PASS |  |
| test_037 | general_inquiry | return_request | 2 | neutral | True | True | 75 | PASS |  |
| test_038 | refund_request | refund_request | 2 | frustrated | False | True | 100 | PASS |  |
| test_039 | delivery_complaint | delivery_complaint | 2 | neutral | False | True | 100 | PASS |  |
| test_040 | exchange_request | exchange_request | 2 | neutral | False | True | 100 | PASS |  |
| test_041 | return_request | return_request | 2 | neutral | True | True | 100 | PASS |  |
| test_042 | wrong_item | wrong_item | 2 | frustrated | False | True | 80 | PASS |  |
| test_043 | escalate | escalate | 5 | frustrated | False | True | 100 | PASS |  |
| test_044 | return_request | return_request | 2 | neutral | False | True | 100 | PASS |  |
| test_045 | refund_request | refund_request | 2 | neutral | False | True | 85 | PASS |  |
| test_046 | general_inquiry | return_request | 2 | neutral | True | True | 55 | FAIL |  |
| test_047 | general_inquiry | general_inquiry | 1 | neutral | False | True | 100 | PASS |  |
| test_048 | escalate | escalate | 3 | frustrated | False | True | 80 | PASS |  |
| test_049 | escalate | escalate | 3 | frustrated | False | True | 80 | PASS |  |
| test_050 | general_inquiry | general_inquiry | 1 | frustrated | False | True | 80 | PASS |  |
| test_051 | general_inquiry | general_inquiry | 1 | neutral | True | True | 100 | PASS |  |
| test_052 | general_inquiry |  |  |  |  |  | 0 | FAIL | JSONDecodeError |

## Notable Failures
Cases below 75 (or failing due to automatic failure / error):

- **test_046**: score=55, pass=False, error=none
  - expected_intent=general_inquiry
  - actual_intent=return_request
  - urgency=2
  - sentiment=neutral
  - clarification_needed=True
  - language_check=True
- **test_052**: score=0, pass=False, error=JSONDecodeError
  - expected_intent=general_inquiry
  - actual_intent=None
  - urgency=None
  - sentiment=None
  - clarification_needed=None
  - language_check=None

## Automatic Failures
None.

## Coverage Checklist (minimum-set sanity)
This repository includes a synthetic eval set in `data/test_emails.json` (now **50+ cases**, bilingual). The set includes at least:
- **Arabic inputs**: multiple Gulf Arabic cases (e.g., wrong item, formula delay).
- **Adversarial / ambiguous**: very short “where is my order?” + vague angry complaint → should trigger `clarification_needed`.
- **Health-critical urgency 5**: baby formula delay, allergy reaction, recall safety check.
- **Out-of-policy**: vendor onboarding request, phishing/spam, unsubscribe.
- **Gibberish / empty-ish**: dedicated low-signal cases (added in dataset) intended to trigger clarification mode rather than guessing.

## Partial Misses (Passed but imperfect)
Not all rows are perfect even when they PASS at the ≥75 threshold. For example, there are cases where:
- intent differs from the expected intent but the output still meets urgency/clarification/language requirements (score lands around 75–85).

## Named Failure Modes (observed during development)
- **Non-JSON output**: JSON wrapped in markdown code fences or extra prose.
- **Schema violations**: missing fields / empty strings / reply provided when clarification is required.
- **Language mismatch**: model claims Arabic but outputs English (or vice versa).
- **Intent confusion**: wrong-item vs exchange wording; vague complaints routed incorrectly.
- **Provider volatility**: rate limits / model not found / transient 5xx errors.

## Historical Reliability Notes (honest failures)
Earlier iterations (before adding post-processing + routing overrides) produced real failures, e.g.:
- **JSON parse failures** when the model wrapped output in ```json fences.
- **Validation failures** when `raw_input_language_check` was false.
- **External API/model availability issues** (404 model not found; transient provider errors).

These were addressed with:
- stripping markdown fences before JSON parsing
- deterministic language checks (don’t trust the model’s flag)
- deterministic routing overrides for common confusions (wrong-item vs exchange, escalation triggers)

## Eval Methodology
Each case is scored out of **100** using the rubric:

- intent_match: **25** (exact match)
- urgency_in_range: **20** (actual urgency >= expected_urgency_min)
- sentiment_match: **15** (exact match)
- clarification_correct: **20** (matches expected; if true, clarification_reason non-empty)
- reply_language_correct: **10** (raw_input_language_check is True)
- schema_valid: **10** (10 if schema validated; 0 if a TriageValidationError was caught)

Automatic failures override scoring (case fails regardless of score):

- suggested_reply is non-null when clarification_needed is True
- urgency is 5 but urgency_reasoning has no required health keywords
- policy_citations is an empty list when a policy-relevant intent is classified
