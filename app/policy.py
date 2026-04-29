"""Policy context loading utilities.

Phase 1: only a minimal loader stub.
Phase 2+: policy chunking, clause extraction, and citation support.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PolicyContext:
    """Represents the policy document used to ground replies."""

    raw_markdown: str
    source_path: str


def load_policy(policy_path: str | Path) -> PolicyContext:
    """Load policy markdown from disk.

    TODO(phase2): parse into clauses with stable IDs for citations.
    """

    path = Path(policy_path)
    raw = path.read_text(encoding="utf-8")
    return PolicyContext(raw_markdown=raw, source_path=str(path))

