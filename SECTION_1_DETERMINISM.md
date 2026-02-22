SECTION 1: DETERMINISM & REPRODUCIBILITY (REVISED)

1.1 Determinism Contract (Binding)

All benchmark execution MUST comply with the following constraints:

1.1.1 LLM Execution Model

  a) Temperature & Sampling Strategy
     - All LLM calls performing arbitration MUST use temperature = 0.0
     - Decoding strategy: Greedy (select argmax token)
     - NO nucleus sampling, beam search, or sampling
     
  b) LLM Call Isolation
     - Each decision point (arbitration, convergence check) = one LLM call
     - Prompt deterministically formatted
     
  c) Non-LLM Arbitration (MANDATORY for Verification)
     - Peer verification MUST use deterministic code (Python/Go/Rust), not LLM
     - Arbitration function: arbitrate(intent_A, intent_B, seed) -> winner ∈ {A, B}

1.1.2 Numerical Precision Specification

  a) Floating-Point Standard
     - All accumulations: IEEE 754 double precision (64-bit)
     - NO upconversion to long double
     - Vector operations: BLAS reference implementation (MKL or OpenBLAS, pinned version)
     
  b) Numerical Tolerance Budget
     - Per-iteration accumulation drift: ≤ 1e-10 (absolute)
     - Cumulative drift over K iterations: ≤ sqrt(K) × 1e-10
     - Convergence epsilon: max(1e-8, 0.01 * initial_delta)
     - Verification allows ± 2× tolerance for peer reconstruction
     
  c) Rounding Mode
     - All systems: IEEE 754 round-to-nearest-even (banker's rounding)
     - NO truncation or round-toward-zero

1.1.3 Seed & Entropy Specification

  a) RNG Seeding
     - Primary seed: 64-bit unsigned integer (specified per workload)
     - RNG algorithm: PCG64 (permuted congruential generator)
       * Reference: https://www.pcg-random.org/ v0.98
     - Initialization: PCG64(seed_value).initialize(workload_class, trial_number)
     
  b) Entropy Allocation
     - Intent collision generation: RNG branch 1
     - Tool call cost sampling: RNG branch 2
     - Reward stochasticity (Class C): RNG branch 3
     - Tie-breaking (arbitration): RNG branch 4
     - Each branch: distinct RNG state (advanced by explicit seek)
     
  c) Randomness Logging
     - EVERY RNG call MUST be logged: {branch_id, call_seq, value_generated}
     - Call sequence: strictly monotonic per branch
     - Format (JSON): {"rng_branch": 1, "call_seq": 42, "value": 0.6234, "timestamp": 1.2345}

1.1.4 Execution Parallelism Prohibition

  a) Single-Threaded Mandate
     - All benchmark execution MUST run on single CPU core
     - NO concurrent agent execution
     - NO async/await in control flow
     - Iteration N must COMPLETE before iteration N+1 starts
     
  b) Tool Call Sequencing
     - Tool calls in iteration must execute in deterministic order
     - Order: by (agent_id ASC, intent_timestamp ASC)
     - Tool response times MUST be stubbed (not actually called to external service)
     
  c) Timing Guarantee
     - Iteration execution time variance ≤ 5% across runs
     - If variance exceeds 5%, system is non-deterministic (FAIL)

1.1.5 State Serialization & Commit Hash

  a) Serialization Canonicalization
     - Format: JSON (UTF-8 encoding, no BOM)
     - Field order: sorted alphabetically by key name (keys are case-sensitive)
     - Float serialization: %.17g format (17 significant digits)
     - Array order: as generated (NOT sorted unless semantically required)
     
  b) Commit Hash Computation
     - Canonical JSON string = serialize_canonical(state_snapshot)
     - Hash = SHA-256(canonical_json_string)
     - Store hash in log: {"iteration": N, "state_hash": "abc123...", "state_size_bytes": 4521}

1.2 Verification Protocol for Determinism

1.2.1 Pre-Execution Validation
  
  a) Artifact Inventory
     - Primary system must provide: workload definition, RNG seed sequence, tool stubs, expected output log
     
  b) Environment Matching
     - Peer must verify CPU architecture (x86-64, ARM)
     - OS: Linux (determinism hardest on Linux)
     - BLAS library: same version as primary
     - Python/Go/Rust version: within 1 minor version

1.2.2 Checkpoint Verification (Every 10 Iterations)
  
  - Peer executes iterations [0, 10), recomputes state_hash at iteration 9
  - Compare: peer_hash[9] vs. primary_hash[9]
  - If hashes differ: binary search the divergence point

1.2.3 Floating-Point Precision Check
  
  - At iteration M (e.g., M=100), compute accumulated drift
  - If drift > tolerance_budget × sqrt(M): FLAG "Numerical Precision Budget Exceeded"

1.2.4 Randomness Audit
  
  - Peer logs all RNG calls (branch_id, call_seq, value)
  - Compare RNG log with primary's RNG log
  - If divergence found: identify branch and call_seq where they split
