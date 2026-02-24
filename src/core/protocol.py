"""Protocol enforcement stubs for deterministic MoE Stage 5.

This module provides minimal checks and a pluggable interface for
enforcing the 3 deterministic protocol rules during execution.
"""

from __future__ import annotations


class ProtocolGuard:
    def __init__(self):
        self.mutated = False

    def mutate(self):
        self.mutated = True

    def is_mutated(self) -> bool:
        return self.mutated

    def reset(self):
        self.mutated = False
