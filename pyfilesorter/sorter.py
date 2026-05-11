import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json

CATEGORY_MAP = {
    '.jpg': 'Images', '.png': 'Images', '.gif': 'Images', '.svg': 'Images',
    '.pdf': 'Documents', '.docx': 'Documents', '.txt': 'Documents', '.xlsx': 'Documents',
    '.py': 'Code', '.js': 'Code', '.sh': 'Code', '.go': 'Code',
    '.zip': 'Archives', '.rar': 'Archives',
    '.mp3': 'Audio', '.wav': 'Audio',
    '.mp4': 'Video', '.mov': 'Video',
    '.exe': 'Executables', '.app': 'Executables',
}

def get_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def organize_folder(source_folder: str, dry_run: bool = True, report_path: str = None):
    source = Path(source_folder)
    if not source.is_dir():
        return {"error": "Not a directory"}
    
    duplicates = set()
    hash_seen = {}
    moved = []
    skipped = []
    
    for item in source.iterdir():
        if item.is_file():
            ext = item.suffix.lower()
            category = CATEGORY_MAP.get(ext, 'Others')
            month = item.stat().st_mtime
            date_str = datetime.fromtimestamp(month).strftime('%Y-%m')
            target_dir = source / category / date_str
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = target_dir / item.name
            
            file_hash = get_file_hash(str(item))
            if file_hash in hash_seen:
                duplicates.add(item.name)
                continue
            
            hash_seen[file_hash] = True
            
            if target_path.exists():
                target_path = target_path.with_name(target_path.stem + '_1' + target_path.suffix)
            
            if not dry_run:
                shutil.move(str(item), str(target_path))
                moved.append(str(target_path))
            else:
                moved.append(str(target_path))
    
    report = {
        "moved": len(moved),
        "duplicates": len(duplicates),
        "summary": "Demo complete"
    }
    if report_path:
        Path(report_path).write_text(json.dumps(report, indent=2))
    
    return report
