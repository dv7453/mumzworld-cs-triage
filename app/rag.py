"""Minimal RAG over policy clauses using a local vector DB (Chroma).

This keeps the prototype honest: we retrieve only relevant clauses instead of
stuffing the full policy document into every prompt.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import chromadb
from chromadb.api.models.Collection import Collection

_CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)\s*$")


@dataclass(frozen=True)
class PolicyClause:
    clause_id: str  # e.g., "5.2"
    text: str


def parse_policy_clauses(policy_markdown: str) -> list[PolicyClause]:
    """Extract numbered clauses like `2.1 ...` from policy markdown."""

    clauses: list[PolicyClause] = []
    for line in policy_markdown.splitlines():
        m = _CLAUSE_RE.match(line)
        if not m:
            continue
        clause_id, text = m.group(1), m.group(2)
        clauses.append(PolicyClause(clause_id=clause_id, text=text))
    return clauses


class _LocalHashEmbeddingFunction:
    """Deterministic, local embedding function (no API calls, no token cost).

    It uses a simple hashing trick over word tokens into a fixed-size dense vector.
    This is sufficient for retrieving relevant clauses from a small policy document.
    """

    def __init__(self, *, dim: int = 512) -> None:
        self._dim = dim

    # Newer Chroma versions expect embedding functions to expose a stable name.
    @staticmethod
    def name() -> str:  # pragma: no cover
        return "local_hash_v1"

    def __call__(self, input: Iterable[str]) -> list[list[float]]:  # Chroma protocol
        return [_embed_text(t, dim=self._dim) for t in input]

    # Chroma's embedding function protocol expects these helper methods.
    def embed_documents(self, input: Iterable[str]) -> list[list[float]]:  # pragma: no cover
        return self(input)

    def embed_query(self, input: object) -> object:  # pragma: no cover
        # Chroma may pass either a single string or a list containing one string.
        if isinstance(input, list) and input:
            # When passed a list, return a single embedding wrapped in a list
            # to match Chroma's expected shape for batched queries.
            return [_embed_text(str(input[0]), dim=self._dim)]  # type: ignore[return-value]
        return _embed_text(str(input), dim=self._dim)


_WORD_RE = re.compile(r"[A-Za-z0-9]+|[\u0600-\u06FF]+")


def _embed_text(text: str, *, dim: int) -> list[float]:
    # Tokenize into alnum + Arabic blocks; ignore punctuation.
    tokens = _WORD_RE.findall((text or "").lower())
    vec = [0.0] * dim
    if not tokens:
        return vec

    for tok in tokens:
        h = hashlib.sha256(tok.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "little") % dim
        sign = 1.0 if (h[4] % 2 == 0) else -1.0
        vec[idx] += sign

    # L2 normalize for cosine similarity behavior.
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _get_collection(*, persist_dir: Path) -> Collection:
    client = chromadb.PersistentClient(path=str(persist_dir))
    return client.get_or_create_collection(
        # Bump collection name when index/embedding scheme changes.
        name="mumzworld_policy_clauses_v2_localhash",
        embedding_function=_LocalHashEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )


def ensure_policy_index(
    *,
    policy_path: Path,
    persist_dir: Path,
) -> None:
    """Create/update the policy clause index in Chroma."""

    # Ensure the persistence directory exists before opening Chroma.
    persist_dir.mkdir(parents=True, exist_ok=True)

    policy_text = policy_path.read_text(encoding="utf-8")
    clauses = parse_policy_clauses(policy_text)
    if not clauses:
        raise ValueError("No numbered clauses found in policy.md to index.")

    col = _get_collection(persist_dir=persist_dir)
    # Avoid re-upserting (and re-embedding) on every run.
    if col.count() == len(clauses):
        return
    ids = [c.clause_id for c in clauses]
    docs = [f"{c.clause_id} {c.text}" for c in clauses]
    metas = [{"clause_id": c.clause_id} for c in clauses]

    # Upsert keeps the index updated if the policy changes.
    col.upsert(ids=ids, documents=docs, metadatas=metas)


def retrieve_policy_clauses(
    *,
    query: str,
    policy_path: Path,
    persist_dir: Path,
    k: int = 6,
) -> list[PolicyClause]:
    """Retrieve top-K relevant policy clauses for a query."""

    ensure_policy_index(policy_path=policy_path, persist_dir=persist_dir)
    col = _get_collection(persist_dir=persist_dir)
    res = col.query(query_texts=[query], n_results=k)

    docs = (res.get("documents") or [[]])[0]
    clauses: list[PolicyClause] = []
    for d in docs:
        m = re.match(r"^(\d+\.\d+)\s+(.*)$", d.strip())
        if not m:
            continue
        clauses.append(PolicyClause(clause_id=m.group(1), text=m.group(2)))
    return clauses


def build_retrieved_policy_markdown(clauses: list[PolicyClause]) -> str:
    """Format retrieved clauses as markdown the model can cite by clause id."""

    lines = ["## Retrieved Policy Clauses"]
    for c in clauses:
        lines.append(f"- **{c.clause_id}** {c.text}")
    return "\n".join(lines)


def default_policy_paths() -> tuple[Path, Path]:
    """Return (policy_path, persist_dir) defaults relative to project root."""

    root = Path(__file__).resolve().parents[1]
    return root / "data" / "policy.md", root / ".chroma"

