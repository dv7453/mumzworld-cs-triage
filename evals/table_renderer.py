"""Rich table rendering for eval results (extracted from eval_runner)."""

from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table


@dataclass(frozen=True)
class EvalRow:
    case_id: str
    expected_intent: str
    actual_intent: str | None
    urgency: int | None
    sentiment: str | None
    clarification_needed: bool | None
    language_check: bool | None
    total_score: int
    passed: bool
    automatic_failures: list[str]
    error: str | None = None


def render_table(console: Console, rows: list[EvalRow]) -> None:
    table = Table(title="Mumzworld Triage Evals")
    table.add_column("id", style="bold")
    table.add_column("intent", justify="left")
    table.add_column("urg", justify="right")
    table.add_column("sent", justify="left")
    table.add_column("clar", justify="left")
    table.add_column("lang_ok", justify="left")
    table.add_column("score", justify="right")
    table.add_column("pass", justify="left")

    for r in rows:
        intent_cell = (
            f"{r.actual_intent or '—'} (exp: {r.expected_intent})"
            if r.error is None
            else f"ERROR (exp: {r.expected_intent})"
        )
        table.add_row(
            r.case_id,
            intent_cell,
            str(r.urgency) if r.urgency is not None else "—",
            str(r.sentiment) if r.sentiment is not None else "—",
            str(r.clarification_needed) if r.clarification_needed is not None else "—",
            str(r.language_check) if r.language_check is not None else "—",
            str(r.total_score),
            "PASS" if r.passed else "FAIL",
        )

    console.print(table)

