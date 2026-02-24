"""Arbitration utilities for MoE Stage 5 (deterministic)."""

from __future__ import annotations
import math


def relevance(v, max_v, alpha, h):
    return 0.4 * (v / max_v) + 0.3 * alpha + 0.3 * h


def utility(p_success, expected_reward, cost):
    return p_success * expected_reward - cost


def step1_winner(rel_a, rel_b, thresh=0.01):
    diff = abs(rel_a - rel_b)
    if diff > thresh:
        return 0 if rel_a > rel_b else 1
    return None


def step2_winner(util_a, util_b, thresh=1e-6):
    diff = abs(util_a - util_b)
    if diff > thresh:
        return 0 if util_a > util_b else 1
    return None


def step3_softmax(intent_a, intent_b, seed, temp=0.1):
    import hashlib

    key_a = f"{intent_a['id']}|{seed}"
    key_b = f"{intent_b['id']}|{seed}"
    ha = int(hashlib.sha256(key_a.encode()).hexdigest(), 16) % 1_000_000 / 1_000_000
    hb = int(hashlib.sha256(key_b.encode()).hexdigest(), 16) % 1_000_000 / 1_000_000
    sa = math.exp(ha / temp)
    sb = math.exp(hb / temp)
    return 0 if sa > sb else 1
