#!/usr/bin/env python3
"""
PyFileSorter - Core sorting logic (zero external dependencies)
"""

import hashlib
import json
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# File type categories (ext -> category)
FILE_CATEGORIES = {
    # Images
    '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images',
    '.bmp': 'Images', '.svg': 'Images', '.webp': 'Images', '.tiff': 'Images',
    # Documents
    '.pdf': 'Documents', '.doc': 'Documents', '.docx': 'Documents',
    '.xls': 'Documents', '.xlsx': 'Documents', '.ppt': 'Documents', '.pptx': 'Documents',
    '.txt': 'Documents', '.md': 'Documents', '.csv': 'Documents', '.rtf': 'Documents',
    # Code
    '.py': 'Code', '.js': 'Code', '.ts': 'Code', '.java': 'Code', '.c': 'Code',
    '.cpp': 'Code', '.h': 'Code', '.go': 'Code', '.rs': 'Code', '.rb': 'Code',
    '.php': 'Code', '.html': 'Code', '.css': 'Code', '.json': 'Code', '.xml': 'Code',
    '.yml': 'Code', '.yaml': 'Code', '.toml': 'Code', '.sh': 'Code', '.bat': 'Code',
    # Archives
    '.zip': 'Archives', '.tar': 'Archives', '.gz': 'Archives', '.bz2': 'Archives',
    '.7z': 'Archives', '.rar': 'Archives', '.xz': 'Archives',
    # Audio
    '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio', '.m4a': 'Audio',
    # Video
    '.mp4': 'Video', '.mov': 'Video', '.avi': 'Video', '.mkv': 'Video',
    # Others
    '.exe': 'Executables', '.dmg': 'Executables', '.pkg': 'Executables',
}

def get_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_category(file_path: Path) -> str:
    """Determine category from file extension."""
    ext = file_path.suffix.lower()
    return FILE_CATEGORIES.get(ext, 'Others')

def get_month_folder(file_path: Path) -> str:
    """Get YYYY-MM folder name from file modification time."""
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime('%Y-%m')

def organize_folder(
    source: Path,
    dry_run: bool = True,
    detect_duplicates: bool = True,
    organize_by_type: bool = True,
    organize_by_month: bool = True,
) -> Dict:
    """
    Main organization function.
    Returns JSON-serializable report dict.
    """
    if not source.exists() or not source.is_dir():
        raise ValueError(f"Source path does not exist or is not a directory: {source}")

    seen_hashes: Dict[str, Path] = {}
    report = {
        "source": str(source),
        "dry_run": dry_run,
        "timestamp": datetime.now().isoformat(),
        "moved": [],
        "duplicates": [],
        "skipped": [],
        "errors": [],
        "summary": {
            "total_files": 0,
            "moved_files": 0,
            "duplicate_files": 0,
            "categories": defaultdict(int),
            "months": defaultdict(int),
        }
    }

    # Collect all files first (skip hidden + report/temp files)
    SKIP_SUFFIXES = {'.json', '.log', '.tmp', '.bak'}
    all_files: List[Path] = [
        p for p in source.rglob('*')
        if p.is_file()
        and not p.name.startswith('.')
        and p.suffix.lower() not in SKIP_SUFFIXES
    ]

    report["summary"]["total_files"] = len(all_files)

    for file_path in all_files:
        try:
            file_hash = get_file_hash(file_path) if detect_duplicates else None

            # Duplicate detection
            if detect_duplicates and file_hash in seen_hashes:
                report["duplicates"].append({
                    "original": str(seen_hashes[file_hash]),
                    "duplicate": str(file_path),
                    "hash": file_hash[:16] + "..."
                })
                report["summary"]["duplicate_files"] += 1
                continue

            if detect_duplicates:
                seen_hashes[file_hash] = file_path

            category = get_category(file_path) if organize_by_type else "All"
            month = get_month_folder(file_path) if organize_by_month else ""

            # Build target path
            target_dir = source / category
            if month:
                target_dir = target_dir / month
            target_dir.mkdir(parents=True, exist_ok=True)

            target_path = target_dir / file_path.name

            # Handle name conflicts
            counter = 1
            original_target = target_path
            while target_path.exists() and target_path != file_path:
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            if target_path == file_path:
                report["skipped"].append(str(file_path))
                continue

            action = "WOULD MOVE" if dry_run else "MOVED"
            report["moved"].append({
                "from": str(file_path),
                "to": str(target_path),
                "category": category,
                "month": month,
                "action": action
            })
            report["summary"]["categories"][category] += 1
            if month:
                report["summary"]["months"][month] += 1

            if not dry_run:
                shutil.move(str(file_path), str(target_path))

        except Exception as e:
            report["errors"].append({"file": str(file_path), "error": str(e)})

    report["summary"]["moved_files"] = len(report["moved"])
    # Convert defaultdict to regular dict for JSON
    report["summary"]["categories"] = dict(report["summary"]["categories"])
    report["summary"]["months"] = dict(report["summary"]["months"])

    return report

def save_report(report: Dict, output_path: Path):
    """Save report as pretty JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return output_path