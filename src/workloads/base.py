"""Abstract base for deterministic workload implementations.

Each workload must implement:
- generate_intents(iteration): produce a deterministic set of intents
- run(iteration): execute a single iteration and return a result snapshot
"""

from __future__ import annotations


class WorkloadBase:
    def __init__(self, name: str):
        self.name = name

    def generate_intents(self, iteration: int):  # pragma: no cover
        raise NotImplementedError

    def run(self, iteration: int):  # pragma: no cover
        raise NotImplementedError
