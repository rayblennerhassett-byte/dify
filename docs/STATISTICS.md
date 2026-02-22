# 5. Statistical Verification Protocol

**Status:** ✅ Fully Specified  
**Section ID:** S5  
**Trials:** 330 minimum (30 per variant × 11 variants)  
**Tests:** 64 hypothesis tests  
**Correction:** Bonferroni (α = 0.05 / 64 = 0.00078)

---

## 5.1 Trial Protocol

### Samples & Variants

```
Class A: 1 variant × 30 trials =  30 trials
Class B: 3 variants × 30 trials = 90 trials
Class C: 4 variants × 30 trials = 120 trials
Class D: 3 variants × 30 trials = 90 trials
─────────────────────────────────────
Total:  11 variants × 30 trials = 330 trials
```

**Variants:**
- **Class B:** Agents ∈ {3, 10, 25}
- **Class C:** Samples ∈ {100, 1000, 10000, 100000}
- **Class D:** Agents ∈ {3, 5, 10}

### Randomness Across Trials

```
Primary seeds: {base_seed+0, base_seed+1, ..., base_seed+29}
Peer seeds:    {base_seed+1000, base_seed+1001, ..., base_seed+1029}

Rationale: Different sequences but both deterministic
```

---

## 5.2 Metrics Collected Per Trial

```
For each trial:
  - iter_conv           (convergence iteration count)
  - frontier_size       (final frontier size)
  - n_conflicts         (total arbitration conflicts)
  - conflict_resolution_rate
  - hypervolume         (Class D only)
  - brier_score         (Classes B, C only)
  - eig_efficiency      (Classes B, C only)
  - tail_risk_q95       (Class C only)
  - wall_time_ms        (execution time)
  - rng_divergence      (boolean: no divergence?)
```

---

## 5.3 Hypothesis Tests (64 Total)

### Tests per Workload

```
Class A: 3 metrics × 1 variant =  3 tests
Class B: 6 metrics × 3 variants = 18 tests
Class C: 7 metrics × 4 variants = 28 tests
Class D: 5 metrics × 3 variants = 15 tests
────────────────────────────────────────
Total:                             64 tests
```

### Bonferroni Correction

```
Family-wise α: 0.05 (Type I error rate across all tests)
Individual α:  0.05 / 64 = 0.00078

Each test must have p > 0.00078 to pass
```

### Two-Sample Tests (Welch's t-test)

```python
from scipy import stats

def test_metric_equivalence(primary_values, peer_values):
    """
    Welch's t-test (robust to unequal variances)
    """
    # Pre-tests
    _, p_normality_primary = stats.shapiro(primary_values)
    _, p_normality_peer = stats.shapiro(peer_values)
    
    _, p_levene = stats.levene(primary_values, peer_values)
    
    # Main test (Welch's t-test, always robust)
    t_stat, p_value = stats.ttest_ind(primary_values, peer_values, equal_var=False)
    
    # Effect size (Cohen's d)
    n1, n2 = len(primary_values), len(peer_values)
    var1, var2 = np.var(primary_values, ddof=1), np.var(peer_values, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    cohens_d = (np.mean(primary_values) - np.mean(peer_values)) / pooled_std
    
    # Decision
    alpha_individual = 0.00078
    passes_p = p_value > alpha_individual
    passes_d = abs(cohens_d) < 0.2
    passes_test = passes_p and passes_d
    
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "cohens_d": cohens_d,
        "passes_p_threshold": passes_p,
        "passes_effect_size_threshold": passes_d,
        "overall_result": "PASS" if passes_test else "FAIL"
    }
```

---

## 5.4 Effect Size (Cohen's d)

```
d = (mean_primary - mean_peer) / pooled_std

Interpretation:
  |d| < 0.2:   Trivial effect (PASS)
  0.2 ≤ |d| < 0.5: Small effect (caution)
  0.5 ≤ |d| < 0.8: Medium effect (FAIL)
  |d| ≥ 0.8:   Large effect (FAIL)

Threshold for acceptance: |d| < 0.2
```

---

## 5.5 Workload-Specific Tests

### Class A Tests

```
Test 1: Convergence Iterations
  Requirement: primary_iter == peer_iter (exact match, no tolerance)
  Method: Compare iteration count
  Pass: If match

Test 2: Conflict Rate
  Requirement: rate ≤ 0.001
  Method: Welch's t-test
  Pass: If p > 0.00078 AND |d| < 0.2

Test 3: Frontier Match
  Requirement: F_primary == F_peer (exact set equality)
  Method: Set comparison
  Pass: If sets identical
```

### Class B Tests

```
Test 1: Arbitration Winner
  Requirement: 100% winner agreement
  Method: Count disagreements
  Pass: If disagreements = 0

Test 2–4: Deadlock, Rollback, Conflict Rate (t-tests)
Test 5–6: Cost & EIG tests (t-tests)
```

### Class C Tests

```
Test 1: Expected Value Equivalence
  Requirement: |E_peer - E_primary| / E_primary ≤ 2%
  Method: Paired t-test
  Pass: If p > 0.00078 AND |d| < 0.2

Test 2: Tail Risk
  Requirement: |Q95_peer - Q95_primary| / Q95 ≤ 5%

Test 3: Scaling (log-log regression)
  Requirement: R² ≥ 0.85
  Method: Fit convergence ~ 1/sqrt(samples)

Tests 4–7: Other metrics
```

### Class D Tests

```
Test 1: Frontier Match
  Requirement: F_primary == F_peer
  Method: Set comparison

Test 2: Hypervolume
  Requirement: |HV_peer - HV_primary| / HV_primary ≤ 3%
  Method: t-test

Test 3: Dominated Count
  Requirement: 0 dominated solutions

Tests 4–5: Other metrics
```

---

## 5.6 Composite Performance Index (CPI)

```
CPI = 0.25 × (1/iter_norm)
    + 0.20 × calibration_norm
    + 0.25 × hypervolume_norm
    - 0.15 × latency_norm
    - 0.15 × conflict_norm

where:
  X_norm = (X - pool_mean) / pool_std  [z-score across all trials]
```

**Verification:**
```
Δ_CPI = |CPI_primary - CPI_peer| / |CPI_primary|
Tolerance: Δ_CPI ≤ 5%
```

---

## 5.7 Failure Detection Criteria (10 Total)

```
1. Infinite Loop:      iterations > max_iterations + 10%
2. Deadlock:           same conflict reversed 3+ times consecutively
3. Confidence Collapse: sum(weights) < 0.1
4. Frontier Explosion:  size > 2× expected
5. Tool Flooding:       calls/iteration > threshold
6. State Hash Divergence: peer_hash ≠ primary_hash
7. RNG Divergence:     RNG log mismatch
8. Numerical Violation: drift > tolerance_budget
9. Statistical Failure: p ≤ α_individual OR |d| ≥ 0.2
10. Protocol Violation: unlogged mutation, unregistered tool, frontier violation
```

**Any failure → verification FAILS**

---

## 5.8 Acceptance Criteria

### All-or-Nothing Verification

```
✓ All workload classes (A, B, C, D) pass
✓ All individual metric tests pass (p > 0.00078, |d| < 0.2)
✓ Composite Performance Index deviation ≤ 5%
✓ No failure detection criteria triggered
✓ Arbitration 100% deterministic
✓ Convergence iterations match (±0)
✓ Protocol rules enforced (3 checks)

Result: PASS or FAIL (no partial credit)
```

---

**Section Status:** ✅ COMPLETE  
**Next:** [Section 6: Verification & Certification](VERIFICATION.md)
