@echo off
REM NEUVO_MoE Documentation Consolidation Batch Script
REM This script deletes redundant files and completes consolidation

cd /d "E:\REPO\NEUVO_MoE"

echo.
echo ================================================================
echo  NEUVO_MoE Documentation Consolidation Script
echo ================================================================
echo.
echo Deleting 18 redundant files...
echo.

REM Delete redundant files
del /Q "CLEANUP_COMPLETE.md" 2>nul && echo [OK] CLEANUP_COMPLETE.md || echo [SKIP] CLEANUP_COMPLETE.md
del /Q "BUILD_AND_CLEANUP_COMPLETE.md" 2>nul && echo [OK] BUILD_AND_CLEANUP_COMPLETE.md || echo [SKIP] BUILD_AND_CLEANUP_COMPLETE.md
del /Q "BUILD_AND_TEST_READY.md" 2>nul && echo [OK] BUILD_AND_TEST_READY.md || echo [SKIP] BUILD_AND_TEST_READY.md
del /Q "LLM_REVIEW_READY.md" 2>nul && echo [OK] LLM_REVIEW_READY.md || echo [SKIP] LLM_REVIEW_READY.md
del /Q "THREE_STEP_EXECUTION_COMPLETE.md" 2>nul && echo [OK] THREE_STEP_EXECUTION_COMPLETE.md || echo [SKIP] THREE_STEP_EXECUTION_COMPLETE.md
del /Q "FINAL_EXECUTION_INDEX.md" 2>nul && echo [OK] FINAL_EXECUTION_INDEX.md || echo [SKIP] FINAL_EXECUTION_INDEX.md
del /Q "DELIVERY_INDEX.md" 2>nul && echo [OK] DELIVERY_INDEX.md || echo [SKIP] DELIVERY_INDEX.md
del /Q "COMPLETION_REPORT.txt" 2>nul && echo [OK] COMPLETION_REPORT.txt || echo [SKIP] COMPLETION_REPORT.txt
del /Q "FINAL_SUMMARY.txt" 2>nul && echo [OK] FINAL_SUMMARY.txt || echo [SKIP] FINAL_SUMMARY.txt
del /Q "FINAL_STATUS.md" 2>nul && echo [OK] FINAL_STATUS.md || echo [SKIP] FINAL_STATUS.md
del /Q "FINAL_VERIFICATION_CHECKLIST.md" 2>nul && echo [OK] FINAL_VERIFICATION_CHECKLIST.md || echo [SKIP] FINAL_VERIFICATION_CHECKLIST.md
del /Q "COMPLETE_DELIVERY_SUMMARY.md" 2>nul && echo [OK] COMPLETE_DELIVERY_SUMMARY.md || echo [SKIP] COMPLETE_DELIVERY_SUMMARY.md
del /Q "DOCUMENTATION_INDEX.md" 2>nul && echo [OK] DOCUMENTATION_INDEX.md || echo [SKIP] DOCUMENTATION_INDEX.md
del /Q "CLEANUP_GUIDE.md" 2>nul && echo [OK] CLEANUP_GUIDE.md || echo [SKIP] CLEANUP_GUIDE.md
del /Q "NEXT_STEPS.md" 2>nul && echo [OK] NEXT_STEPS.md || echo [SKIP] NEXT_STEPS.md
del /Q "BUILD_GUIDE.md" 2>nul && echo [OK] BUILD_GUIDE.md || echo [SKIP] BUILD_GUIDE.md
del /Q "ANSWER_PEER_VERIFICATION.md" 2>nul && echo [OK] ANSWER_PEER_VERIFICATION.md || echo [SKIP] ANSWER_PEER_VERIFICATION.md
del /Q "SUBMIT_FOR_PEER_REVIEW.md" 2>nul && echo [OK] SUBMIT_FOR_PEER_REVIEW.md || echo [SKIP] SUBMIT_FOR_PEER_REVIEW.md

echo.
echo ================================================================
echo  File cleanup complete!
echo ================================================================
echo.
echo Remaining .md files in root:
dir /b *.md
echo.
echo Next steps:
echo   1. git add -A
echo   2. git commit -m "chore: consolidate documentation..."
echo.
pause
