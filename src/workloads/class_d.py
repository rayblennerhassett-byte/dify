"""Class D: Pareto Frontier (Skeleton)"""

from __future__ import annotations
from .base import WorkloadBase


class ClassD(WorkloadBase):
    def __init__(self):
        super().__init__("ClassD")
        self.solutions = 50

    def generate_frontier(self):
        frontier = []
        for i in range(self.solutions):
            frontier.append(
                {
                    "A": 0.8 - i * 0.01,
                    "C": 10 + i * 0.5,
                    "L": 1.0 + (i % 5) * 0.5,
                    "R": 0.2 + i * 0.01,
                }
            )
        return frontier

    def run(self, iteration: int):
        return {"iteration": iteration, "frontier": self.generate_frontier()}
