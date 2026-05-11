#!/usr/bin/env python3
"""
PyFileSorter CLI - Command line interface
"""

import argparse
import json
import sys
from pathlib import Path
from .sorter import organize_folder, save_report

def main():
    parser = argparse.ArgumentParser(
        prog="pyfilesorter",
        description="Organize files by type and month with duplicate detection. Pure Python, zero dependencies.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (safe preview)
  pyfilesorter organize ~/Downloads --dry-run --report report.json

  # Actually organize
  pyfilesorter organize ~/Downloads --apply --report report.json

  # Only by type, no month folders
  pyfilesorter organize ./messy --apply --no-by-month
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Organize subcommand
    org_parser = subparsers.add_parser("organize", help="Organize a folder")
    org_parser.add_argument("source", type=Path, help="Source folder to organize")
    org_parser.add_argument("--dry-run", action="store_true", default=True,
                           help="Preview changes without moving files (default)")
    org_parser.add_argument("--apply", action="store_true",
                           help="Actually move files (overrides --dry-run)")
    org_parser.add_argument("--no-duplicates", action="store_true",
                           help="Disable duplicate detection")
    org_parser.add_argument("--no-by-type", action="store_true",
                           help="Do not create type folders")
    org_parser.add_argument("--no-by-month", action="store_true",
                           help="Do not create month subfolders")
    org_parser.add_argument("--report", type=Path, default=None,
                           help="Path to save JSON report (default: print to stdout)")
    org_parser.add_argument("--verbose", "-v", action="store_true",
                           help="Show detailed progress")

    args = parser.parse_args()

    if args.command == "organize":
        dry_run = not args.apply  # --apply overrides default dry-run

        try:
            report = organize_folder(
                source=args.source,
                dry_run=dry_run,
                detect_duplicates=not args.no_duplicates,
                organize_by_type=not args.no_by_type,
                organize_by_month=not args.no_by_month,
            )

            if args.report:
                save_report(report, args.report)
                print(f"Report saved to: {args.report}")
            else:
                print(json.dumps(report, indent=2))

            # Summary to stderr for clean piping
            moved = len(report["moved"])
            dups = len(report["duplicates"])
            errors = len(report["errors"])
            mode = "DRY-RUN" if dry_run else "APPLIED"
            print(f"\n[{mode}] {moved} files would be moved, {dups} duplicates found, {errors} errors",
                  file=sys.stderr)

            if not dry_run and moved > 0:
                print("\u2713 Files successfully organized!", file=sys.stderr)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()