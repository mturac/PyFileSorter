# PyFileSorter

**CLI tool that automatically organizes messy folders by file type + month with duplicate detection (SHA256).**

- Dry-run mode (safe preview)
- Apply mode (actually moves files)
- Zero external dependencies — pure Python 3.8+
- JSON report for every run
- Duplicate files are detected by content hash and skipped

## Who is this for?

Anyone with a chaotic Downloads, Desktop, or project folder who wants order in one command.

## Why it exists

Finding files wastes hours. This tool turns chaos into predictable structure:
```
Downloads/
├── Images/2025-04/
├── Documents/2025-03/
├── Code/2025-05/
└── Archives/2025-04/
```

## Tech Stack

- Pure Python 3 (stdlib only: pathlib, hashlib, shutil, argparse, json, datetime)
- No pip install required

## Installation

```bash
git clone https://github.com/mturac/PyFileSorter.git
cd PyFileSorter
```

No installation needed — run directly with `python -m`.

## Running Locally

### Dry-run (recommended first)

```bash
python -m pyfilesorter.cli organize /path/to/messy/folder --dry-run
```

### Apply changes

```bash
python -m pyfilesorter.cli organize /path/to/messy/folder --apply
```

### Save JSON report

```bash
python -m pyfilesorter.cli organize ~/Downloads --apply --report my_report.json
```

### Options

```bash
python -m pyfilesorter.cli organize ~/Downloads --apply \
  --no-by-month \      # flat category folders only
  --no-duplicates \    # skip hash check
  --verbose
```

## Example Usage (from demo)

```bash
# 1. Create sample messy folder and run full demo
python demo/create_sample_and_demo.py
```

This creates 15 mixed files, runs dry-run, then apply, and prints before/after + report.

## Current Limitations

- Does not handle filename conflicts gracefully beyond simple `_1` suffix
- Modification time used for month (not creation time on all OSes)
- No undo (use git or backup first)
- Hidden files (starting with `.`) are ignored

## Roadmap

- [ ] Config file support (`~/.pyfilesorter.json`)
- [ ] Custom category rules
- [ ] Watch mode (auto-organize on file change)
- [ ] GUI version (optional)

## Validation / Testing

Run the demo script — it proves the entire flow works reproducibly:

```bash
python demo/create_sample_and_demo.py
```

Expected output: 13 files moved, 2 duplicates detected, clean category/month structure created.

## License

MIT — use freely, contribute improvements.