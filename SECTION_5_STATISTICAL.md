SECTION 5: STATISTICAL VERIFICATION & ACCEPTANCE CRITERIA (REVISED)

6.0 STATISTICAL FRAMEWORK
───────────────────────────────────────────────────────────────────────────

  Objective: Verify peer outputs are statistically equivalent to primary
  
  Design: Multiple comparison framework with family-wise error control
  
  Significance level (family-wise): α_family = 0.05
  Correction method: Bonferroni

6.1 SAMPLE SIZE & TRIAL PROTOCOL

  6.1.1 Trial Count
    
    Minimum trials: 30 per workload class per variant
    
    Variants:
      Class A: 1 variant (fixed 25 nodes, 3 agents)
      Class B: 3 variants (N ∈ {3, 10, 25} agents)
      Class C: 4 variants (S ∈ {100, 1000, 10000, 100000} Monte Carlo samples)
      Class D: 3 variants (A ∈ {3, 5, 10} agents)
    
    Total trials per peer verification:
      30 trials × (1 + 3 + 4 + 3) = 30 × 11 = 330 trials minimum
  
  6.1.2 Randomness Across Trials
    
    Trial t uses seed_base + t (deterministic variation)
    Seeds are disjoint between primary and peer

6.2 METRIC COLLECTION (PER TRIAL)

  For each trial, record:
    - Convergence iteration count (iter_conv)
    - Final frontier size (frontier_size)
    - Total arbitration conflicts encountered (n_conflicts)
    - Conflict resolution rate
    - Final hypervolume (Class D only)
    - Brier score (Classes B, C only)
    - EIG efficiency (Classes B, C only)
    - Tail risk Q95 (Class C only)
    - Total wall-clock time (ms)
    - RNG entropy verification (no divergence boolean)

6.3 DESCRIPTIVE STATISTICS (ACROSS 30 TRIALS)

  For each metric M:
    
    Primary distribution:
      mean_primary = (1/30) Σ M_primary[t]
      std_primary = sqrt((1/29) Σ (M_primary[t] - mean_primary)^2)
      median_primary = percentile(M_primary, 0.5)
      Q1 = percentile(M_primary, 0.25)
      Q3 = percentile(M_primary, 0.75)
      IQR = Q3 - Q1
    
    Peer distribution: (same calculations)

6.4 STATISTICAL HYPOTHESIS TESTS (WITH CORRECTIONS)

  6.4.1 Number of Comparisons & Family-Wise Error Rate
    
    Tests per workload class:
      Class A: 3 metrics → 3 tests
      Class B: 6 metrics × 3 variants → 18 tests
      Class C: 7 metrics × 4 variants → 28 tests
      Class D: 5 metrics × 3 variants → 15 tests
      
      Total: 64 statistical tests
    
    Family-wise significance level: α_family = 0.05
    
    Bonferroni correction: α_individual = 0.05 / 64 = 0.00078

  6.4.2 Assumption Checking (PRE-TEST)
    
    For each metric distribution:
      
      a) NORMALITY TEST (Shapiro-Wilk)
         p-value > 0.05: assume normal
         p-value ≤ 0.05: use non-parametric test
      
      b) EQUAL VARIANCE TEST (Levene)
         p-value > 0.05: assume equal variances (use standard t-test)
         p-value ≤ 0.05: variances unequal (use Welch t-test)

  6.4.3 PRIMARY TEST: TWO-SAMPLE t-TEST (or equivalent)
    
    If both metrics are normally distributed AND variances equal:
      Test: Welch's t-test
      H0: mean_primary == mean_peer
      H1: mean_primary ≠ mean_peer
      
      Test statistic: t = (mean_primary - mean_peer) / SE_diff
      where SE_diff = sqrt(std_primary^2/n + std_peer^2/n)
      
      p-value: two-tailed P(|T| > |t|) where T ~ t(df)
    
    If NOT both normal OR variances significantly unequal:
      Test: Mann-Whitney U (non-parametric)

  6.4.4 SECONDARY TEST: EFFECT SIZE
    
    Effect size (Cohen's d):
      d = (mean_primary - mean_peer) / pooled_std
      
      Interpretation:
        |d| < 0.2: trivial effect (pass)
        0.2 ≤ |d| < 0.5: small effect (pass with caution)
        0.5 ≤ |d| < 0.8: medium effect (fail)
        |d| ≥ 0.8: large effect (fail)
      
      Threshold: |d| < 0.2 required for acceptance

  6.4.5 TEST DECISION RULE
    
    A metric PASSES if:
      (p-value > α_individual) AND (|effect_size| < 0.2)
    
    A metric FAILS if:
      (p-value ≤ α_individual) OR (|effect_size| ≥ 0.2)

6.6 COMPOSITE PERFORMANCE INDEX (CPI)

  6.6.1 Normalization Strategy
    
    For each metric M across all trials (both primary and peer):
      
      a) POOLED STATISTICS (compute on combined data)
         pool_mean_M = mean of M across all trials (primary + peer)
         pool_std_M = std of M across all trials
      
      b) Z-SCORE NORMALIZATION (robust method)
         For metric value m:
           m_norm = (m - pool_mean_M) / pool_std_M
           Range: typically [-3, +3]

  6.6.2 CPI Formula (REVISED)
    
    PI = w_1 × (1 / iter_norm)
       + w_2 × calibration_norm
       + w_3 × hypervolume_norm
       - w_4 × latency_norm
       - w_5 × conflict_norm
    
    where:
      Weights (fixed):
        w_1 = 0.25 (convergence speed)
        w_2 = 0.20 (calibration accuracy)
        w_3 = 0.25 (frontier quality)
        w_4 = 0.15 (execution latency)
        w_5 = 0.15 (conflict frequency)
        Sum(w_i) = 1.0

  6.6.3 CPI Comparison Protocol
    
    a) Primary computes: CPI_primary
       Peer computes: CPI_peer
    
    b) Compute CPI deviation:
       Δ_CPI = |CPI_primary - CPI_peer| / |CPI_primary|
    
    c) Acceptance threshold: Δ_CPI ≤ 0.05 (5%)

6.8 FAILURE DETECTION CRITERIA (UPDATED)

  Peer MUST flag and FAIL verification if any of the following occur:

  a) INFINITE LOOP: iterations exceed max_iterations + 10%
  b) ARBITRATION DEADLOCK: same conflict decision reversed 3+ times
  c) CONFIDENCE COLLAPSE: sum(confidence_weights) < 0.1
  d) FRONTIER EXPLOSION: frontier_size > 2 × expected_size
  e) TOOL FLOODING: tool_calls_per_iteration > threshold
  f) STATE HASH DIVERGENCE: state_hash_peer ≠ state_hash_primary
  g) RNG DIVERGENCE: RNG log diverges between primary and peer
  h) NUMERICAL PRECISION VIOLATION: accumulated drift > tolerance_budget
  i) STATISTICAL TEST FAILURE: metric fails t-test or effect size
  j) PROTOCOL VIOLATION: mutation without commit, unregistered tool call, frontier violation

6.9 ACCEPTANCE CRITERIA (REVISED)

  Stage 5 verification is ACCEPTED if and only if ALL of the following hold:

  ✓ All workload classes (A, B, C, D) pass their respective test suites
  
  ✓ No failure detection criteria triggered
  
  ✓ All individual metric t-tests pass:
    - p-value > Bonferroni-corrected α
    - Effect size |d| < threshold (class-dependent)
  
  ✓ Composite Performance Index deviation ≤ 5%
  
  ✓ Arbitration determinism confirmed:
    - 100% winner agreement
    - Relevance and utility scores match within tolerance
  
  ✓ Convergence stability:
    - Primary and peer converge at same or adjacent iteration
    - Frontier sets match
  
  ✓ Logging completeness:
    - All iterations logged, no gaps
    - RNG audit trail complete
    - Tool calls documented
  
  ✓ No unresolved outliers or anomalies

  Verification status: PASS
  
  If ANY criterion fails: Verification status: FAIL
