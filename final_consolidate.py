#!/usr/bin/env python3
"""
Final ruthless consolidation: Delete all 25 redundant meta/status files.
Reduces documentation bloat from 40+ .md files to 8 essential.
"""

import os
import sys
from pathlib import Path

def main():
    os.chdir(r"E:\REPO\NEUVO_MoE")
    
    # 25 files to delete (meta bloat only)
    files_to_delete = [
        # Meta status files (15)
        "SPRINT_COMPLETION.md",
        "MANIFEST.md",
        "CLEANUP_COMPLETE.md",
        "BUILD_AND_CLEANUP_COMPLETE.md",
        "BUILD_AND_TEST_READY.md",
        "LLM_REVIEW_READY.md",
        "THREE_STEP_EXECUTION_COMPLETE.md",
        "FINAL_EXECUTION_INDEX.md",
        "FINAL_STATUS.md",
        "FINAL_VERIFICATION_CHECKLIST.md",
        "FINAL_SUMMARY.txt",
        "COMPLETION_REPORT.txt",
        "COMPLETE_DELIVERY_SUMMARY.md",
        "CONSOLIDATION_COMPLETE.md",
        "READY_TO_CONSOLIDATE.md",
        
        # Consolidation planning files (5)
        "CONSOLIDATION_PLAN.md",
        "CONSOLIDATION_SUMMARY.md",
        "CONSOLIDATION_EXECUTION_READY.md",
        "CONSOLIDATION_COMMIT_READY.md",
        "CONSOLIDATION.md",  # This file itself after execution
        
        # Navigation bloat (2)
        "DELIVERY_INDEX.md",
        "DOCUMENTATION_INDEX.md",
        "NEXT_STEPS.md",
        
        # Helper scripts (2)
        "consolidate.bat",
        "execute_consolidation.py",
    ]
    
    deleted = 0
    failed = 0
    
    print("=" * 70)
    print("  RUTHLESS DOCUMENTATION CONSOLIDATION")
    print("=" * 70)
    print(f"\nDeleting {len(files_to_delete)} meta/redundant files...\n")
    
    for fname in files_to_delete:
        fpath = Path(fname)
        if fpath.exists():
            try:
                fpath.unlink()
                print(f"  ✅ {fname}")
                deleted += 1
            except Exception as e:
                print(f"  ❌ {fname}: {e}")
                failed += 1
        else:
            print(f"  ⊘ {fname} (not found)")
    
    print(f"\n" + "=" * 70)
    print(f"  RESULT: {deleted} deleted, {failed} failed")
    print("=" * 70)
    
    # Count remaining .md files
    remaining = list(Path(".").glob("*.md"))
    print(f"\n📋 Remaining .md files in root: {len(remaining)}")
    for f in sorted(remaining):
        print(f"   - {f.name}")
    
    if len(remaining) == 8:
        print(f"\n✅ CONSOLIDATION SUCCESSFUL (80% reduction)")
    else:
        print(f"\n⚠️ Expected 8 files, found {len(remaining)}")
    
    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print("\n1. Verify: python scripts/verify.py")
    print("2. Commit: git add -A && git commit -m '...'")
    print("3. Deploy: docker build && docker run")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
