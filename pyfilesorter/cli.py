import argparse
from .sorter import organize_folder

def main():
    parser = argparse.ArgumentParser(description="PyFileSorter - Organize files by type and date")
    parser.add_argument("folder", help="Folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--report", help="Save JSON report")
    args = parser.parse_args()
    
    dry_run = not args.apply
    report = organize_folder(args.folder, dry_run, args.report)
    print("Organized successfully:", report)

if __name__ == "__main__":
    main()
