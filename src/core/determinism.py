"""Deterministic RNG primitives (PCG64-like) with 4 branches.

This module provides a lightweight Python implementation intended for
reproducible experiments in MoE Stage 5. It is not a full drop-in for
the PCG64 C reference but provides bitwise deterministic behavior suitable
for single-threaded simulations and deterministic branching.
"""

from __future__ import annotations

MASK64 = (1 << 64) - 1


def _rotl64(x: int, r: int) -> int:
    r &= 63
    return ((x << r) | (x >> (64 - r))) & MASK64


class _PCG64:
    def __init__(self, seed: int = 0):
        self._state = seed & MASK64

    def _step(self) -> None:
        # LCG-like step for deterministic progression (PCG64-like family)
        self._state = (self._state * 6364136223846793005 + 1442695040888963407) & MASK64

    def next_uint32(self) -> int:
        self._step()
        x = ((self._state >> 18) ^ self._state) >> 27
        rot = self._state >> 59
        return _rotl64(x & 0xFFFFFFFF, int(rot)) & 0xFFFFFFFF

    def random(self) -> float:
        # Produce a float in [0.0, 1.0)
        return self.next_uint32() / 2**32

    @property
    def state(self) -> int:
        return self._state


@staticmethod
def _mix_seed(seed: int, workload_class: int, trial_number: int) -> int:
    # Simple mixing to seed per-workload and trial
    return (seed ^ (workload_class * 0x9E3779B97F4A7C15) ^ (trial_number << 8)) & (
        (1 << 64) - 1
    )


class DeterministicRNG:
    """High-level RNG container exposing deterministic branches."""

    def __init__(self, seed: int, workload_class: int = 0, trial_number: int = 0):
        base = _mix_seed(seed, workload_class, trial_number)
        self._branches = {
            1: _PCG64(base ^ 0x1),  # collision generation
            2: _PCG64(base ^ 0x2),  # tool cost sampling
            3: _PCG64(base ^ 0x3),  # reward stochasticity
            4: _PCG64(base ^ 0x4),  # tie-breaking
        }
        # Deterministic branch seeding: advance by 1e6 per branch
        for bid, rng in self._branches.items():
            rng = self._branches[bid]
            rng.advance_cache = 0  # placeholder to keep lints happy
            for _ in range(1_000_000 * bid):
                rng._step()
            self._branches[bid] = rng

    def sample(self, branch_id: int) -> float:
        rng = self._branches[branch_id]
        return rng.random()
