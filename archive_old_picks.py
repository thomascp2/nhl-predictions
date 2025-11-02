"""
Archive Outdated Prediction Files
Moves prediction files older than 24 hours to archive/ folder

Usage:
    python archive_old_picks.py [--dry-run]

Options:
    --dry-run    Show what would be archived without actually moving files
"""

import os
import shutil
import re
from datetime import datetime, timedelta
import argparse


def parse_timestamp_from_filename(filename):
    """
    Extract timestamp from prediction filename

    Patterns supported:
    - NHL_PREDICTIONS_2025-11-01_143022.csv
    - ENHANCED_PICKS_2025-11-01_143022.txt
    - GOALIE_SAVES_2025-11-01_143022.csv
    - PRIZEPICKS_EDGES_2025-11-01_143022.csv
    - GTO_PARLAYS_2025-11-01_143022.txt

    Returns:
        datetime object or None if pattern doesn't match
    """
    # Match pattern: YYYY-MM-DD_HHMMSS
    pattern = r'(\d{4})-(\d{2})-(\d{2})_(\d{6})'
    match = re.search(pattern, filename)

    if match:
        year, month, day, time_str = match.groups()
        hour = time_str[:2]
        minute = time_str[2:4]
        second = time_str[4:6]

        try:
            return datetime(int(year), int(month), int(day),
                          int(hour), int(minute), int(second))
        except ValueError:
            return None

    return None


def get_files_to_archive(base_dir='.', cutoff_hours=24):
    """
    Find prediction files older than cutoff_hours

    Args:
        base_dir: Directory to search for prediction files
        cutoff_hours: Archive files older than this many hours

    Returns:
        List of (filepath, timestamp) tuples
    """
    cutoff_time = datetime.now() - timedelta(hours=cutoff_hours)
    files_to_archive = []

    # File patterns to match
    patterns = [
        'NHL_PREDICTIONS_*.csv',
        'ENHANCED_PICKS_*.txt',
        'ENHANCED_PICKS_*.csv',
        'GOALIE_SAVES_*.csv',
        'PRIZEPICKS_EDGES_*.csv',
        'GTO_PARLAYS_*.txt',
        'GTO_PARLAYS_*.csv',
    ]

    # Files to always keep (never archive)
    keep_files = [
        'LATEST_PICKS.txt',
        'LATEST_PICKS.csv',
        'LATEST_EDGES.csv',
        'LATEST_PARLAYS.txt',
    ]

    for filename in os.listdir(base_dir):
        # Skip if it's a keep file
        if filename in keep_files:
            continue

        # Skip if not a prediction file
        is_prediction_file = any(
            filename.startswith(p.split('*')[0])
            for p in patterns
        )
        if not is_prediction_file:
            continue

        # Parse timestamp
        file_time = parse_timestamp_from_filename(filename)
        if file_time is None:
            continue

        # Check if old enough to archive
        if file_time < cutoff_time:
            filepath = os.path.join(base_dir, filename)
            files_to_archive.append((filepath, file_time))

    return files_to_archive


def archive_files(files_to_archive, archive_base='archive/predictions', dry_run=False):
    """
    Move old files to archive directory organized by date

    Args:
        files_to_archive: List of (filepath, timestamp) tuples
        archive_base: Base directory for archives
        dry_run: If True, only print what would be done

    Returns:
        Number of files archived
    """
    if not files_to_archive:
        print("No files to archive.")
        return 0

    archived_count = 0

    for filepath, file_time in files_to_archive:
        # Create archive subdirectory by date (YYYY-MM)
        year_month = file_time.strftime('%Y-%m')
        archive_dir = os.path.join(archive_base, year_month)

        filename = os.path.basename(filepath)
        dest_path = os.path.join(archive_dir, filename)

        if dry_run:
            print(f"[DRY RUN] Would move: {filepath}")
            print(f"          To: {dest_path}")
            archived_count += 1
        else:
            # Create archive directory if it doesn't exist
            os.makedirs(archive_dir, exist_ok=True)

            # Move file to archive
            try:
                shutil.move(filepath, dest_path)
                print(f"Archived: {filename} → {archive_dir}/")
                archived_count += 1
            except Exception as e:
                print(f"Error archiving {filename}: {e}")

    return archived_count


def main():
    parser = argparse.ArgumentParser(
        description='Archive outdated prediction files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be archived without moving files'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Archive files older than this many hours (default: 24)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("NHL Prediction File Archival")
    print("=" * 60)
    print(f"Cutoff: {args.hours} hours ago")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Find files to archive
    print("Scanning for old prediction files...")
    files_to_archive = get_files_to_archive(cutoff_hours=args.hours)

    if not files_to_archive:
        print("[OK] No old files found. All files are recent!")
        return

    print(f"Found {len(files_to_archive)} file(s) to archive:")
    print()

    # Sort by timestamp
    files_to_archive.sort(key=lambda x: x[1])

    # Archive the files
    archived_count = archive_files(
        files_to_archive,
        archive_base='archive/predictions',
        dry_run=args.dry_run
    )

    print()
    print("=" * 60)
    if args.dry_run:
        print(f"DRY RUN: Would archive {archived_count} file(s)")
    else:
        print(f"[OK] Archived {archived_count} file(s)")
    print("=" * 60)


if __name__ == '__main__':
    main()
