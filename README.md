# PyFileSorter

A zero-dependency CLI tool that organizes messy folders by file type and date (YYYY-MM).

## Features
- Organizes by type + month
- Dry-run mode
- Duplicate detection (SHA256)
- JSON reports

## Usage
```bash
python -m pyfilesorter.cli <folder> --dry-run
python -m pyfilesorter.cli <folder> --apply
```
