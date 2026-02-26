import math
import hashlib
import numpy as np


def compute_relevance(intent):
    """Formula: 0.4v + 0.3a + 0.3h as per Section 3.2"""
    v = intent.get("value", 0)
    max_v = intent.get("max_value", 100)
    alpha = intent.get("authority", 0)
    h = intent.get("history", 0)
    return 0.4 * (v / max_v) + 0.3 * alpha + 0.3 * h


def compute_utility(intent):
    """Formula: P(success) * expected_reward - cost"""
    p_succ = intent.get("success_prob", 0)
    reward = intent.get("expected_reward", 0)
    cost = intent.get("cost", 0)
    return p_succ * reward - cost


def arbitrate(intent_a, intent_b, resource_id, seed):
    """
    3-Step Arbitration Rule as per Section 3.2.
    Returns: 'A' or 'B'
    """
    # Step 1: Relevance
    rel_a = compute_relevance(intent_a)
    rel_b = compute_relevance(intent_b)

    if abs(rel_a - rel_b) > 0.01:
        return "A" if rel_a > rel_b else "B"

    # Step 2: Utility
    util_a = compute_utility(intent_a)
    util_b = compute_utility(intent_b)

    if abs(util_a - util_b) > 1e-6:
        return "A" if util_a > util_b else "B"

    # Step 3: Seed-based Softmax (Deterministic Tie-break)
    # Using SHA-256(intent_id|resource_id|seed)
    def get_softmax_score(intent):
        input_str = f"{intent['id']}|{resource_id}|{seed}"
        h_hex = hashlib.sha256(input_str.encode()).hexdigest()
        # Normalization to [0, 1] as per Section 3.2
        val = int(h_hex, 16) % 1_000_000 / 1_000_000
        return math.exp(val / 0.1)

    score_a = get_softmax_score(intent_a)
    score_b = get_softmax_score(intent_b)

    return "A" if score_a > score_b else "B"
