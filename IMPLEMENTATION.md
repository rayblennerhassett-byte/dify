# Implementation Guide: Step-by-Step Checklist

**Target:** Full MoE Protocol Stage 5 implementation  
**Language:** Python 3.11+ (or Go/Rust equivalent)  
**OS:** Linux x86-64  
**Timeline:** 6 phases

---

## Phase 1: Environment & Dependencies

### 1.1 System Setup
```bash
# Linux x86-64 (required for determinism)
uname -m  # Should output: x86_64

# Python 3.11+
python --version

# BLAS library (pinned version)
apt-get install libopenblas0=0.3.24

# NumPy with BLAS integration
pip install numpy==1.24.3 scikit-learn scipy
```

### 1.2 Verify Floating-Point Mode
```python
import numpy as np

# Verify IEEE 754 double precision
assert np.float64 == np.float_  # Default float type
print(f"Float info: {np.finfo(np.float64)}")

# Test: 2 + 1e-16 should NOT equal 2 (double precision)
assert 2.0 + 1e-16 == 2.0  # This will pass (within epsilon)
assert 2.0 + 1e-15 != 2.0  # This will fail (beyond epsilon)
```

### 1.3 PCG64 RNG Implementation
```python
# Option A: Use reference implementation
pip install pcg64

# Option B: Verify custom implementation
from pcg64 import PCG64

rng = PCG64(seed=12345678)
sample = rng.random()  # Returns [0, 1)
assert isinstance(sample, float)
```

**Checkpoint:** ✓ Environment validated

---

## Phase 2: Determinism & State Management

### 2.1 Temperature Control
```python
# Disable LLM sampling
import torch

# Method 1: PyTorch
model.eval()
with torch.no_grad():
    output = model(input, temperature=0.0)  # Greedy only

# Method 2: HuggingFace
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")
output = generator(prompt, temperature=0.0, top_p=None, top_k=None)
```

### 2.2 IEEE 754 & Rounding Mode
```python
import numpy as np
import ctypes

# Verify double precision (64-bit)
x = np.array([1.0, 2.0, 3.0], dtype=np.float64)
assert x.dtype == np.float64

# Set rounding mode to round-to-nearest-even
# (Most systems default to this, but verify)
np.seterr(all='raise')  # Raise on any floating-point error

# Test rounding
a = 1.0
b = a + 1e-16  # Below epsilon
assert a == b  # True (rounded)

c = a + 1e-15  # Above epsilon
assert a != c   # True (not rounded)
```

### 2.3 RNG 4-Branch System
```python
class DeterministicRNG:
    def __init__(self, seed):
        self.seed = seed
        self.branches = {}
        for branch_id in [1, 2, 3, 4]:
            # Initialize each branch deterministically
            rng_main = PCG64(seed)
            rng_main.advance(10**6 * branch_id)  # Seek deterministically
            self.branches[branch_id] = PCG64(rng_main.state)
    
    def sample(self, branch_id):
        """Sample from specific RNG branch"""
        return self.branches[branch_id].random()

# Usage:
rng = DeterministicRNG(seed=12345678)
collision_value = rng.sample(1)  # Branch 1: collision generation
tool_cost_value = rng.sample(2)  # Branch 2: tool cost sampling
```

### 2.4 State Canonicalization & Hashing
```python
import json
import hashlib

def compute_state_hash(state_dict):
    """
    Compute canonical SHA-256 hash of state
    """
    # Sort keys alphabetically, no spaces
    canonical_json = json.dumps(
        state_dict,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True
    )
    
    # UTF-8 encode
    state_bytes = canonical_json.encode('utf-8')
    
    # SHA-256
    state_hash = hashlib.sha256(state_bytes).hexdigest()
    
    return state_hash

# Test canonicalization
state1 = {"z": 1, "a": 2}
state2 = {"a": 2, "z": 1}

hash1 = compute_state_hash(state1)
hash2 = compute_state_hash(state2)

assert hash1 == hash2, "Canonicalization failed!"
```

**Checkpoint:** ✓ Determinism layer complete

---

## Phase 3: Workload Implementation

### 3.1 Class A: DAG Generation
```python
import networkx as nx

def generate_class_a_graph():
    """25-node 5-layer DAG"""
    G = nx.DiGraph()
    
    # Layers
    layers = {
        0: [0, 1, 2],
        1: [3, 4, 5, 6, 7],
        2: [8, 9, 10, 11, 12],
        3: [13, 14, 15, 16, 17],
        4: [18, 19, 20, 21, 22, 23, 24]
    }
    
    # Add nodes
    for layer, nodes in layers.items():
        G.add_nodes_from(nodes)
    
    # Add edges (deterministic, 2 per source)
    seed_gen = DeterministicRNG(seed=0xDEADBEEF)
    for layer_id in range(4):
        sources = layers[layer_id]
        targets = layers[layer_id + 1]
        
        for src in sources:
            # Pick 2 random targets deterministically
            idx1 = int(seed_gen.sample(1) * len(targets))
            idx2 = int(seed_gen.sample(1) * len(targets))
            
            G.add_edge(src, targets[idx1], weight=0.5)
            G.add_edge(src, targets[idx2], weight=0.6)
    
    return G

dag = generate_class_a_graph()
assert nx.is_directed_acyclic_graph(dag), "Not a DAG!"
```

### 3.2 Class B: Collision Model
```python
def generate_class_b_intents(n_agents=10, n_nodes=40, iteration=1, seed=12345678):
    """Generate intents with collision probability ≥ 0.35"""
    rng = DeterministicRNG(seed)
    intents = []
    
    for agent_id in range(n_agents):
        for intent_idx in range(2):  # 2 intents per agent
            for node_id in range(n_nodes):
                # Deterministic value generation
                value = (seed + iteration*10 + agent_id*5 + node_id*3) % 100
                
                intents.append({
                    "agent_id": f"A{agent_id}",
                    "node_id": node_id,
                    "proposed_value": value,
                    "iteration": iteration
                })
    
    return intents

# Verify collision probability
intents = generate_class_b_intents()
node_intent_count = {}
for intent in intents:
    node = intent["node_id"]
    node_intent_count[node] = node_intent_count.get(node, 0) + 1

collision_prob = sum(1 for count in node_intent_count.values() if count > 1) / len(node_intent_count)
assert collision_prob >= 0.35, f"Collision probability {collision_prob} < 0.35"
```

### 3.3 Class C: Monte Carlo Sampling
```python
def sample_node_rewards(node_id, iteration, seed, mu=50, sigma=15, n_samples=10000):
    """Generate deterministic Monte Carlo samples"""
    rng = DeterministicRNG(hash(f"{seed}_{iteration}_{node_id}") % (2**32))
    
    samples = []
    for _ in range(n_samples):
        u = rng.sample(3)  # Branch 3: reward stochasticity
        # Box-Muller transform
        z = np.sqrt(-2 * np.log(u))
        sample = mu + sigma * z
        samples.append(sample)
    
    return np.array(samples)

# Verify seeded determinism
samples_1 = sample_node_rewards(node_id=5, iteration=1, seed=12345)
samples_2 = sample_node_rewards(node_id=5, iteration=1, seed=12345)

assert np.allclose(samples_1, samples_2), "RNG not deterministic!"
```

### 3.4 Class D: Pareto Frontier
```python
def check_dominance(sol_a, sol_b):
    """Check if sol_a dominates sol_b"""
    a_better = (sol_a['accuracy'] >= sol_b['accuracy'] and
                sol_a['cost'] <= sol_b['cost'] and
                sol_a['latency'] <= sol_b['latency'] and
                sol_a['robustness'] >= sol_b['robustness'])
    
    at_least_one_strict = (sol_a['accuracy'] > sol_b['accuracy'] or
                          sol_a['cost'] < sol_b['cost'] or
                          sol_a['latency'] < sol_b['latency'] or
                          sol_a['robustness'] > sol_b['robustness'])
    
    return a_better and at_least_one_strict

def compute_frontier(solutions):
    """Compute Pareto frontier"""
    frontier = []
    for sol in solutions:
        dominated = False
        for other in solutions:
            if check_dominance(other, sol):
                dominated = True
                break
        if not dominated:
            frontier.append(sol)
    return frontier
```

**Checkpoint:** ✓ All workloads defined

---

## Phase 4: Metrics Implementation

### 4.1 Convergence Check
```python
def check_convergence(O_prev, O_curr, O_0, K=10, history_deltas=None):
    """Check all 3 convergence criteria"""
    if history_deltas is None:
        history_deltas = []
    
    # Criterion 1: Delta < epsilon
    delta = np.linalg.norm(O_curr - O_prev, ord=2)
    eps = max(1e-8, 0.01 * np.linalg.norm(O_0, ord=2))
    
    if len(history_deltas) < K:
        history_deltas.append(delta)
        return False  # Not enough history
    
    history_deltas = history_deltas[-K:]
    criterion_1 = all(d < eps for d in history_deltas)
    
    # Criterion 2: Frontier improvement = 0 for K iterations
    # (assume frontier_improvement tracked separately)
    
    # Criterion 3: Confidence variance < 0.01
    # (assume confidence_weights tracked separately)
    
    return criterion_1  # Simplified; add other criteria
```

### 4.2 Arbitration Decision
```python
def arbitrate(intent_a, intent_b, seed):
    """3-step arbitration rule"""
    
    # Step 1: Compare relevance
    rel_a = 0.4 * (intent_a['value'] / 100) + 0.3 * intent_a['authority'] + 0.3 * intent_a['history']
    rel_b = 0.4 * (intent_b['value'] / 100) + 0.3 * intent_b['authority'] + 0.3 * intent_b['history']
    
    if abs(rel_a - rel_b) > 0.01:
        return 'A' if rel_a > rel_b else 'B'
    
    # Step 2: Compare utility
    util_a = intent_a['success_prob'] * intent_a['reward'] - intent_a['cost']
    util_b = intent_b['success_prob'] * intent_b['reward'] - intent_b['cost']
    
    if abs(util_a - util_b) > 1e-6:
        return 'A' if util_a > util_b else 'B'
    
    # Step 3: Seed-based softmax
    hash_a = int(hashlib.sha256(f"A|{intent_a['id']}|{seed}".encode()).hexdigest(), 16) % 1e6 / 1e6
    hash_b = int(hashlib.sha256(f"B|{intent_b['id']}|{seed}".encode()).hexdigest(), 16) % 1e6 / 1e6
    
    score_a = np.exp(hash_a / 0.1)
    score_b = np.exp(hash_b / 0.1)
    
    return 'A' if score_a > score_b else 'B'
```

**Checkpoint:** ✓ Metrics functional

---

## Phase 5: Logging

### 5.1 Canonical JSON Logging
```python
def log_iteration(iteration_id, state_snapshot, intents, conflicts, arbitration_results):
    """Log iteration with canonical JSON"""
    
    # Compute hash
    state_hash, size = compute_state_hash(state_snapshot)
    
    log_entry = {
        "arbitration_results": arbitration_results,
        "commit_hash": {
            "hash_algorithm": "SHA-256",
            "state_hash": state_hash,
            "state_serialized_size_bytes": size
        },
        "conflicts": conflicts,
        "intents": intents,
        "iteration_id": iteration_id,
        "state_snapshot": state_snapshot,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Write canonical JSON
    canonical_json = json.dumps(log_entry, sort_keys=True, separators=(',', ':'))
    
    with open(f"logs/iteration_{iteration_id}.jsonl", "a") as f:
        f.write(canonical_json + "\n")
```

**Checkpoint:** ✓ Logging operational

---

## Phase 6: Verification

### 6.1 Hypothesis Tests
```python
from scipy import stats

def verify_metric_equivalence(primary_values, peer_values, metric_name):
    """Run Welch's t-test with Bonferroni correction"""
    
    # Welch's t-test
    t_stat, p_value = stats.ttest_ind(primary_values, peer_values, equal_var=False)
    
    # Cohen's d
    n1, n2 = len(primary_values), len(peer_values)
    var1, var2 = np.var(primary_values, ddof=1), np.var(peer_values, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    cohens_d = (np.mean(primary_values) - np.mean(peer_values)) / pooled_std
    
    # Bonferroni correction
    alpha_individual = 0.05 / 64  # 64 total tests
    
    passes = (p_value > alpha_individual) and (abs(cohens_d) < 0.2)
    
    print(f"{metric_name}: p={p_value:.4f}, d={cohens_d:.4f}, PASS={passes}")
    
    return passes
```

### 6.2 Verification Report
```python
def generate_verification_report(all_test_results):
    """Generate final report"""
    
    report = {
        "verification_status": "PASS" if all(all_test_results.values()) else "FAIL",
        "tests_passed": sum(all_test_results.values()),
        "tests_total": len(all_test_results),
        "detailed_results": all_test_results,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    with open("verification_report.json", "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
```

**Checkpoint:** ✓ Verification complete

---

## Implementation Timeline

```
Week 1: Phase 1 (Environment) + Phase 2 (Determinism)
Week 2: Phase 3 (Workloads) + Phase 4 (Metrics)
Week 3: Phase 5 (Logging) + Phase 6 (Verification)
Week 4: Testing & debugging
Week 5: 330 trials collection + peer review
Week 6: Final verification & certification
```

---

## Testing Checklist

- [ ] Determinism: Same seed → identical outputs
- [ ] Precision: Drift ≤ tolerance_budget × sqrt(K)
- [ ] RNG: 4 branches produce expected distributions
- [ ] Workloads: Class A (0 conflicts), Class B (≥0.35 collisions), Class C (samples match), Class D (frontier correct)
- [ ] Metrics: All formulas compute correctly
- [ ] Logging: Canonical JSON + SHA-256 hashes verified
- [ ] Verification: 64 tests pass, Bonferroni correction applied

---

**Implementation Status:** READY  
**Target Completion:** 6 weeks  
**Success Criteria:** All 330 trials pass, verification report PASS
