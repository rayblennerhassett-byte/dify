# 1. Determinism & Reproducibility

**Status:** ✅ Fully Specified  
**Section ID:** S1  
**References:** IEEE 754-2019, PCG Random v0.98

---

## 1.1 Determinism Contract (Binding)

All benchmark execution MUST comply with:

### 1.1.1 LLM Execution Model

```
Temperature: 0.0 (MANDATORY)
Decoding: Greedy (argmax tokens only)
Sampling: DISABLED (no nucleus, beam search, or stochastic sampling)
```

**Rationale:** LLM inference introduces uncontrolled entropy. Determinism requires fixed decoding.

**Implementation:**
- PyTorch: `torch.no_grad()` + greedy decoding
- HuggingFace: `temperature=0.0, top_p=None, top_k=None`
- Custom: Return argmax token only

**Non-LLM Arbitration (for verification):**
```python
def arbitrate(intent_A, intent_B, seed):
    # Deterministic code, not LLM
    relevance_A, relevance_B = compute_relevance(intent_A, intent_B)
    utility_A, utility_B = compute_utility(intent_A, intent_B)
    if abs(relevance_A - relevance_B) > 0.01:
        return argmax([relevance_A, relevance_B])
    elif abs(utility_A - utility_B) > 1e-6:
        return argmax([utility_A, utility_B])
    else:
        return seed_softmax([intent_A, intent_B], seed)
```

### 1.1.2 Numerical Precision

```
Standard:      IEEE 754 double precision (64-bit)
NO UPCONVERSION to long double
Rounding Mode: Round-to-nearest-even (banker's rounding)
BLAS:          Pinned version (OpenBLAS 0.3.24 or MKL equivalent)
```

**Tolerance Budget:**
```
Per-iteration drift:    ≤ 1e-10 (absolute)
Cumulative (K iter):    ≤ sqrt(K) × 1e-10
Convergence epsilon:    ε = max(1e-8, 0.01 × ||O_0||_2)
Peer grace period:      ± 2× tolerance (numerical reconstruction)
```

**Example:**
```python
import numpy as np

# CORRECT: IEEE 754 double
values = np.array([1.0, 2.0, 3.0], dtype=np.float64)
result = np.sum(values)  # Accumulation error bounded

# WRONG: Long double
values_ld = np.array([1.0, 2.0, 3.0], dtype=np.longdouble)
result_ld = np.sum(values_ld)  # Non-deterministic accumulation

# Drift check at iteration K
accumulated_drift = abs(result_peer - result_primary)
max_allowed = np.sqrt(K) * 1e-10
assert accumulated_drift <= max_allowed * 2  # With grace period
```

### 1.1.3 RNG Seeding & Entropy Allocation

**Algorithm:** PCG64 (Permuted Congruential Generator)
```
Version:     0.98 (reference https://www.pcg-random.org/)
Seed Type:   64-bit unsigned integer
Init:        PCG64(seed).initialize(workload_class, trial_number)
```

**Entropy Branch Allocation:**
```
Branch 1: Collision generation (Class A proposals, Class B intents)
Branch 2: Tool cost sampling (Class B tool invocations)
Branch 3: Reward stochasticity (Class C Monte Carlo sampling)
Branch 4: Tie-breaking (Arbitration softmax)
```

**Implementation:**
```python
from pcg64 import PCG64

# Create main RNG with seed
rng_main = PCG64(seed_value)

# Allocate branches with deterministic seeking
branches = {}
for branch_id in [1, 2, 3, 4]:
    rng_main.advance(10**6)  # Deterministic seek
    branches[branch_id] = PCG64(rng_main.state)

# Usage:
value_collision = branches[1].random()  # Always branch 1
value_tool_cost = branches[2].random()  # Always branch 2
```

**Logging (MANDATORY):**
```json
{
  "rng_call_id": 342,
  "branch_id": 1,
  "call_sequence": 342,
  "iteration": 5,
  "value_generated": 0.6234567890123456,
  "rng_algorithm": "PCG64",
  "seed_used": 12345678,
  "context": {"operation": "generate_intent_collision", "agent_id": "A1"}
}
```

### 1.1.4 Execution Parallelism Prohibition

```
SINGLE-THREADED ONLY
NO concurrent agent execution
NO async/await in control flow
Iteration N must COMPLETE before iteration N+1 starts
```

**Timing Guarantee:**
```
Iteration execution time variance ≤ 5% across runs
If variance > 5%: System is NON-DETERMINISTIC (FAIL)
```

**Tool Call Sequencing:**
```python
# CORRECT: Deterministic order
tool_calls = sorted(intents, key=lambda x: (x.agent_id, x.timestamp))
for call in tool_calls:
    result = execute_tool(call)  # Sequential, no parallelism

# WRONG: Non-deterministic order
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(execute_tool, intents)  # FORBIDDEN
```

### 1.1.5 State Serialization & Commit Hash

**Canonicalization Rules (MANDATORY):**

1. **Field Ordering:** Alphabetically sorted (case-sensitive)
   ```json
   {"agents": {...}, "conflicts": [...], "intents": [...]}  // CORRECT
   {"intents": [...], "agents": {...}, "conflicts": [...]}  // WRONG
   ```

2. **Float Format:** `%.17g` (17 significant digits)
   ```
   0.6234567890123456     (CORRECT)
   0.62345678901234567890 (WRONG: too many digits)
   1.234567890123456e-10  (CORRECT: lowercase 'e')
   1.234567890123456E-10  (WRONG: uppercase 'E')
   ```

3. **Hash Computation:**
   ```python
   import hashlib
   import json
   
   # Serialize with canonical field ordering
   canonical_json = json.dumps(state_snapshot, sort_keys=True, separators=(',', ':'))
   
   # Compute SHA-256
   state_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
   
   # Store
   log_entry = {
       "iteration": N,
       "state_hash": state_hash,
       "state_size_bytes": len(canonical_json)
   }
   ```

---

## 1.2 Verification Protocol for Determinism

### 1.2.1 Pre-Execution Validation

**Artifact Inventory (provided by primary):**
- Workload definition (JSON)
- RNG seed sequence (per trial)
- Tool stub library (cost/response model)
- Expected output log (all iterations)

**Environment Matching:**
```
CPU Architecture:    x86-64 (or ARM with explicit declaration)
OS:                  Linux (determinism hardest on Linux)
BLAS Library:        OpenBLAS 0.3.24+ (or MKL with same version)
Python/Go/Rust:      Within 1 minor version of primary
```

### 1.2.2 Checkpoint Verification

```
Every 10 iterations:
  1. Peer computes state_hash at iteration N = [0, 10, 20, ...]
  2. Compare: peer_hash[N] vs. primary_hash[N]
  3. If match: Continue to next checkpoint
  4. If divergence:
     a. Binary search the divergence point
     b. Log byte-level diff of serialized states
     c. FLAG as "Determinism Violation at Iteration M"
```

**Binary Search Example:**
```python
def find_divergence(primary_log, peer_log, start=0, end=10):
    if start == end:
        return start
    mid = (start + end) // 2
    if peer_log[mid] == primary_log[mid]:
        return find_divergence(primary_log, peer_log, mid+1, end)
    else:
        return find_divergence(primary_log, peer_log, start, mid)
```

### 1.2.3 Numerical Precision Check

```
At iteration M (e.g., M=100):
  drift = max(|peer_value[i] - primary_value[i]| for all state values i)
  max_allowed = tolerance_budget × sqrt(M)
  
  If drift <= max_allowed:           PASS
  If max_allowed < drift <= 2×:      PASS (grace period)
  If drift > 2× max_allowed:         FAIL ("Precision Budget Exceeded")
```

### 1.2.4 RNG Divergence Audit

```
Peer logs all RNG calls: {branch_id, call_seq, value}
Compare with primary's RNG log:
  
  If call_seq matches but values diverge:
    - Verify seeds are identical at branch start
    - If seeds match but values differ: RNG non-standard (FAIL)
    
  If call_seq differs:
    - One system called RNG more times
    - Likely due to different collision detection (investigate)
```

---

## 1.3 Summary: Determinism Guarantees

| Component | Specification | Verification |
|-----------|---|---|
| LLM | temp=0.0, greedy | Confirm in implementation |
| Precision | IEEE 754, ≤1e-10/iter | Checkpoint hashing |
| RNG | PCG64, 4 branches | RNG audit trail |
| State | Canonical JSON → SHA-256 | Hash comparison |
| Threading | Single-threaded only | Variance ≤ 5% |

**Result:** Peer and primary produce identical outputs within numerical tolerance.

---

**Section Status:** ✅ COMPLETE  
**Next:** [Section 2: Workload Definitions](WORKLOADS.md)
