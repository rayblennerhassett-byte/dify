SECTION 2: WORKLOAD CLASS DEFINITIONS (REVISED)

CLASS A: DETERMINISTIC GRAPH ORCHESTRATION
─────────────────────────────────────────────────────────────────────────

2.1 Graph Structure Definition

  a) Node Graph
     - Nodes: 25 (numbered 0–24)
     - Topology: Layered DAG with 5 layers
       * Layer 0 (sources): nodes {0, 1, 2} — no dependencies
       * Layer 1: nodes {3, 4, 5, 6, 7}
       * Layer 2: nodes {8, 9, 10, 11, 12}
       * Layer 3: nodes {13, 14, 15, 16, 17}
       * Layer 4 (sinks): nodes {18, 19, 20, 21, 22, 23, 24}
     
     - Edges: DAG with fixed edge set (deterministic)
       * Each node in layer K connects to 2 random nodes in layer K+1
       * Randomness: seeded with seed=0xDEADBEEF for graph generation only
     
  b) Node Semantics
     - Each node represents a decision task
     - Node value = deterministic function of input edges
     - Aggregation: sum(incoming_edges) + base_reward
     - No stochasticity: same inputs always produce same outputs

  c) Execution Semantics
     - Scheduling: topological sort (layer-by-layer execution)
     - No agent choice in execution order (deterministic)
     - Tool calls: DISABLED (no tool invocations)

2.2 Agent Configuration

  a) Agent Count: 3 agents {A1, A2, A3}
  
  b) Agent Roles (static assignment)
     - A1: Proposes layers 0–1 (source optimization)
     - A2: Proposes layers 2–3 (middle orchestration)
     - A3: Proposes layers 4 (sink aggregation)
     
  c) Intent Generation (per iteration)
     - Each agent i proposes an intent: reorder its assigned layer by some heuristic
     - Intent = (agent_id, layer_id, proposed_ordering)
     - Heuristic: maximize sum of edge rewards in proposed order
     - Heuristic is deterministic given iteration number
     
  d) Conflict Avoidance
     - Intents do NOT conflict (by design)
     - Each agent proposes for disjoint layer sets
     - Arbitration always selects: first agent proposal (A1 > A2 > A3 priority)
     - VERIFICATION: Arbitration conflict rate must be 0.0

2.3 Convergence Criteria

  a) Frontier State
     - Frontier = set of all proposed orderings across all iterations
     - Frontier size grows monotonically
     - Initial frontier: layer orderings [identity for each layer]
     
  b) Convergence Condition (MUST use BOTH criteria)
     - Criterion 1: No new orderings proposed in last 10 iterations
     - Criterion 2: All layer orderings have been tried (exhaustion condition)
     - Convergence triggered when BOTH are true
     
  c) Maximum Iterations: 50

CLASS B: HIGH-CONFLICT ARBITRATION
─────────────────────────────────────────────────────────────────────────

2.5 Conflict-Heavy Environment

  a) Graph Structure
     - Nodes: 40 (fully connected resource allocation problem)
     - No layer structure (unlike Class A)
     - Each node represents a resource allocation decision
     
  b) Agent Configuration
     - Agent count: 10 agents {A1, A2, ..., A10}
     - All agents can propose for ANY node (resource overlap)
     
  c) Intent Generation (per iteration)
     - Each agent i generates 2 intents (higher density)
     - Intent: (agent_id, node_id, proposed_value ∈ [0, 100])
     - Intent i = (A_j, node_k, value)
     - Intents sampled deterministically:
       * value = (seed + iteration*10 + agent_j*5 + node_k*3) mod 100

  d) Tool Calls (Enabled for Class B)
     - Tool: "evaluate_proposal"
       * Input: proposal value
       * Cost: 0.01 + 0.05 × (100 - value) / 100
       * Output: relevance_score ∈ [0.0, 1.0] (deterministic)
       * relevance_score = 0.5 + 0.5 × (value / 100)

CLASS C: HIGH-UNCERTAINTY MONTE CARLO SAMPLING
─────────────────────────────────────────────────────────────────────────

2.10 Stochastic Reward Environment

  a) Problem Setup
     - Nodes: 30 decision nodes
     - Each node has uncertain reward distribution (Monte Carlo sampling)
     - Agents must estimate expected values under uncertainty
     
  b) Reward Model
     - True reward for node i: R_i ~ Normal(μ_i, σ_i)
     - Parameters (μ_i, σ_i): fixed per workload
     - Node rewards are FIXED (same across all trials)
     - But samples are different each time (deterministic via seed)
     
  c) Monte Carlo Sampling
     - Samples per node per iteration: 10,000
     - RNG: PCG64 seeded with (workload_seed, iteration, node_id)
     - Sample generation: inverse transform on Normal(0,1) using Box-Muller
     - Each iteration: re-sample (fresh Monte Carlo ensemble)

CLASS D: MULTI-OBJECTIVE PARETO FRONTIER OPTIMIZATION
─────────────────────────────────────────────────────────────────────────

2.14 Multi-Objective Problem Setup

  a) Objectives
     - Accuracy: A ∈ [0, 1] (higher is better)
     - Cost: C ∈ [1, 100] (lower is better)
     - Latency: L ∈ [0.1, 10.0] seconds (lower is better)
     - Robustness: R ∈ [0, 1] (higher is better)
     
  b) Objective Space
     - Solution: vector (A, C, L, R)
     - Valid solutions: pre-generated set of 50 candidate solutions

  c) Agent Role
     - Agents: 3, 5, 10 (depending on test variant)
     - Each agent proposes a competing solution vector

2.15 Pareto Dominance and Frontier

  a) Dominance Definition
     - Solution X dominates Y if:
       * X.A ≥ Y.A (accuracy at least as good)
       * X.C ≤ Y.C (cost at most as bad)
       * X.L ≤ Y.L (latency at most as bad)
       * X.R ≥ Y.R (robustness at least as good)
       * AND at least one inequality is strict
     
  b) Frontier (Pareto Set)
     - Non-dominated set: solutions not dominated by any other
     - Frontier = {X : ¬∃Y s.t. Y dominates X}
     - Frontier is deterministic given solution set
