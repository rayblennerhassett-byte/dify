#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
prepare_bundle.py - Handover package preparation script

This script packages current logs, verification artifacts,
and a SHA-256 digest of the logs directory into a tarball for transfer.

Usage:
    prepare_bundle.py [-h] [--output OUTPUT] [--digest]

Options:
    -h, --help       Show this help message and exit
    --output OUTPUT  Output filename (default: handover-bundle.tar.gz)
    --digest         Include SHA-256 digest of logs directory in output

Example:
    python prepare_bundle.py --output my-handover-bundle.tar.gz
"""

import argparse
import os
import shutil
import tarfile
import hashlib
from pathlib import Path


def calculate_sha256(file_path):
    """Calculate SHA-256 hash for a file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_bundle(output_file, include_digest=False):
    """Create handover bundle tarball."""
    # Define directories to include
    log_dir = Path("logs")
    artifacts_dir = Path("artifacts")

    # Prepare files for inclusion
    files_to_include = []

    # Add logs directory if it exists
    if log_dir.exists() and log_dir.is_dir():
        files_to_include.append(str(log_dir))

    # Add artifacts directory if it exists
    if artifacts_dir.exists() and artifacts_dir.is_dir():
        files_to_include.append(str(artifacts_dir))

    # Create tarball
    with tarfile.open(output_file, "w:gz") as tar:
        for file_path in files_to_include:
            tar.add(file_path)

    print(f"Bundle created successfully: {output_file}")

    if include_digest and log_dir.exists():
        digest = calculate_sha256(str(log_dir / ".digest.sha256"))
        with open(output_file, "ab") as f:
            f.write(digest.encode("utf-8"))
        print(f"SHA-256 digest added to bundle")


def main():
    parser = argparse.ArgumentParser(
        description="Create handover package bundle",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--output",
        default="handover-bundle.tar.gz",
        help="Output filename for the tarball",
    )

    parser.add_argument(
        "--digest",
        action="store_true",
        help="Include SHA-256 digest of logs directory in output",
    )

    args = parser.parse_args()

    create_bundle(args.output, include_digest=args.digest)


if __name__ == "__main__":
    main()
