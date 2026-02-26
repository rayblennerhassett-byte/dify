import networkx as nx
from .base import WorkloadBase
from ..core.determinism import DeterministicRNG


class ClassA(WorkloadBase):
    """
    Class A: Deterministic Graph Orchestration.
    Implements a 25-node, 5-layer DAG with 3 agents.
    """

    def __init__(self, seed=0xDEADBEEF):
        super().__init__("ClassA")
        self.seed = seed
        self.dag = self._generate_dag()
        self.layers = self._get_layers()

    def _generate_dag(self):
        """Generates the 25-node 5-layer DAG as per Section 2.1"""
        G = nx.DiGraph()
        # Layers definition
        layers = {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7],
            2: [8, 9, 10, 11, 12],
            3: [13, 14, 15, 16, 17],
            4: [18, 19, 20, 21, 22, 23, 24],
        }
        for nodes in layers.values():
            G.add_nodes_from(nodes)

        # Edge generation with deterministic RNG
        rng = DeterministicRNG(self.seed)
        # Use Branch 1 for graph generation structure
        gen = rng.get_generator(1)

        for layer_id in range(4):
            sources = layers[layer_id]
            targets = layers[layer_id + 1]
            for src in sources:
                # Pick 2 targets deterministically
                # Note: using bit generator directly for index sampling
                idx1 = int(gen.random() * len(targets))
                idx2 = int(gen.random() * len(targets))
                G.add_edge(src, targets[idx1], weight=0.5, reward=10.0)
                G.add_edge(src, targets[idx2], weight=0.6, reward=12.0)
        return G

    def _get_layers(self):
        return {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7],
            2: [8, 9, 10, 11, 12],
            3: [13, 14, 15, 16, 17],
            4: [18, 19, 20, 21, 22, 23, 24],
        }

    def generate_intents(self, iteration: int):
        """
        Agent A1: Layers 0-1
        Agent A2: Layers 2-3
        Agent A3: Layer 4
        """
        intents = []
        # Simplified deterministic heuristic: shuffle based on iteration
        for agent_id, role in enumerate([(0, 1), (2, 3), (4,)], 1):
            for layer_id in role:
                layer_nodes = self.layers[layer_id]
                # Deterministic shuffle heuristic as per Section 2.1
                heuristic_val = (iteration * agent_id + layer_id) % 10
                # Copy and shuffle
                proposed = list(layer_nodes)
                # Seed a local RNG for the shuffle to keep it deterministic
                local_rng = np.random.default_rng(heuristic_val)
                local_rng.shuffle(proposed)

                intents.append(
                    {
                        "id": f"INT_A{agent_id}_L{layer_id}_I{iteration}",
                        "agent_id": f"A{agent_id}",
                        "layer_id": layer_id,
                        "proposed_ordering": proposed,
                        "iteration": iteration,
                    }
                )
        return intents

    def run(self, iteration: int):
        intents = self.generate_intents(iteration)
        # Class A has 0 conflicts by design (disjoint layers)
        return {
            "iteration": iteration,
            "intents": intents,
            "conflicts": [],
            "state_snapshot": {
                "nodes": list(self.dag.nodes),
                "edges": list(self.dag.edges(data=True)),
            },
        }
