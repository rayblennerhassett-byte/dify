# 🤖 LLM Peer Review Prompts (Copy-Paste Ready)

Ready-to-use prompts for LLM peer review. Copy and paste these into your LLM interface.

---

## PROMPT 1: Initial Specification Compliance Review

```
You are an expert peer reviewer for distributed systems and formal verification.

I am requesting a peer review of MoE Protocol Stage 5 implementation.

TASK: Verify specification compliance

Review the following implementation against the specification and verify:

SPECIFICATION REQUIREMENTS:
1. Phase 1-2 (Determinism):
   - LLM temperature must be 0.0 (greedy decoding only)
   - IEEE 754 double precision enforced
   - PCG64 RNG v0.98 with 4 deterministic branches
   - State SHA-256 hashing with canonical JSON
   - Single-threaded execution only

2. Phase 3 (Workloads):
   - Class A: 25-node 5-layer DAG, 3 agents (A1,A2,A3), 0 conflicts
   - Class B: 40-node, 10 agents, collision probability ≥ 0.35
   - Class C: 30-node, 10^4 seeded Monte Carlo samples
   - Class D: 4-objective Pareto frontier, 50 solutions

3. Phase 4 (Metrics):
   - Convergence: L₂ norm < epsilon (epsilon = max(1e-8, 0.01 * ||O_0||))
   - Arbitration: 3-step rule (relevance → utility → softmax)
   - Brier Score: ±0.01 tolerance
   - Hypervolume: ±3% tolerance
   - EIG: Information entropy in bits, threshold = 1.0

4. Phase 5 (Logging):
   - Canonical JSON with alphabetical fields
   - Per-iteration SHA-256 state hashing
   - Protocol rules: (1) no mutations, (2) registered tools, (3) frontier integrity
   - RNG audit trail + tool invocation log

5. Phase 6 (Verification):
   - 330 trials (30 per variant × 11 variants)
   - 64 hypothesis tests (Welch's t-test)
   - Bonferroni correction: α_individual = 0.05 / 64 = 0.000781
   - Cohen's d effect size: < 0.2 threshold
   - 10 failure detection criteria

[INSERT verify.py CONTENT HERE]
[INSERT determinism.py CONTENT HERE]

QUESTIONS:
1. Are all 6 phases implemented per specification?
2. Are all metrics correctly defined?
3. Are all workloads correctly implemented?
4. Are tolerance levels correct?
5. Is the verification approach statistically sound?

PROVIDE:
- Compliance matrix (Phase | Requirement | Implementation | Status)
- Any issues found (with line numbers)
- Recommendations for improvement
- Overall assessment: COMPLIANT / ISSUES FOUND / NEEDS REVISION
```

---

## PROMPT 2: Audit Gap Closure Verification

```
TASK: Verify all 11 audit gaps have been properly closed

The MoE Protocol Stage 5 specification had 11 critical audit gaps that needed resolution.
Verify each gap has been properly addressed:

GAP 1: LLM entropy unspecified
- Requirement: LLM sampling must be disabled (temperature = 0.0, greedy decoding only)
- Evidence location: [verify.py, lines 50-60]
- Test verification: [verify.py verification report]

GAP 2: Numerical drift undefined
- Requirement: IEEE 754 double precision, ≤ 1e-10 drift per iteration
- Evidence location: [determinism.py verify_ieee_754_precision()]
- Test verification: [Unit test for precision]

GAP 3: RNG specification vague
- Requirement: PCG64 v0.98 with 4 deterministic entropy branches
- Evidence location: [DeterministicRNG class in verify.py]
- Test verification: [RNG determinism verified: same seed = same output]

GAP 4: State hashing unclear
- Requirement: Canonical JSON → SHA-256, deterministic across platforms
- Evidence location: [compute_state_hash() in verify.py]
- Test verification: [Canonicalization verified]

GAP 5: Threading unspecified
- Requirement: Single-threaded execution only, variance ≤ 5%
- Evidence location: [main() orchestration, no parallelism]
- Test verification: [Single-threaded execution confirmed]

GAP 6: Class A undefined
- Requirement: 25-node 5-layer DAG, 3 agents, 0 conflicts
- Evidence location: [ClassA implementation in verify.py]
- Test verification: [classA.run() produces correct structure]

GAP 7: Class B undefined
- Requirement: 40-node, 10 agents, collision ≥ 0.35
- Evidence location: [ClassB implementation with collision detection]
- Test verification: [Collision probability verified ≥ 0.35]

GAP 8: Class C contradiction
- Requirement: Seeded RNG (Branch 3), deterministic samples
- Evidence location: [ClassC.sample_node_rewards() using branch 3]
- Test verification: [Determinism verified: same seed = same samples]

GAP 9: Class D underspecified
- Requirement: 4-objective Pareto, 50 solutions, dominance rules
- Evidence location: [ClassD.check_dominance() and compute_frontier()]
- Test verification: [Frontier computed correctly]

GAP 10: Metrics undefined
- Requirement: Formal ℝⁿ notation, explicit formulas, tolerances
- Evidence location: [All metric functions with tolerance specifications]
- Test verification: [Metrics computed correctly]

GAP 11: Statistics loose
- Requirement: Bonferroni correction (α = 0.00078), effect size < 0.2
- Evidence location: [StatisticalVerifier class]
- Test verification: [Correction applied to all 64 tests]

PROVIDE:
- Gap closure matrix (Gap # | Requirement | Solution | Status)
- Evidence for each closure
- Any gaps remaining (if found)
- Confidence level for gap closure
```

---

## PROMPT 3: Code Quality and Correctness Review

```
TASK: Review implementation code quality and correctness

Review this implementation code:

[INSERT verify.py CONTENT - Key functions only]

ASSESSMENT CRITERIA:

1. CORRECTNESS
   - Do algorithms match specifications?
   - Are edge cases handled?
   - Are data structures appropriate?
   - Are error conditions handled?

2. DETERMINISM
   - Are there any non-deterministic operations?
   - Is the RNG truly deterministic?
   - Is state management correct?
   - Can reproducibility be guaranteed?

3. CODE QUALITY
   - Is code modular and maintainable?
   - Are functions well-documented?
   - Are naming conventions consistent?
   - Is code DRY (Don't Repeat Yourself)?

4. PERFORMANCE
   - Are algorithms efficient?
   - Are there obvious optimizations?
   - Is memory usage reasonable?
   - Are there bottlenecks?

5. TESTING
   - Are test cases comprehensive?
   - Do tests verify requirements?
   - Are edge cases tested?
   - Are tests reproducible?

PROVIDE:
- Issues found (with line numbers and severity: Critical / Major / Minor)
- Code quality assessment (Excellent / Good / Acceptable / Poor)
- Recommendations for improvement
- Overall code assessment: APPROVED / NEEDS WORK
```

---

## PROMPT 4: Statistical Rigor Review

```
TASK: Review statistical methodology and rigor

VERIFICATION APPROACH:
- 330 trials (30 per variant × 11 variants)
- 64 hypothesis tests (Welch's t-test)
- Bonferroni correction (α_individual = 0.000781)
- Cohen's d effect size (< 0.2 threshold)
- 10 failure detection criteria

STATISTICAL ASSESSMENT:

1. TEST DESIGN
   - Is sample size (330) adequate?
   - Are 11 variants appropriate?
   - Is Welch's t-test the right choice?
   - Are assumptions met?

2. MULTIPLE COMPARISONS
   - Bonferroni correction: α_individual = 0.05 / 64 = 0.000781
   - Is this correctly calculated?
   - Is the approach conservative enough?
   - Are family-wise error rates controlled?

3. EFFECT SIZE
   - Is Cohen's d < 0.2 (trivial effect) appropriate?
   - How is Cohen's d calculated?
   - What does "trivial effect" mean in this context?
   - Are effect sizes interpreted correctly?

4. FAILURE DETECTION
   - Are 10 failure criteria comprehensive?
   - Do they cover all failure modes?
   - Are thresholds appropriate?
   - Is failure detection sensitive enough?

5. TEST RESULTS
   [INSERT verification_report.json HERE]
   - Did all 330 trials complete?
   - Did all 64 tests pass?
   - Were all effect sizes < 0.2?
   - Is the overall result PASS?

PROVIDE:
- Statistical methodology assessment (Sound / Acceptable / Questionable / Flawed)
- Issues with statistical approach (if any)
- Recommendations for improvement
- Confidence in statistical results (High / Medium / Low)
```

---

## PROMPT 5: Documentation and Specification Review

```
TASK: Review documentation completeness and clarity

Review all documentation:

[INSERT SPECIFICATION.md - Key sections]
[INSERT IMPLEMENTATION.md - Full document]
[INSERT BUILD_GUIDE.md - Key sections]

ASSESSMENT CRITERIA:

1. COMPLETENESS
   - Are all phases documented?
   - Are all metrics explained?
   - Are all workloads defined?
   - Are all requirements listed?

2. CLARITY
   - Are explanations clear and understandable?
   - Are examples provided?
   - Are technical terms defined?
   - Is formatting consistent?

3. ACCURACY
   - Do specifications match implementation?
   - Are code examples correct?
   - Are all numbers/tolerances accurate?
   - Are no contradictions?

4. USABILITY
   - Can users build from documentation?
   - Are commands working?
   - Are links functional?
   - Is structure logical?

5. ACCESSIBILITY
   - Is technical level appropriate?
   - Are there diagrams or visualizations?
   - Is there quick-start guide?
   - Is navigation clear?

PROVIDE:
- Documentation assessment (Complete / Mostly Complete / Incomplete)
- Issues found (missing sections, errors, clarifications needed)
- Recommendations for improvement
- User-friendliness rating (Excellent / Good / Acceptable / Poor)
```

---

## PROMPT 6: Combined Assessment

```
TASK: Provide combined peer review assessment

Based on all analyses, provide:

1. OVERALL RECOMMENDATION
   - APPROVE: Ready for production
   - APPROVE WITH COMMENTS: Ready, but has minor issues
   - NEEDS REVISION: Issues must be fixed
   - REJECT: Critical problems found

2. COMPLIANCE SUMMARY
   - Specification compliance: [%]
   - Gap closure: [11/11 or X gaps remaining]
   - Code quality: [Assessment]
   - Test coverage: [Assessment]

3. ISSUES SUMMARY
   - Critical issues: [Count]
   - Major issues: [Count]
   - Minor issues: [Count]
   - No issues: [Yes/No]

4. CONFIDENCE ASSESSMENT
   - Implementation correctness: [High/Medium/Low]
   - Specification compliance: [High/Medium/Low]
   - Statistical rigor: [High/Medium/Low]
   - Production readiness: [High/Medium/Low]

5. RECOMMENDATIONS
   1. [Recommendation 1]
   2. [Recommendation 2]
   [etc]

6. CERTIFICATION DECISION
   Can this implementation be certified as meeting MoE Protocol Stage 5?
   [YES / NO / CONDITIONAL]

7. FINAL ASSESSMENT
   [2-3 paragraph summary of findings]

PROVIDE:
- Structured report following above format
- Clear recommendation (approve/reject/conditional)
- Evidence-based assessment
- Actionable recommendations
```

---

## PROMPT 7: Fast Pre-Review (30 min version)

```
QUICK ASSESSMENT: MoE Protocol Stage 5

I need a fast initial assessment. Please review this implementation
and answer these 10 questions:

[INSERT verify.py - First 100 lines]
[INSERT verification_report.json]

QUICK CHECK:
1. Is LLM temperature set to 0.0? (Yes/No/Unclear)
2. Is IEEE 754 double precision used? (Yes/No/Unclear)
3. Is PCG64 RNG implemented? (Yes/No/Unclear)
4. Are all 4 workload classes defined? (Yes/No/Unclear)
5. Are all 5 metrics specified? (Yes/No/Unclear)
6. Is logging in canonical JSON? (Yes/No/Unclear)
7. Are 330 trials executed? (Yes/No/Unclear)
8. Is Bonferroni correction applied? (Yes/No/Unclear)
9. Are all 11 audit gaps addressed? (Yes/No/Unclear)
10. Is code quality acceptable? (Yes/No/Unclear)

PROVIDE:
- Quick answers to 10 questions
- Any red flags found?
- Overall impression (Looks Good / Has Issues / Needs Review)
- Estimated effort for full review (hours)
```

---

## PROMPT 8: Gap-Specific Deep Dive

```
TASK: Deep dive into specific audit gap closure

Focus on GAP #[X]: [GAP DESCRIPTION]

REQUIREMENT: [Specific requirement]
SPECIFICATION: [From spec]
IMPLEMENTATION: [From code]

VERIFY:
1. Is the requirement correctly understood?
2. Is the implementation addressing the requirement?
3. Are there any alternative interpretations?
4. Is the solution sufficient?
5. Could there be better solutions?

PROVIDE:
- Clear assessment of gap closure
- Any issues with the solution
- Confidence in the solution
- Recommendations if applicable
```

---

## Usage Instructions

1. **Choose the appropriate prompt** based on your review need
2. **Copy the entire prompt** into your LLM interface (ChatGPT, Claude, etc.)
3. **Replace [INSERT ...] sections** with actual file content
4. **Run the prompt** and wait for analysis
5. **Document findings** in your peer review report

---

## Expected Output

Each prompt will generate a structured analysis with:
- ✅ Assessment of compliance
- ✅ Issues found (if any)
- ✅ Recommendations
- ✅ Overall recommendation (APPROVE/NEEDS WORK/REJECT)

---

## Tips for Best Results

1. **Use GPT-4 or Claude 3+** - Better at technical analysis
2. **Provide full context** - More info = better analysis
3. **Be specific** - Detailed prompts get detailed responses
4. **Run multiple prompts** - Different angles catch more issues
5. **Have humans verify** - LLMs can hallucinate

---

**Ready to use!** Copy any prompt above and paste into your LLM.

See LLM_PEER_REVIEW_GUIDE.md for detailed instructions and best practices.
