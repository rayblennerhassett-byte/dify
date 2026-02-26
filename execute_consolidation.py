#!/usr/bin/env python3
"""
NEUVO_MoE Documentation Consolidation Script

This script executes the file consolidation as described in CONSOLIDATION_PLAN.md
It moves files to docs/ subdirectories and deletes redundant files.
"""

import os
import shutil
import sys
from pathlib import Path

def main():
    base_dir = Path.cwd()
    print(f"📂 Working directory: {base_dir}\n")
    
    # Ensure we're in the right directory
    if not (base_dir / "scripts" / "verify.py").exists():
        print("❌ Error: Not in NEUVO_MoE root directory (scripts/verify.py not found)")
        sys.exit(1)
    
    # Step 1: Verify docs/ subdirectories exist
    print("📁 Verifying docs/ subdirectories...")
    subdirs = ["guides", "peer-review", "specifications", "reference"]
    for subdir in subdirs:
        path = base_dir / "docs" / subdir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: docs/{subdir}/")
        else:
            print(f"  ✓ Exists: docs/{subdir}/")
    
    # Step 2: Move files to docs/ subdirectories
    print("\n📦 Moving files to docs/...\n")
    
    moves = {
        "CLEANUP_EXECUTION_PLAN.md": "docs/guides/CLEANUP.md",
        "SPRINT_COMPLETION.md": "docs/reference/SPRINT_COMPLETION.md",
        "MANIFEST.md": "docs/reference/MANIFEST.md",
    }
    
    for src, dst in moves.items():
        src_path = base_dir / src
        dst_path = base_dir / dst
        
        if src_path.exists():
            # Only move if destination doesn't already exist
            if dst_path.exists():
                print(f"  ⚠️  Skipped (already exists): {src} → {dst}")
            else:
                shutil.move(str(src_path), str(dst_path))
                print(f"  ✅ Moved: {src} → {dst}")
        else:
            print(f"  ⚠️  Not found: {src}")
    
    # Step 3: Delete redundant files (18 total)
    print("\n🗑️  Deleting redundant files...\n")
    
    delete_list = [
        "CLEANUP_COMPLETE.md",
        "BUILD_AND_CLEANUP_COMPLETE.md",
        "BUILD_AND_TEST_READY.md",
        "LLM_REVIEW_READY.md",
        "THREE_STEP_EXECUTION_COMPLETE.md",
        "FINAL_EXECUTION_INDEX.md",
        "DELIVERY_INDEX.md",
        "COMPLETION_REPORT.txt",
        "FINAL_SUMMARY.txt",
        "FINAL_STATUS.md",
        "FINAL_VERIFICATION_CHECKLIST.md",
        "COMPLETE_DELIVERY_SUMMARY.md",
        "DOCUMENTATION_INDEX.md",
        "CLEANUP_GUIDE.md",
        "NEXT_STEPS.md",
        "BUILD_GUIDE.md",
        "ANSWER_PEER_VERIFICATION.md",
        "SUBMIT_FOR_PEER_REVIEW.md",
    ]
    
    deleted_count = 0
    for fname in delete_list:
        fpath = base_dir / fname
        if fpath.exists():
            fpath.unlink()
            print(f"  ✅ Deleted: {fname}")
            deleted_count += 1
        else:
            print(f"  ⚠️  Not found: {fname}")
    
    # Step 4: Verify final state
    print(f"\n✅ Consolidation Summary")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Count .md files in root
    md_files = list(base_dir.glob("*.md"))
    print(f"  .md files in root: {len(md_files)}")
    print(f"  Files deleted: {deleted_count}/18")
    print(f"  Files moved: 3")
    
    # List remaining .md files
    print(f"\n📋 Remaining .md files in root:")
    for md in sorted(md_files):
        print(f"    - {md.name}")
    
    print(f"\n✅ Consolidation COMPLETE!")
    print(f"\nNext steps:")
    print(f"  1. Review root directory: ls -1 *.md")
    print(f"  2. Review docs/ structure: tree docs/")
    print(f"  3. Run verification: python scripts/verify.py")
    print(f"  4. Git commit: git add -A && git commit -m '...'")

if __name__ == "__main__":
    main()
