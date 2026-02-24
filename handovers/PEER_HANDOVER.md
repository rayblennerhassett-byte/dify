# Peer LLM Handover Kit — MoE Stage 5

Purpose
- Provide a compact, reproducible handover package for a peer LLM to validate MoE Protocol Stage 5 verification without ambiguity.
- Includes environment setup, runbook, artifact expectations, and verification criteria to achieve a PASSED Stage 5 certification.

Scope of Handover
- Primary artifacts to reproduce: 330 trials across 11 variants, 64 statistical tests, and a final verification report in JSON.
- Run environment: Docker-based deterministic container or a locally pinned Python environment.
- Expected outputs: logs/ (metadata.json, iteration_N.jsonl, rng_audit.jsonl, tool_calls.jsonl) and verification_report.json.

Delivery Package
- This repository contains the following handover assets:
  - handovers/PEER_HANDOVER.md (this document)
  - handovers/README.md (quick start for peers)
  - handovers/verification_report_example.json (template for final report)

Prerequisites
- Access to a Linux x86-64 environment (recommended) or a GitHub/CI runner that supports Docker.
- Docker or Python 3.11+ with pinned dependencies.
- Git to fetch the repository and verify integrity of committed hashes.

Deployment & Verification Runbook (peer workflow)
- Step 0: Prepare environment
  - If using Docker: build a hardened image (moe-stage5-determinism)
  - If using local Python: install pinned dependencies from requirements.txt
  - Ensure deterministic CPU settings (OMP/BLAS threads = 1) to match primary.

- Step 1: Acquire primary artifacts
  - Clone or fetch the MoE repo and pull the primary logs from the designated location.
  - Ensure you have the same seeds and iterations as in the primary run.

- Step 2: Reproduce verification run (partial)
  - Run the trial runner for a small subset (e.g., first 5 iterations) to validate environment parity.

- Step 3: Full verification run (recommended)
  - Build and run the verification workflow to generate logs/ and verification_report.json.
  - Validate that:
    - 330 trials completed
    - 64 tests pass with p > 0.00078 and |d| < 0.2 where applicable
    - CPI deviation ≤ 5%
    - Arbitration is deterministic and there are no protocol violations

- Step 4: Compare to the provided verification_report example
  - Confirm the schema matches the example (or update your local copy accordingly).

- Step 5: Certification decision
  - If all checks pass, mark as READY for Stage 6; otherwise, document issues and open remediation.

Artifact Reference
- Current Verification Report Template: handovers/verification_report_example.json
- See also: logs/ and the verification script in scripts/verify.py

Notes for Peer Verifiers
- The peer’s environment must mirror the primary environment as closely as possible to ensure deterministic results.
- If minor architecture differences exist, the peer should report and explain any adjustments in the verification report.

Appendix: Quick Start (Copy-Paste)
- Build (Docker):
  docker build -t moe-stage5-determinism -f Dockerfile .
- Run (Container):
  docker run --rm -it moe-stage5-determinism
- Local Run (Python):
  python -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  python scripts/verify.py

End of handover kit.
