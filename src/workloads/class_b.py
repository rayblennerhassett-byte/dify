"""Class B: High-Conflict Arbitration (Skeleton)"""

from __future__ import annotations
from .base import WorkloadBase


class ClassB(WorkloadBase):
    def __init__(self, variants=None):
        super().__init__("ClassB")
        self.variants = variants or [3, 10, 25]

    def generate_intents(self, iteration: int):
        intents = []
        for agent in range(2):
            for node in range(40):
                intents.append(
                    {
                        "agent_id": f"A{agent + 1}",
                        "node_id": node,
                        "proposed_value": (iteration * 7 + agent * 11 + node) % 101,
                    }
                )
        return intents

    def run(self, iteration: int):
        return {"iteration": iteration, "intents": self.generate_intents(iteration)}
