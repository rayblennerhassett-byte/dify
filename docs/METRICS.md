# 3. Metric Formal Definitions

**Status:** ✅ Fully Specified  
**Section ID:** S3  
**Math Notation:** ℝⁿ (n-dimensional Euclidean space)

---

## 3.1 Convergence Metric

**Definition:**
```
Δ_t = ||O_t - O_{t-1}||_2

where:
  O_t ∈ ℝᵏ   (output vector at iteration t)
  k = frontier dimension (grows for Classes A–C)
  ||·||_2 = Euclidean norm (MANDATORY)
```

**Convergence Condition (ALL THREE REQUIRED):**
```
(a) Delta:    Δ_t < ε for all t ∈ [T-K, T]
(b) Frontier: No new solutions in last K iterations
(c) Confidence: var(w) < 0.01 where w = confidence weights

where:
  ε = max(1e-8, 0.01 × ||O_0||_2)
  K = 10 (lookback window)
  T = current iteration
```

**Example:**
```python
import numpy as np

# Output vectors (Euclidean)
O_prev = np.array([42.5, 38.2, 40.1])  # Previous iteration
O_curr = np.array([42.5, 38.2, 40.1])  # Current iteration

# Compute delta
delta = np.linalg.norm(O_curr - O_prev, ord=2)  # L2 norm

# Check convergence criteria
eps = max(1e-8, 0.01 * np.linalg.norm(O_0, ord=2))
frontier_improved = False
confidence_var = np.var([0.85, 0.87, 0.86])

converged = (delta < eps) and (not frontier_improved) and (confidence_var < 0.01)
```

---

## 3.2 Arbitration Determinism

**3-Step Decision Rule (MANDATORY SEQUENCE):**

### Step 1: Relevance Comparison

```
relevance(intent) = 0.4 × (v / max_v) + 0.3 × α + 0.3 × h

where:
  v = proposed value [0, 100]
  α = agent authority (accepted / total proposals)
  h = historical success rate
  
Range: [0.0, 1.0]
```

**Decision Logic:**
```python
def step_1_relevance(intent_A, intent_B):
    rel_A = 0.4 * (intent_A.value / 100) + 0.3 * intent_A.authority + 0.3 * intent_A.history
    rel_B = 0.4 * (intent_B.value / 100) + 0.3 * intent_B.authority + 0.3 * intent_B.history
    
    if abs(rel_A - rel_B) > 0.01:  # Threshold: 0.01
        return argmax([rel_A, rel_B])  # 'A' or 'B'
    else:
        return None  # Go to Step 2
```

### Step 2: Utility Ranking

```
utility(intent) = P(success) × E[reward] - cost

Example (Class B):
  utility = 0.68 × 18.5 - 0.0375 = 12.548
```

**Decision Logic:**
```python
def step_2_utility(intent_A, intent_B):
    util_A = intent_A.success_prob * intent_A.expected_reward - intent_A.cost
    util_B = intent_B.success_prob * intent_B.expected_reward - intent_B.cost
    
    if abs(util_A - util_B) > 1e-6:  # Threshold: 1e-6
        return argmax([util_A, util_B])
    else:
        return None  # Go to Step 3
```

### Step 3: Seed-Based Softmax

```
score(intent) = exp(hash(intent, resource_id, seed) / temperature)

where:
  temperature = 0.1 (FIXED)
  hash = SHA-256(concat(intent_id, resource_id, seed))
  hash ∈ [0.0, 1.0] (via modulo normalization)
```

**Deterministic Argmax:**
```python
def step_3_softmax(intent_A, intent_B, seed, temp=0.1):
    hash_A = int(sha256(f"{intent_A.id}|{resource}|{seed}".encode()).hexdigest(), 16) % 1e6 / 1e6
    hash_B = int(sha256(f"{intent_B.id}|{resource}|{seed}".encode()).hexdigest(), 16) % 1e6 / 1e6
    
    score_A = np.exp(hash_A / temp)
    score_B = np.exp(hash_B / temp)
    
    return argmax([score_A, score_B])  # Deterministic, not probabilistic
```

---

## 3.3 Brier Score (Calibration)

```
B = (1/N) Σ(pᵢ - yᵢ)²

where:
  N = number of predictions
  pᵢ = predicted probability ∈ [0, 1]
  yᵢ = realized outcome ∈ {0, 1}
  B ∈ [0, 1]
```

**Interpretation:**
- B = 0: Perfect calibration
- B = 0.25: Random guessing (p = 0.5 always)
- B = 1: Worst predictions

**Verification Tolerance:** ± 0.01 absolute

---

## 3.4 Hypervolume (Multi-Objective)

**4D Objective Space:**
```
Objectives: (Accuracy, Cost, Latency, Robustness)
Reference Point: (0, 100, 10, 0)
```

**Hypervolume Computation:**
```python
def compute_hypervolume(frontier, ref_point=(0, 100, 10, 0)):
    volume = 0
    for solution in frontier:
        # Hyperbox dimensions
        a_gap = ref_point[0] - solution.accuracy    # [0, 1]
        c_gap = solution.cost - ref_point[1]        # [0, 99]
        l_gap = solution.latency - ref_point[2]     # [0, 9.9]
        r_gap = solution.robustness - ref_point[3]  # [0, 1]
        
        volume += a_gap * c_gap * l_gap * r_gap
    
    return volume
```

**Tolerance:** ± 3% relative

---

## 3.5 Expected Information Gain (EIG)

```
EIG = H(prior) - H(posterior)

where:
  H(X) = -Σ p(x) × log₂(p(x))  [in bits]
```

**Example (Binary Prediction):**
```python
import numpy as np

def entropy(p):
    """Shannon entropy in bits"""
    if p <= 0 or p >= 1:
        return 0
    return -p * np.log2(p) - (1-p) * np.log2(1-p)

# Prior: 60% chance of success
H_prior = entropy(0.6)  # 0.971 bits

# After tool call: 85% chance
H_posterior = entropy(0.85)  # 0.610 bits

EIG = H_prior - H_posterior  # 0.361 bits
```

**Tool Call Decision:**
```
cost(tool) = 0.01 + 0.05 × (100 - value) / 100
EIG_threshold = 1.0

if (EIG / cost) > threshold:
    CALL tool
else:
    USE heuristic
```

---

## 3.6 Summary: All Metrics

| Metric | Formula | Tolerance | Class |
|--------|---------|-----------|-------|
| **Convergence** | Δ_t = \|\|O_t - O_{t-1}\|\|_2 | < ε | A,B,C,D |
| **Arbitration** | relevance → utility → softmax | ±0 | B,D |
| **Brier** | (1/N)Σ(pᵢ-yᵢ)² | ±0.01 | B,C |
| **Hypervolume** | Σ volume(hyperbox) | ±3% | D |
| **EIG** | H(prior) - H(posterior) | ±5% | B,C |

---

**Section Status:** ✅ COMPLETE  
**Next:** [Section 4: Logging & Protocol](LOGGING.md)
