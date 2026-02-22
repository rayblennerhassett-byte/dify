# 2. Workload Class Definitions

**Status:** ✅ Fully Specified  
**Section ID:** S2  
**Variants:** 11 total (1 + 3 + 4 + 3)

---

## 2.1 Class A: Deterministic Graph Orchestration

**Purpose:** Baseline deterministic workload (no stochasticity)  
**Expected Iterations:** < 50  
**Conflicts:** 0 (by design)

### Graph Structure

```
Topology: 5-layer DAG
  Layer 0: {0, 1, 2}           (sources)
  Layer 1: {3, 4, 5, 6, 7}     (2 edges per source)
  Layer 2: {8, 9, 10, 11, 12}
  Layer 3: {13, 14, 15, 16, 17}
  Layer 4: {18–24}             (sinks)

Node Count: 25 total
Edge Generation: seed=0xDEADBEEF (deterministic)
```

**Edge Definition:**
```csv
from,to,cost,reward
0,3,0.5,10.0
0,4,0.7,12.0
1,3,0.6,11.0
1,5,0.4,9.0
2,4,0.8,13.0
2,6,0.3,8.0
... [complete edge list]
```

### Agent Configuration

```
Count: 3 agents {A1, A2, A3}
Assignment:
  A1: Optimize layers 0–1
  A2: Optimize layers 2–3
  A3: Optimize layer 4
```

### Intent Generation

```python
def generate_intent(agent_id, layer_id, iteration):
    # Intent: reorder layer by heuristic
    heuristic_value = (iteration * agent_id + layer_id) % 10
    proposed_ordering = shuffle(layer_nodes, seed=heuristic_value)
    return {
        "agent_id": agent_id,
        "layer_id": layer_id,
        "proposed_ordering": proposed_ordering,
        "iteration": iteration
    }
```

### Convergence Criteria (MANDATORY: ALL THREE)

```
(a) Delta Stasis:
    Δ_t < ε for all t ∈ [T-10, T]
    ε = max(1e-8, 0.01 × ||O_0||_2)

(b) Frontier Improvement = 0:
    No new orderings added in last 10 iterations

(c) Confidence Variance:
    var(confidence_weights) < 0.01
```

### Verification Checks

```
Convergence Iterations: Must match primary exactly (±0 tolerance)
Conflict Rate: ≤ 0.001 (expected: 0)
Frontier Match: Set equality required
```

---

## 2.2 Class B: High-Conflict Arbitration

**Purpose:** Test arbitration determinism under conflict  
**Expected Conflicts:** ≥ 0.35 probability per node per iteration  
**Variants:** 3 (agents ∈ {3, 10, 25})

### Resource Allocation Problem

```
Nodes: 40 (resource allocation decisions)
Agents: 10 (configurable: 3, 10, 25 for scaling test)
Intents per Agent: 2 per iteration (20 total intents)
Intent Space: value ∈ [0, 100] per node
Collision Probability: ≥ 0.35 (Poisson model)
```

### Intent Generation (Deterministic)

```python
def generate_intent(agent_j, node_k, iteration, seed):
    # Deterministic value generation
    value = (seed + iteration*10 + agent_j*5 + node_k*3) % 100
    return {
        "agent_id": f"A{agent_j}",
        "node_id": node_k,
        "proposed_value": value,
        "confidence": 0.7 + 0.3 * (value / 100)
    }
```

### Tool Stubs

**Tool 1: evaluate_proposal**
```python
def evaluate_proposal(proposal_value):
    cost = 0.01 + 0.05 * (100 - proposal_value) / 100
    relevance = 0.5 + 0.5 * (proposal_value / 100)
    return {
        "cost": cost,
        "relevance": relevance,
        "success_probability": 0.5 + 0.3 * (proposal_value / 100)
    }
```

**Tool 2: validate_feasibility**
```python
def validate_feasibility(proposal_set):
    cost = 0.1 * len(proposal_set)
    is_feasible = all(p <= 100 for p in proposal_set)
    return {"cost": cost, "feasible": is_feasible}
```

### Arbitration (3-Step Rule)

```
Step 1: Compare relevance scores
  If diff > 0.01: winner = argmax(relevance)
  Else: Step 2

Step 2: Compare utility
  If diff > 1e-6: winner = argmax(utility)
  Else: Step 3

Step 3: Softmax tie-breaking
  score(intent) = exp(hash(intent, seed) / 0.1)
  winner = argmax(score)
```

### Verification Checks

```
Arbitration Winner: 100% agreement (no divergence allowed)
Deadlock Detection: Max 3 consecutive reversals → FLAG
Rollback Rate: ≤ 5% (conflicts / total proposals)
```

---

## 2.3 Class C: High-Uncertainty Monte Carlo

**Purpose:** Test stochastic consistency with seeded RNG  
**Samples:** 10^4 per node per iteration  
**Variants:** 4 (samples ∈ {100, 1000, 10000, 100000})

### Problem Setup

```
Nodes: 30 (decision nodes with uncertain rewards)
Reward Distribution: R_i ~ Normal(μ_i, σ_i)
Parameters: Fixed per workload (see appendix)
Sampling: Deterministic via seeded RNG
```

### Monte Carlo Sampling

```python
def sample_rewards(node_id, iteration, seed, n_samples=10000):
    # Seed per (seed, iteration, node_id)
    rng_seed = hash(seed, iteration, node_id)
    rng = PCG64(rng_seed)
    
    samples = []
    for _ in range(n_samples):
        u = rng.random()  # [0, 1)
        # Box-Muller transform
        z = np.sqrt(-2 * np.log(u))
        sample = mu[node_id] + sigma[node_id] * z
        samples.append(sample)
    
    return np.array(samples)
```

### Convergence (Expected Value Stabilization)

```
Criterion 1: E[node_i] converges (std < 0.01 * mean)
Criterion 2: Frontier improvement < 0.001 for 15 iterations
Criterion 3: Confidence variance < 0.01
```

### Verification Checks

```
Expected Value Equivalence: |E_peer - E_primary| / E_primary ≤ 2%
Tail Risk (Q95): |Q95_peer - Q95_primary| / Q95_primary ≤ 5%
Scaling: convergence ~ O(1/sqrt(S)) where S = sample count
```

---

## 2.4 Class D: Multi-Objective Pareto Frontier

**Purpose:** Test frontier correctness and hypervolume  
**Objectives:** 4 (Accuracy, Cost, Latency, Robustness)  
**Solutions:** 50 candidates  
**Variants:** 3 (agents ∈ {3, 5, 10})

### Objective Space

```
Accuracy:   A ∈ [0, 1]   (maximize)
Cost:       C ∈ [1, 100] (minimize)
Latency:    L ∈ [0.1, 10.0] seconds (minimize)
Robustness: R ∈ [0, 1]   (maximize)
```

### Pareto Dominance

```
Solution X dominates Y if:
  X.A ≥ Y.A AND X.C ≤ Y.C AND X.L ≤ Y.L AND X.R ≥ Y.R
  AND at least one inequality is strict

Epsilon-Dominance Tolerance: 1e-6 per objective
```

### Frontier Definition

```python
def is_pareto_optimal(solution, candidates):
    for other in candidates:
        if dominates(other, solution):
            return False
    return True

def compute_frontier(candidates):
    frontier = [c for c in candidates if is_pareto_optimal(c, candidates)]
    return frontier
```

### Hypervolume Computation

```python
def compute_hypervolume(frontier, ref_point=(0, 100, 10, 0)):
    volume = 0
    for solution in frontier:
        hyperbox = (
            ref_point[0] - solution.A,    # Accuracy gap
            solution.C - ref_point[1],     # Cost gap (inverted)
            solution.L - ref_point[2],     # Latency gap (inverted)
            solution.R - ref_point[3]      # Robustness gap
        )
        volume += np.prod(hyperbox)
    return volume
```

### Verification Checks

```
Frontier Match: F_peer == F_primary (exact set equality)
Hypervolume: |HV_peer - HV_primary| / HV_primary ≤ 3%
Dominated Solutions: 0 (none in frontier)
```

---

## Summary: Workload Specifications

| Class | Nodes | Agents | Conflicts | Convergence | Variants |
|-------|-------|--------|-----------|-------------|----------|
| **A** | 25 (DAG) | 3 | 0 | 3 criteria | 1 |
| **B** | 40 (full) | 10 | ≥0.35 | Arbitration | 3 (N=3,10,25) |
| **C** | 30 | 10 | Variable | E[R] stable | 4 (S=10^2–10^5) |
| **D** | 50 | 10 | Variable | Frontier | 3 (A=3,5,10) |

**Total Variants:** 11 (1+3+4+3)  
**Trials per Variant:** 30 minimum  
**Total Trials:** 330 minimum

---

**Section Status:** ✅ COMPLETE  
**Next:** [Section 3: Metric Definitions](METRICS.md)
