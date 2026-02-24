"""Canonical JSON utilities and SHA-256 hashing for MoE Stage 5"""

from __future__ import annotations
import json
import hashlib


def canonical_json(obj) -> str:
    # Alphabetical ordering, no spaces, ASCII-only
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_state_hash(state_dict: object) -> tuple[str, int]:
    s = canonical_json(state_dict)
    b = s.encode("utf-8")
    h = hashlib.sha256(b).hexdigest()
    return h, len(b)
