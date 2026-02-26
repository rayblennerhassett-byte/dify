#!/usr/bin/env python3
"""
MoE Stage 5: One-Command Deployment & Verification
Orchestrates Phases 1-6 with full verification suite
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


def print_banner(text):
    width = 70
    print("\n" + "="*width)
    print(text.center(width))
    print("="*width)


def run_command(cmd, description):
    """Run shell command with output"""
    print(f"\n▶ {description}")
    print(f"  $ {cmd}\n")
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    return result.returncode == 0


def check_environment():
    """Verify Python 3.11+ and dependencies"""
    print_banner("ENVIRONMENT CHECK")
    
    # Python version
    version = sys.version_info
    py_ver = f"{version.major}.{version.minor}.{version.micro}"
    print(f"✓ Python {py_ver}")
    
    # Check required packages
    required = ['numpy', 'scipy', 'networkx']
    try:
        for pkg in required:
            __import__(pkg)
            print(f"✓ {pkg}")
    except ImportError as e:
        print(f"✗ Missing: {pkg}")
        print(f"  Install with: pip install -r requirements.txt")
        return False
    
    return True


def build_docker():
    """Build Docker image"""
    print_banner("DOCKER BUILD")
    
    cmd = "docker build -t neuvo-moe:5.0 -f Dockerfile ."
    return run_command(cmd, "Building Docker image")


def run_verification_local():
    """Run verification locally (Python)"""
    print_banner("LOCAL VERIFICATION SUITE")
    
    cmd = "python scripts/verify.py"
    return run_command(cmd, "Executing verification pipeline")


def run_verification_docker():
    """Run verification in Docker"""
    print_banner("CONTAINERIZED VERIFICATION")
    
    # Create logs dir
    os.makedirs("logs", exist_ok=True)
    
    cmd = "docker run --rm -v $(pwd)/logs:/app/logs neuvo-moe:5.0"
    return run_command(cmd, "Running verification in Docker container")


def generate_report():
    """Generate final report"""
    print_banner("FINAL REPORT")
    
    logs_dir = Path("logs")
    report_file = logs_dir / "verification_report.json"
    
    if report_file.exists():
        with open(report_file) as f:
            report = json.load(f)
        
        print(f"\nVerification Status: {report.get('verification_status', 'UNKNOWN')}")
        print(f"Trials Executed: {report.get('trials_executed', 0)}")
        print(f"Tests Passed: {report.get('tests_passed', 0)}/{report.get('tests_total', 0)}")
        print(f"Specification: {report.get('specification_id', 'N/A')}")
        print(f"Timestamp: {report.get('timestamp', 'N/A')}")
        
        return report.get('verification_status') == 'PASS'
    else:
        print("✗ Report file not found")
        return False


def main():
    print_banner("MoE STAGE 5: ONE-COMMAND DEPLOYMENT")
    
    # Parse arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    
    if mode == "docker":
        print("\n[MODE] Containerized Verification")
        if not build_docker():
            print("✗ Docker build failed")
            return False
        if not run_verification_docker():
            print("✗ Docker verification failed")
            return False
    elif mode == "local":
        print("\n[MODE] Local Verification")
        if not check_environment():
            print("✗ Environment check failed")
            return False
        if not run_verification_local():
            print("✗ Local verification failed")
            return False
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python deploy.py [local|docker]")
        return False
    
    # Generate report
    success = generate_report()
    
    print_banner("DEPLOYMENT COMPLETE")
    
    if success:
        print("\n✓ Verification PASSED")
        print("\nNext steps:")
        print("  1. Review logs/verification_report.json")
        print("  2. Submit for peer review")
        print("  3. Request certification")
    else:
        print("\n✗ Verification FAILED")
        print("\nCheck logs for details:")
        print("  cat logs/iteration_*.jsonl")
        print("  cat logs/verification_report.json")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
