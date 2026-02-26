# 📋 CLEANUP EXECUTION PLAN

## Step 1: Current State Analysis

**Root .md files to move:** (based on BUILD_GUIDE.md and CLEANUP_GUIDE.md)

Guides → docs/guides/:
- [ ] BUILD_GUIDE.md
- [ ] DEPLOYMENT_SUMMARY.md
- [ ] IMPLEMENTATION.md
- [ ] NEXT_STEPS.md

Peer Review → docs/peer-review/:
- [ ] HOW_TO_GET_PEER_VERIFICATION.md
- [ ] PEER_VERIFICATION_GUIDE.md
- [ ] SUBMIT_FOR_PEER_REVIEW.md
- [ ] ANSWER_PEER_VERIFICATION.md
- [ ] LLM_PEER_REVIEW_GUIDE.md (NEW)
- [ ] LLM_REVIEW_PROMPTS.md (NEW)

Specifications → docs/specifications/:
- [ ] SPECIFICATION.md
- [ ] AUDIT_AND_BUILD_REPORT.md

Reference → docs/reference/:
- [ ] SPRINT_COMPLETION.md
- [ ] COMPLETION_REPORT.txt
- [ ] MANIFEST.md
- [ ] DOCUMENTATION_INDEX.md

Keep in Root (Navigation):
- [ ] README.md (update links)
- [ ] START_HERE.md (update links)

---

## Step 2: Directory Structure to Create

```
docs/
├── README.md (NEW - index for all docs)
├── guides/
├── peer-review/
├── specifications/
└── reference/
```

---

## Step 3: Create Directory Structure

**Command sequence:**
```bash
mkdir -p docs/guides
mkdir -p docs/peer-review
mkdir -p docs/specifications
mkdir -p docs/reference
```

---

## Step 4: Move Documentation Files

**Guides (4 files):**
```bash
mv BUILD_GUIDE.md docs/guides/
mv DEPLOYMENT_SUMMARY.md docs/guides/
mv IMPLEMENTATION.md docs/guides/
mv NEXT_STEPS.md docs/guides/
```

**Peer Review (6 files):**
```bash
mv HOW_TO_GET_PEER_VERIFICATION.md docs/peer-review/
mv PEER_VERIFICATION_GUIDE.md docs/peer-review/
mv SUBMIT_FOR_PEER_REVIEW.md docs/peer-review/
mv ANSWER_PEER_VERIFICATION.md docs/peer-review/
mv LLM_PEER_REVIEW_GUIDE.md docs/peer-review/
mv LLM_REVIEW_PROMPTS.md docs/peer-review/
```

**Specifications (2 files):**
```bash
mv SPECIFICATION.md docs/specifications/
mv AUDIT_AND_BUILD_REPORT.md docs/specifications/
```

**Reference (4 files):**
```bash
mv SPRINT_COMPLETION.md docs/reference/
mv COMPLETION_REPORT.txt docs/reference/
mv MANIFEST.md docs/reference/
mv DOCUMENTATION_INDEX.md docs/reference/
```

---

## Step 5: Create docs/README.md

Create file: `docs/README.md` with complete documentation index and navigation.

**Content:** [See docs/README.md template in CLEANUP_GUIDE.md]

---

## Step 6: Update START_HERE.md (Root)

Update links from relative paths to `docs/` subdirectories.

**Current links:**
```
BUILD_GUIDE.md → docs/guides/BUILD_GUIDE.md
HOW_TO_GET_PEER_VERIFICATION.md → docs/peer-review/HOW_TO_GET_PEER_VERIFICATION.md
SPECIFICATION.md → docs/specifications/SPECIFICATION.md
etc...
```

---

## Step 7: Update README.md (Root)

Update repository structure section to reflect new docs/ organization.

**Add:**
- docs/ directory structure
- References to docs/guides/, docs/peer-review/, etc.

---

## Step 8: Clean Up Cache

```bash
rm -rf .ruff_cache/
rm -rf __pycache__/
rm -rf .pytest_cache/
```

---

## Step 9: Verify After Cleanup

**Check directories exist:**
```bash
ls -la docs/guides/
ls -la docs/peer-review/
ls -la docs/specifications/
ls -la docs/reference/
```

**Verify key files moved:**
```bash
ls docs/guides/BUILD_GUIDE.md
ls docs/peer-review/HOW_TO_GET_PEER_VERIFICATION.md
ls docs/specifications/SPECIFICATION.md
```

**Check no orphaned .md files in root:**
```bash
ls -1 *.md | grep -v README | grep -v START_HERE | grep -v CLEANUP_GUIDE | grep -v FINAL_STATUS | grep -v COMPLETE_DELIVERY_SUMMARY | grep -v DELIVERY_INDEX
# Should return nothing
```

---

## Step 10: Run Verification

```bash
python scripts/verify.py
# Should output: Status: PASS ✅
```

---

## Step 11: Git Commit

```bash
git add -A
git commit -m "chore: reorganize documentation structure

- Move guides to docs/guides/
- Move peer-review materials to docs/peer-review/
- Move specifications to docs/specifications/
- Move reference materials to docs/reference/
- Clean up cache directories
- Update README and START_HERE with new links
- Organize for production release

All functionality preserved, documentation reorganized for clarity.
Specification ID: MoE-S5-v5.0
Audit-By: Gordon (LLM Assistant)"
```

---

## Final Checklist

- [ ] Step 1: Current state analyzed
- [ ] Step 2: Directory structure planned
- [ ] Step 3: docs/ directories created
- [ ] Step 4: Documentation files moved (16 files)
- [ ] Step 5: docs/README.md created
- [ ] Step 6: START_HERE.md updated with new links
- [ ] Step 7: README.md updated with new structure
- [ ] Step 8: Cache directories cleaned
- [ ] Step 9: Verification performed
- [ ] Step 10: python scripts/verify.py runs successfully
- [ ] Step 11: Git commit completed

---

## Result After Cleanup

✅ **Root directory:** Clean (only essential files: README.md, START_HERE.md, scripts/, src/, docs/, logs/, Dockerfile, requirements.txt, deploy.py)

✅ **docs/ directory:** Organized (guides/, peer-review/, specifications/, reference/)

✅ **Documentation:** All 15+ guides organized in logical structure

✅ **Functionality:** 100% preserved

✅ **Ready for:** Peer verification, distribution, production

---

## Summary

**Total files to move:** 16 documentation files  
**Time required:** ~10 minutes  
**Result:** Professional, organized repository  

**Status After Cleanup:** READY FOR PEER VERIFICATION & DISTRIBUTION ✅
