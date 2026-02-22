SECTION 3: METRIC DEFINITIONS (REVISED)

4.0 NOTATION AND CONVENTIONS

  Symbol             Definition
  ─────────────────────────────────────────────────────────
  ||v||_p            Lp-norm: (Σ|v_i|^p)^(1/p)
  ||v||_2            Euclidean norm (default)
  ||v||_∞            Chebyshev norm: max(|v_i|)
  ℝ^n                n-dimensional Euclidean space
  arg max            Argmax (if tie, use tie-breaking rule)
  ≈_ε                Approximate equality within tolerance ε
  δ(·)               Kronecker delta (1 if true, 0 if false)

4.1 CONVERGENCE METRIC (REVISED)

  4.1.1 Output Space Definition
    - Output vector O_t ∈ ℝ^k where k = dimension of frontier space
    - For Class A: k = number of proposed orderings (grows over time)
    - For Class B: k = 40 (one allocation value per node)
    - For Class C: k = 30 (one expected value per node)
    - For Class D: k = 4 (Pareto frontier size in objectives)
  
  4.1.2 Delta (Change) Metric
    
    DEFINITION:
      Δ_t = ||O_t - O_{t-1}||_2
    
    where ||·||_2 is the Euclidean norm (MANDATORY).
    
    For varying-dimension outputs (e.g., frontier grows):
      - Pad O_{t-1} with zeros to match dimension of O_t
  
  4.1.3 Convergence Condition (MANDATORY: USE ALL THREE)
    
    CONVERGED if ALL of the following are satisfied:
    
    (a) DELTA THRESHOLD:
        Δ_t < ε  for all iterations t ∈ [T-K, T]
        
        where:
          ε = max(1e-8, 0.01 × ||O_0||_2)
          T = current iteration
          K = 10 (lookback window size, FIXED)
    
    (b) FRONTIER IMPROVEMENT STASIS:
        frontier_improvement_{t} = 0  for all t ∈ [T-K, T]
        
        where frontier_improvement_t = 1 if new non-dominated solution added
    
    (c) CONFIDENCE VARIANCE:
        var(confidence_weights_t) < θ
        
        where:
          confidence_weights_t = [w_1, w_2, ..., w_n] (per-agent confidence)
          θ = 0.01 (threshold, FIXED)
          var(w) = (1/n) Σ(w_i - mean(w))^2

4.2 ARBITRATION DETERMINISM METRIC (REVISED)

  4.2.1 Conflict Definition
    
    A CONFLICT is a tuple (intent_A, intent_B, resource_id):
      - intent_A and intent_B both propose for same resource_id
      - intent_A.proposed_value ≠ intent_B.proposed_value
      - Both intents are "active" (not yet discarded by EIG filter)
  
  4.2.2 Relevance Function (MANDATORY DEFINITION)
    
    DEFINITION:
      relevance(intent, node_context) = f(proposal_value, historical_success_rate, agent_authority)
    
    FORMAL COMPUTATION:
      Let:
        v = intent.proposed_value
        α = agent authority score (based on past acceptance count)
        h = historical success rate of this proposal type
        
      relevance(intent) = 0.4 × (v / max_value_range)
                        + 0.3 × α
                        + 0.3 × h
      
      Bounds: relevance(intent) ∈ [0.0, 1.0]
  
  4.2.3 Expected Utility Function
    
    DEFINITION:
      utility(intent) = E[reward | proposal accepted]
                      = P(success | intent) × expected_reward - cost(intent)
    
    FORMAL COMPUTATION:
      Let:
        p_succ = probability of success (from tool evaluation)
        r_exp = expected reward (from proposal definition)
        c = cost (from tool cost model or fixed)
        
      utility(intent) = p_succ × r_exp - c

  4.2.4 Arbitration Decision Rule (MANDATORY THREE-STEP)
    
    GIVEN: conflict pair (intent_A, intent_B) for resource_id R
    
    STEP 1 — RELEVANCE SORTING:
      intents_sorted = sort([intent_A, intent_B], 
                            key=relevance, 
                            descending=True)
      
      If relevance differs by > 0.01:
        WINNER = intents_sorted[0]
        GOTO RETURN
      
      Otherwise (relevance tie):
        GOTO STEP 2
    
    STEP 2 — UTILITY RANKING:
      intents_sorted = sort(intents_sorted, 
                            key=utility, 
                            descending=True)
      
      If utility differs by > 1e-6:
        WINNER = intents_sorted[0]
        GOTO RETURN
      
      Otherwise (utility tie):
        GOTO STEP 3
    
    STEP 3 — SEED-BASED SOFTMAX TIE-BREAKING:
      Define: score(intent) = exp(hash_deterministic(intent, resource_id, seed) / temp)
      where:
        hash_deterministic = SHA-256 of string "{intent_id}|{resource_id}|{seed}"
        converted to [0.0, 1.0] via: int(hash, 16) % 1e6 / 1e6
        temp = 0.1 (temperature for softmax, FIXED)
      
      WINNER = argmax score

4.3 CALIBRATION METRIC (BRIER SCORE) (REVISED)

  4.3.1 Probabilistic Prediction Setup
    - Some agents generate probabilistic predictions
    - Prediction: P(outcome=1) ∈ [0, 1]
    - Ground truth: y ∈ {0, 1}
  
  4.3.2 Brier Score Definition
    
    DEFINITION:
      B = (1/N) Σ_{i=1}^{N} (p_i - y_i)^2
    
    where:
      N = number of predictions
      p_i = predicted probability for outcome i
      y_i = realized outcome (0 or 1)
      B ∈ [0, 1]
    
    Interpretation:
      B = 0: perfect predictions
      B = 0.25: random guessing
      B = 1: worst predictions

4.4 HYPERVOLUME METRIC (REVISED)

  4.4.1 Hypervolume in Multi-Objective Space
    
    DEFINITION:
      Hypervolume = volume of objective space dominated by Pareto frontier
      relative to reference point
    
    For each solution s_i ∈ F:
      Define hyperbox: [s_i.A, A_ref] × [C_ref, s_i.C] × [L_ref, s_i.L] × [s_i.R, R_ref]
    
    Hypervolume = Σ_{i} volume(hyperbox_i)
    
    where:
      volume(box) = (A_ref - s_i.A) × (s_i.C - C_ref) × (s_i.L - L_ref) × (s_i.R - R_ref)

4.5 TOOL EFFICIENCY METRIC (EIG-BASED) (REVISED)

  4.5.1 Expected Information Gain (EIG) Definition
    
    DEFINITION:
      EIG(tool_call) = H(X | prior) - H(X | posterior)
    
    where:
      H(X) = entropy of random variable X
      prior = prior belief distribution
      posterior = posterior belief distribution after tool call
      Units: bits (using log_2)

  4.5.2 Cost Model
    
    DEFINITION:
      cost(tool_call) = base_cost + variable_cost(parameters)
    
    For "evaluate_proposal" tool (Class B):
      cost = 0.01 + 0.05 × (100 - proposal_value) / 100
      range: [0.01, 0.06]

  4.5.3 Tool Call Decision Rule (EIG Threshold)
    
    RULE:
      IF (EIG / cost) > threshold:
        CALL tool
      ELSE:
        USE heuristic (no tool call)
    
    THRESHOLD (fixed): 1.0
