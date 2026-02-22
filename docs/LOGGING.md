# 4. Logging Schema & Protocol

**Status:** ✅ Fully Specified  
**Section ID:** S4  
**Format:** Canonical JSON (JSONL)

---

## 4.1 Canonicalization Rules (MANDATORY)

### Rule 1: Field Ordering
```
All JSON objects MUST have fields sorted alphabetically (case-sensitive)

CORRECT:
{"agents": {...}, "conflicts": [...], "intents": [...]}

WRONG:
{"intents": [...], "agents": {...}, "conflicts": [...]}
```

### Rule 2: Float Format
```
Format:     %.17g (17 significant decimal digits)
Exponent:   lowercase 'e' only
Examples:
  0.6234567890123456     (CORRECT)
  0.62345678901234567890 (WRONG: too many)
  1.234567890123456e-10  (CORRECT)
  1.234567890123456E-10  (WRONG: uppercase)
```

### Rule 3: Integer Format
```
No decimal point: 1, not 1.0
No leading zeros: 42, not 042
Negative: -5, not -05
```

### Rule 4: Boolean & Null
```
Booleans: lowercase only (true, false)
Null: null (lowercase)

CORRECT: {"flag": true, "value": null}
WRONG:   {"flag": True, "value": None}
```

### Rule 5: Array Ordering
```
Preserve generation order (do NOT sort arrays)
Exception: if semantics require sorting, DOCUMENT it

CORRECT:  [3, 1, 2]  (if generated in this order)
WRONG:    [1, 2, 3]  (sorted when not semantically required)
```

### Rule 6: Whitespace
```
NO trailing whitespace
NO extra spaces around colons
NO newlines inside objects

CORRECT: {"key":"value","arr":[1,2,3]}
WRONG:   {"key" : "value" , "arr" : [ 1 , 2 , 3 ]}
```

---

## 4.2 Log File Structure

### File 1: logs/metadata.json
```json
{
  "algorithm_params": {
    "arbitration_relevance_tie_threshold": 0.01,
    "arbitration_softmax_temperature": 0.1,
    "arbitration_utility_tie_threshold": 1e-6,
    "confidence_variance_threshold": 0.01,
    "convergence_epsilon": 1e-8,
    "convergence_lookback_k": 10,
    "max_iterations": 50
  },
  "seed": 12345678,
  "system_info": {
    "blas_library": "OpenBLAS-0.3.24",
    "numpy_version": "1.24.3",
    "os": "Linux",
    "python_version": "3.11.7"
  },
  "timestamp_start": "2024-01-15T10:30:45.123456Z",
  "trial_id": 1,
  "workload_class": "A"
}
```

### File 2: logs/iteration_N.jsonl (One per line)
```json
{
  "arbitration_results": [...],
  "commit_hash": {
    "hash_algorithm": "SHA-256",
    "hash_scope": "state_snapshot",
    "state_hash": "a3f4e1b2c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4",
    "state_serialized_size_bytes": 4521
  },
  "conflicts": [...],
  "intents": [...],
  "iteration_id": 5,
  "rng_state": {
    "branch_positions": {
      "collision_generation": 342,
      "reward_stochasticity": 0,
      "tie_breaking": 11,
      "tool_sampling": 128
    }
  },
  "state_snapshot": {...},
  "timestamp": "2024-01-15T10:30:46.234567Z",
  "tool_calls": [...],
  "wall_time_ms": 123
}
```

### File 3: logs/rng_audit.jsonl (One per line)
```json
{
  "branch_id": 1,
  "branch_name": "collision_generation",
  "call_sequence": 342,
  "context": {
    "agent_id": "A1",
    "node_id": 3,
    "operation": "generate_intent_collision"
  },
  "iteration": 5,
  "rng_algorithm": "PCG64",
  "rng_call_id": 342,
  "seed_used": 12345678,
  "timestamp": 1.2348,
  "value_format": "float64",
  "value_generated": 0.6234567890123456
}
```

### File 4: logs/tool_calls.jsonl (One per line)
```json
{
  "agent_id": "A1",
  "cost": 0.0375,
  "decision": "ACCEPTED",
  "decision_timestamp": 1.2348,
  "eig": 0.45,
  "eig_to_cost_ratio": 12.0,
  "execution_model": "deterministic_stub",
  "invocation_order": 1,
  "iteration": 5,
  "parameters": {
    "node_id": 3,
    "proposal_value": 42.5
  },
  "resource_id": "node_3",
  "result": {
    "expected_reward": 18.5,
    "relevance_score": 0.75,
    "success_probability": 0.68
  },
  "status": "SUCCESS",
  "threshold": 1.0,
  "tool_call_id": "TC_5_0",
  "tool_call_sequence_id": 42,
  "tool_name": "evaluate_proposal"
}
```

---

## 4.3 State Hash Computation

```python
import hashlib
import json

def compute_state_hash(state_snapshot):
    """
    Compute deterministic SHA-256 of state
    """
    # Serialize with canonical field ordering
    canonical_json = json.dumps(
        state_snapshot,
        sort_keys=True,           # Alphabetical ordering
        separators=(',', ':'),    # No spaces
        ensure_ascii=True         # No unicode escapes
    )
    
    # Encode to UTF-8
    state_bytes = canonical_json.encode('utf-8')
    
    # Compute SHA-256
    state_hash = hashlib.sha256(state_bytes).hexdigest()
    
    return state_hash, len(state_bytes)

# Usage:
hash_result, size = compute_state_hash(iteration_state)
log_entry = {
    "iteration": N,
    "state_hash": hash_result,
    "state_serialized_size_bytes": size
}
```

---

## 4.4 Protocol Enforcement Rules

### Rule 1: No Mutation Without Commit

```
State mutation = any change to agents, frontier, or decisions

Check procedure:
  1. Identify all mutations in iteration N
  2. Verify state_hash is recomputed AFTER mutation
  3. Previous hash ≠ current hash (if mutation occurred)
  4. If mutation found without hash: FLAG violation
```

**Example (CORRECT):**
```
Iteration N:
  - Agent updates confidence
  - State mutated: O_N ≠ O_{N-1}
  - Recompute hash: hash_N = SHA256(canonical_json(O_N))
  - Store: log_entry["state_hash"] = hash_N
```

### Rule 2: No Unregistered Tool Calls

```
Tool call is "registered" if in tool_calls.jsonl

Check procedure:
  1. For each tool result in arbitration_results
  2. Find corresponding tool_call_id in tool_calls
  3. If no match: FLAG "Unregistered Tool Call"
```

### Rule 3: No Frontier Violations

```
Frontier violation = dominated solution in frontier_set

Check procedure:
  1. For each solution S in frontier
  2. Verify: no other solution T dominates S
  3. Dominance: T.A ≥ S.A AND T.C ≤ S.C AND T.L ≤ S.L AND T.R ≥ S.R (strict)
  4. If dominated solution found: FLAG violation
```

---

## 4.5 Verification Checklist

```
□ All JSON files canonicalized (fields sorted)
□ All floats use %.17g format
□ All state_hash values are SHA-256 hex (lowercase, 64 chars)
□ RNG call_sequence monotonically increasing per branch
□ No gaps in RNG call_sequence
□ Convergence condition recorded correctly
□ Arbitration decisions fully logged
□ Tool call costs match tool model
□ No protocol violations (3 rules)
□ Final frontier set is non-dominated (Class D)
```

---

**Section Status:** ✅ COMPLETE  
**Next:** [Section 5: Statistical Verification](STATISTICS.md)
