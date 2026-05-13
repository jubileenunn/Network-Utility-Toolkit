import os
import hashlib
import argparse
from collections import defaultdict
from pathlib import Path

def hash_file(path, chunk_size=8192):
    """Return the SHA256 hash of a file."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha.update(chunk)
    return sha.hexdigest()

def find_duplicates(root_dir):
    """
    Walk through the directory and group files by their hash.
    Returns:
        {hash_value: [list_of_paths_with_that_hash]}
    """
    root = Path(root_dir)
    duplicates = defaultdict(list)

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                file_hash = hash_file(file_path)
                duplicates[file_hash].append(file_path)
            except (PermissionError, OSError) as e:
                print(f"⚠️  Skipping {file_path}: {e}")

    # Only return groups that actually contain duplicates
    return {h: paths for h, paths in duplicates.items() if len(paths) > 1}

def summarize_duplicates(dupe_map):
    """Print a summary of all detected duplicate groups."""
    total_groups = len(dupe_map)
    total_files = sum(len(paths) for paths in dupe_map.values())

    print(f"\n🔍 Found {total_groups} duplicate groups ({total_files} files total).\n")

    for i, (hash_value, paths) in enumerate(dupe_map.items(), start=1):
        print(f"Group {i} — hash: {hash_value[:12]}...")
        for p in paths:
            print(f"   • {p}")
        print()

def delete_duplicates(dupe_map, keep_first=True, dry_run=True):
    """
    Delete duplicates while keeping one file per group.
    If dry_run=True, only prints what would be deleted.
    """
    files_to_delete = []

    for paths in dupe_map.values():
        # Sort for predictable behavior
        sorted_paths = sorted(paths, key=lambda p: str(p))
        file_to_keep = sorted_paths[0] if keep_first else None

        for p in sorted_paths:
            if keep_first and p == file_to_keep:
                continue
            files_to_delete.append(p)

    if not files_to_delete:
        print("✨ No files to delete.")
        return

    print("🗑️  Files marked for deletion:")
    for p in files_to_delete:
        print(f"   • {p}")

    if dry_run:
        print("\n(Dry run enabled — no files were deleted.)")
        return

    print("\nDeleting files...")
    for p in files_to_delete:
        try:
            os.remove(p)
            print(f"✔️  Deleted: {p}")
        except (PermissionError, OSError) as e:
            print(f"❌ Failed to delete {p}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Smart File Deduplicator — safely detect and remove duplicate files."
    )

    parser.add_argument("directory", help="Directory to scan for duplicates")
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete duplicates (keeps one copy per group)",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually delete files instead of previewing",
    )

    args = parser.parse_args()

    print(f"📁 Scanning directory: {args.directory}")
    duplicates = find_duplicates(args.directory)

    if not duplicates:
        print("🎉 No duplicates found!")
        return

    summarize_duplicates(duplicates)

    if args.delete:
        delete_duplicates(
            duplicates,
            keep_first=True,
            dry_run=not args.no_dry_run
        )
    else:
        print("ℹ️  Run again with --delete to remove duplicates (dry run by default).")

if __name__ == "__main__":
    main()
