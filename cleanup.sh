#!/bin/bash
# cleanup.sh - Repository cleanup and organization
# Run this script to organize the repository for production

set -e

echo "==================================================================="
echo "NEUVO_MoE Repository Cleanup & Organization"
echo "==================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify we're in the right directory
echo -e "${BLUE}Step 1: Verifying repository...${NC}"
if [ ! -f "README.md" ] || [ ! -d "scripts" ]; then
    echo "Error: Not in NEUVO_MoE root directory"
    exit 1
fi
echo -e "${GREEN}✓ Repository verified${NC}"
echo ""

# Step 2: Remove cache directories
echo -e "${BLUE}Step 2: Removing cache directories...${NC}"
rm -rf .ruff_cache/ __pycache__/ .pytest_cache/ 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Cache cleaned${NC}"
echo ""

# Step 3: Create documentation structure
echo -e "${BLUE}Step 3: Creating documentation structure...${NC}"
mkdir -p docs/guides
mkdir -p docs/peer-review
mkdir -p docs/specifications
mkdir -p docs/reference
echo -e "${GREEN}✓ Created: docs/guides${NC}"
echo -e "${GREEN}✓ Created: docs/peer-review${NC}"
echo -e "${GREEN}✓ Created: docs/specifications${NC}"
echo -e "${GREEN}✓ Created: docs/reference${NC}"
echo ""

# Step 4: Move documentation files
echo -e "${BLUE}Step 4: Organizing documentation files...${NC}"

# Move guides
for file in BUILD_GUIDE.md DEPLOYMENT_SUMMARY.md IMPLEMENTATION.md NEXT_STEPS.md; do
    if [ -f "$file" ]; then
        mv "$file" "docs/guides/"
        echo -e "${GREEN}✓ Moved: $file → docs/guides/${NC}"
    fi
done

# Move peer-review materials
for file in HOW_TO_GET_PEER_VERIFICATION.md PEER_VERIFICATION_GUIDE.md SUBMIT_FOR_PEER_REVIEW.md ANSWER_PEER_VERIFICATION.md; do
    if [ -f "$file" ]; then
        mv "$file" "docs/peer-review/"
        echo -e "${GREEN}✓ Moved: $file → docs/peer-review/${NC}"
    fi
done

# Move specifications
for file in SPECIFICATION.md AUDIT_AND_BUILD_REPORT.md; do
    if [ -f "$file" ]; then
        mv "$file" "docs/specifications/"
        echo -e "${GREEN}✓ Moved: $file → docs/specifications/${NC}"
    fi
done

# Move reference materials
for file in SPRINT_COMPLETION.md COMPLETION_REPORT.txt MANIFEST.md DOCUMENTATION_INDEX.md; do
    if [ -f "$file" ]; then
        mv "$file" "docs/reference/"
        echo -e "${GREEN}✓ Moved: $file → docs/reference/${NC}"
    fi
done

echo ""

# Step 5: Create docs/README.md
echo -e "${BLUE}Step 5: Creating docs/README.md...${NC}"
cat > docs/README.md << 'DOCS_README'
# Documentation

Complete documentation for MoE Protocol Stage 5.

## Quick Links

### 📖 Guides (How-to)
- [BUILD_GUIDE.md](guides/BUILD_GUIDE.md) - Build & deployment
- [DEPLOYMENT_SUMMARY.md](guides/DEPLOYMENT_SUMMARY.md) - Quick reference
- [IMPLEMENTATION.md](guides/IMPLEMENTATION.md) - Implementation details
- [NEXT_STEPS.md](guides/NEXT_STEPS.md) - Three paths forward

### 🔬 Peer Review
- [HOW_TO_GET_PEER_VERIFICATION.md](peer-review/HOW_TO_GET_PEER_VERIFICATION.md) - **Start here**
- [PEER_VERIFICATION_GUIDE.md](peer-review/PEER_VERIFICATION_GUIDE.md) - For reviewers
- [SUBMIT_FOR_PEER_REVIEW.md](peer-review/SUBMIT_FOR_PEER_REVIEW.md) - Templates
- [ANSWER_PEER_VERIFICATION.md](peer-review/ANSWER_PEER_VERIFICATION.md) - Quick answer

### 📋 Technical
- [SPECIFICATION.md](specifications/SPECIFICATION.md) - Full technical spec
- [AUDIT_AND_BUILD_REPORT.md](specifications/AUDIT_AND_BUILD_REPORT.md) - Audit report

### 📚 Reference
- [SPRINT_COMPLETION.md](reference/SPRINT_COMPLETION.md) - Executive summary
- [COMPLETION_REPORT.txt](reference/COMPLETION_REPORT.txt) - Final report
- [MANIFEST.md](reference/MANIFEST.md) - Deployment manifest
- [DOCUMENTATION_INDEX.md](reference/DOCUMENTATION_INDEX.md) - Full index

## Organization

```
docs/
├── guides/           - How-to and implementation guides
├── peer-review/      - Peer verification materials
├── specifications/   - Technical specifications
└── reference/        - Project reference materials
```

## Usage

**New user?** → Start with [../START_HERE.md](../START_HERE.md)

**Want peer verification?** → See [peer-review/](peer-review/)

**Building?** → See [guides/BUILD_GUIDE.md](guides/BUILD_GUIDE.md)

**Technical details?** → See [specifications/](specifications/)
DOCS_README
echo -e "${GREEN}✓ Created: docs/README.md${NC}"
echo ""

# Step 6: Verify no orphaned .md files in root
echo -e "${BLUE}Step 6: Verifying cleanup...${NC}"
orphaned=$(find . -maxdepth 1 -type f -name "*.md" ! -name "README.md" ! -name "START_HERE.md" ! -name "CLEANUP_GUIDE.md" 2>/dev/null | wc -l)
if [ "$orphaned" -eq 0 ]; then
    echo -e "${GREEN}✓ No orphaned .md files${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Found $orphaned .md files in root${NC}"
fi
echo ""

# Step 7: Verify directory structure
echo -e "${BLUE}Step 7: Verifying final structure...${NC}"
for dir in "docs/guides" "docs/peer-review" "docs/specifications" "docs/reference"; do
    count=$(find "$dir" -type f | wc -l)
    echo -e "${GREEN}✓ $dir: $count files${NC}"
done
echo ""

# Step 8: Test verification still works
echo -e "${BLUE}Step 8: Testing verification pipeline...${NC}"
if python scripts/verify.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Verification pipeline works${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Verification pipeline may have issues${NC}"
fi
echo ""

# Step 9: Show final structure
echo -e "${BLUE}Step 9: Final repository structure:${NC}"
echo ""
tree -L 2 -I '__pycache__|*.pyc' 2>/dev/null || find . -maxdepth 2 -type f -o -type d | head -30
echo ""

echo "==================================================================="
echo -e "${GREEN}✓ CLEANUP COMPLETE${NC}"
echo "==================================================================="
echo ""
echo "Next steps:"
echo "  1. Review the new structure"
echo "  2. git add -A"
echo "  3. git commit -m 'chore: reorganize documentation'"
echo "  4. Continue with peer verification"
echo ""
