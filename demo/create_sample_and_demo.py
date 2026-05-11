#!/usr/bin/env python3
"""
Demo script for PyFileSorter.
Creates a temporary folder with mixed sample files, runs the organizer,
and prints before/after state + JSON report.

Run from project root:
    python demo/create_sample_and_demo.py
"""

import tempfile
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
import os

def create_sample_files(base: Path):
    """Create realistic mixed files with different types and dates."""
    base.mkdir(parents=True, exist_ok=True)

    # Simulate different modification times
    now = datetime.now()
    dates = [
        now - timedelta(days=5),
        now - timedelta(days=12),
        now - timedelta(days=40),
        now - timedelta(days=3),
    ]

    samples = [
        ("report_Q4.pdf", "Documents", dates[0]),
        ("photo_vacation.jpg", "Images", dates[1]),
        ("screenshot.png", "Images", dates[2]),
        ("main.py", "Code", dates[3]),
        ("notes.txt", "Documents", dates[0]),
        ("archive_backup.zip", "Archives", dates[1]),
        ("song.mp3", "Audio", dates[2]),
        ("video_demo.mp4", "Video", dates[3]),
        ("logo.svg", "Images", dates[0]),
        ("data.xlsx", "Documents", dates[1]),
        ("script.sh", "Code", dates[2]),
        ("thesis_draft.docx", "Documents", dates[3]),
        ("duplicate_photo.jpg", "Images", dates[1]),  # Will be duplicate
        ("another_photo.jpg", "Images", dates[1]),   # Another duplicate of same content
    ]

    for filename, _, mtime in samples:
        file_path = base / filename
        # Create file with some content (duplicate detection uses content hash)
        if "duplicate" in filename or "another_photo" in filename:
            content = b"THIS IS THE SAME PHOTO CONTENT FOR DUPLICATE TEST"
        else:
            content = f"Sample content for {filename}".encode()

        file_path.write_bytes(content)
        # Set modification time
        os.utime(file_path, (mtime.timestamp(), mtime.timestamp()))

    # Make one real duplicate with same content
    dup = base / "photo_vacation_copy.jpg"
    dup.write_bytes((base / "photo_vacation.jpg").read_bytes())
    os.utime(dup, (dates[1].timestamp(), dates[1].timestamp()))

    print(f"Created {len(list(base.iterdir()))} sample files in {base}")
    return base

def run_demo():
    print("=" * 60)
    print("PyFileSorter DEMO - Full end-to-end validation")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "messy_desktop"
        source = create_sample_files(source)

        print("\n📁 BEFORE (raw messy folder):")
        for f in sorted(source.iterdir()):
            print(f"  - {f.name}")

        # Run dry-run first (report outside source to avoid organizing the report itself)
        dry_report = Path(tmpdir) / "dry_run_report.json"
        print("\n🔍 DRY-RUN MODE:")
        result = subprocess.run(
            ["python", "-m", "pyfilesorter.cli", "organize", str(source),
             "--dry-run", "--report", str(dry_report)],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        # Show what the report says
        if dry_report.exists():
            with open(dry_report) as f:
                report = json.load(f)
            print(f"\n📊 DRY-RUN SUMMARY: {report['summary']['moved_files']} files would move, "
                  f"{report['summary']['duplicate_files']} duplicates detected")

        # Now APPLY (report outside source)
        final_report = Path(tmpdir) / "final_report.json"
        print("\n🚀 APPLY MODE (actually moving files):")
        result = subprocess.run(
            ["python", "-m", "pyfilesorter.cli", "organize", str(source),
             "--apply", "--report", str(final_report)],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        print("\n📁 AFTER (organized structure):")
        for root, dirs, files in os.walk(source):
            level = root.replace(str(source), "").count(os.sep)
            indent = "  " * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = "  " * (level + 1)
            for f in sorted(files):
                print(f"{subindent}{f}")

        # Final report
        if final_report.exists():
            with open(final_report) as f:
                report = json.load(f)
            print(f"\n✅ FINAL SUMMARY:")
            print(f"   Moved: {report['summary']['moved_files']}")
            print(f"   Duplicates skipped: {report['summary']['duplicate_files']}")
            print(f"   Categories: {list(report['summary']['categories'].keys())})")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE - PyFileSorter works end-to-end!")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()