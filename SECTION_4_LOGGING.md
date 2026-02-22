SECTION 4: LOGGING SCHEMA & CANONICALIZATION (REVISED)

5.0 LOGGING OVERVIEW
───────────────────────────────────────────────────────────────────────────

  All benchmark execution must emit deterministic, verifiable logs.
  Logs enable peer verification and protocol compliance checking.
  Format: newline-delimited JSON (JSONL)
  
  File structure:
    logs/iteration_N.jsonl        (one file per iteration)
    logs/metadata.json            (global metadata)
    logs/rng_audit.jsonl          (all RNG calls)
    logs/tool_calls.jsonl         (all tool invocations)

5.1 METADATA LOG (logs/metadata.json)

  {
    "workload_class": "A",
    "trial_id": 1,
    "seed": 12345678,
    "timestamp_start": "2024-01-15T10:30:45.123456Z",
    "system_info": {
      "os": "Linux",
      "python_version": "3.11.7",
      "numpy_version": "1.24.3",
      "blas_library": "OpenBLAS-0.3.24"
    },
    "algorithm_params": {
      "max_iterations": 50,
      "convergence_epsilon": 1e-8,
      "convergence_lookback_k": 10,
      "confidence_variance_threshold": 0.01,
      "arbitration_relevance_tie_threshold": 0.01,
      "arbitration_utility_tie_threshold": 1e-6,
      "arbitration_softmax_temperature": 0.1
    }
  }

5.2 ITERATION STATE LOG (logs/iteration_N.jsonl)

  Each iteration emits ONE JSON object (one per line):
  
  {
    "iteration_id": 5,
    "timestamp": "2024-01-15T10:30:46.234567Z",
    "wall_time_ms": 123,
    
    "intents": [...],
    "conflicts": [...],
    "arbitration_results": [...],
    "tool_calls": [...],
    
    "state_snapshot": {
      "agents": {...},
      "frontier": {...},
      "convergence_check": {...}
    },
    
    "commit_hash": {
      "state_hash": "a3f4e1b2c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4",
      "hash_algorithm": "SHA-256",
      "state_serialized_size_bytes": 4521,
      "hash_scope": "state_snapshot"
    },
    
    "rng_state": {
      "branch_positions": {
        "collision_generation": 342,
        "tool_sampling": 128,
        "reward_stochasticity": 0,
        "tie_breaking": 11
      }
    }
  }

5.3 RNG AUDIT LOG (logs/rng_audit.jsonl)

  Every RNG call is logged for reproducibility verification:
  
  {
    "rng_call_id": 342,
    "branch_id": 1,
    "branch_name": "collision_generation",
    "call_sequence": 342,
    "iteration": 5,
    "timestamp": 1.2348,
    "value_generated": 0.6234567890123456,
    "value_format": "float64",
    "rng_algorithm": "PCG64",
    "seed_used": 12345678,
    "context": {...}
  }

5.4 TOOL CALLS LOG (logs/tool_calls.jsonl)

  Detailed tool call trace:
  
  {
    "tool_call_sequence_id": 42,
    "tool_call_id": "TC_5_0",
    "iteration": 5,
    "tool_name": "evaluate_proposal",
    "invocation_order": 1,
    "agent_id": "A1",
    "resource_id": "node_3",
    "parameters": {...},
    "execution_model": "deterministic_stub",
    "cost": 0.0375,
    "eig": 0.45,
    "eig_to_cost_ratio": 12.0,
    "threshold": 1.0,
    "decision": "ACCEPTED",
    "result": {...},
    "status": "SUCCESS"
  }

5.5 CANONICALIZATION RULES (MANDATORY)

  RULE 1: JSON FIELD ORDERING
    - All JSON objects MUST have fields in sorted alphabetical order
    - Sorting is case-sensitive
    
  RULE 2: FLOAT SERIALIZATION
    - Format: %.17g (17 significant decimal digits)
    - Use lowercase 'e' for scientific notation
    
  RULE 3: INTEGER SERIALIZATION
    - No decimal point (1, not 1.0)
    - No leading zeros (42, not 042)
  
  RULE 4: BOOLEAN & NULL
    - Booleans: lowercase (true, false)
    - Null: null (lowercase)
  
  RULE 5: ARRAY ORDERING
    - Arrays preserve generation order (NOT sorted)
    - Exception: if semantics require sorting, DOCUMENT this
  
  RULE 6: STRING ESCAPING
    - UTF-8 encoding, no BOM
    - Escape control characters: \n, \t, \r, etc.
    
  RULE 7: WHITESPACE
    - NO trailing whitespace
    - NO extra spaces around colons

5.6 STATE HASH COMPUTATION (MANDATORY)

  ALGORITHM:
  
    1. Extract state_snapshot from iteration log
    2. Canonicalize JSON: sort fields, apply Rules 1-7
    3. Serialize to string: canonical_json = JSON.stringify(state, sorted=True)
    4. Compute hash: hash = SHA256(canonical_json.encode('utf-8'))
    5. Store as hex string (lowercase)

5.7 PROTOCOL ENFORCEMENT (MANDATORY CHECKS)

  RULE 1: NO MUTATION WITHOUT COMMIT
    - State mutation = any change to agents, frontier, or decisions
    - Each mutation must precede commit_hash computation
    - State_hash must be recomputed AFTER mutation
  
  RULE 2: NO UNREGISTERED TOOL CALLS
    - Tool call is "registered" if it appears in tool_calls log
    - Any tool result mentioned in arbitration_results
      must have corresponding tool_call_id in tool_calls
  
  RULE 3: NO FRONTIER VIOLATIONS
    - Frontier violation = dominated solution in frontier_set
    - For each solution in frontier: verify it is NOT dominated by any other

5.8 LOG VERIFICATION CHECKLIST (FOR PEER AUDITOR)

  □ logs/metadata.json exists and is well-formed
  □ logs/iteration_*.jsonl files for all iterations (0 to N_converged)
  □ logs/rng_audit.jsonl exists and has continuous call_sequence
  □ logs/tool_calls.jsonl exists (if tools enabled for workload class)
  
  □ All JSON files canonicalized (fields sorted alphabetically)
  □ All floats use %.17g format
  □ All state_hash values are SHA-256 hex strings (lowercase, 64 chars)
  
  □ RNG call_sequence is monotonically increasing per branch
  □ No gaps in RNG call_sequence
  
  □ Convergence condition recorded correctly
  □ Arbitration decisions fully logged
  □ Tool call costs and EIG values match tool model
  
  □ No protocol violations detected
  □ Final frontier set is non-dominated
