"""
Main CLI module for Guardian crossword downloader.
Downloads Guardian crosswords and uploads them to SuperNote cloud.
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

from .downloader import GuardianDownloader
from .client import SuperNoteClient
from .file_manager import FileManager
from .config import (
    GUARDIAN_PUZZLE_TYPES, ENV_FILE,
    SUPERNOTE_EMAIL_KEY, SUPERNOTE_PASSWORD_KEY,
    SUPERNOTE_PUZZLES_DIR
)


def load_credentials() -> tuple[str, str]:
    """Load SuperNote credentials from environment variables."""
    load_dotenv(ENV_FILE)
    
    email = os.getenv(SUPERNOTE_EMAIL_KEY)
    password = os.getenv(SUPERNOTE_PASSWORD_KEY)
    
    if not email or not password:
        print(f"❌ Error: SuperNote credentials not found in {ENV_FILE}")
        print(f"Please set {SUPERNOTE_EMAIL_KEY} and {SUPERNOTE_PASSWORD_KEY}")
        sys.exit(1)
    
    return email, password


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"❌ Error: Invalid date format '{date_str}'. Use YYYY-MM-DD")
        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Download Guardian crosswords and upload to SuperNote',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available puzzle types:
{chr(10).join(f"  {ptype}: {info['name']}" for ptype, info in GUARDIAN_PUZZLE_TYPES.items())}

Examples:
  %(prog)s --today                    # Download today's available crosswords
  %(prog)s --date 2025-01-15          # Download crosswords for specific date
  %(prog)s --date 2025-01-15 --type quick  # Download specific type for date
  %(prog)s --cleanup                  # Only run cleanup operations
  %(prog)s --cleanup --auto-cleanup   # Run cleanup without confirmation
  %(prog)s --cleanup --dry-run        # Show what would be cleaned up
  %(prog)s --info                     # Show storage information
        """
    )
    
    # Date options
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('--today', action='store_true',
                           help='Download crosswords for today')
    date_group.add_argument('--date', type=str,
                           help='Download crosswords for specific date (YYYY-MM-DD)')
    
    # Puzzle type options
    parser.add_argument('--type', choices=list(GUARDIAN_PUZZLE_TYPES.keys()),
                       help='Specific puzzle type to download')
    
    # Operation options
    parser.add_argument('--cleanup', action='store_true',
                       help='Only run cleanup operations (local and cloud)')
    parser.add_argument('--info', action='store_true',
                       help='Show storage information')
    parser.add_argument('--no-upload', action='store_true',
                       help='Download only, do not upload to SuperNote')
    parser.add_argument('--auto-cleanup', action='store_true',
                       help='Skip confirmation prompts for cleanup operations')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be cleaned up without actually deleting')
    
    args = parser.parse_args()
    
    # Initialize components
    file_manager = FileManager()
    
    # Handle info request
    if args.info:
        file_manager.print_storage_info()
        return
    
    # Handle cleanup-only request
    if args.cleanup:
        print("🧹 Running cleanup operations...")
        
        # Clean up local files
        file_manager.cleanup_old_files(auto_confirm=args.auto_cleanup, dry_run=args.dry_run)
        file_manager.cleanup_invalid_files()
        
        # Clean up cloud files (if not --no-upload)
        if not args.no_upload:
            email, password = load_credentials()
            supernote = SuperNoteClient()
            
            if supernote.authenticate(email, password):
                supernote.cleanup_old_files(auto_confirm=args.auto_cleanup, dry_run=args.dry_run)
            else:
                print("❌ Failed to authenticate with SuperNote for cloud cleanup")
        
        return
    
    # Determine target date
    if args.today:
        target_date = datetime.now()
    elif args.date:
        target_date = parse_date(args.date)
    else:
        # Default to today
        target_date = datetime.now()
    
    print(f"📅 Processing crosswords for {target_date.strftime('%Y-%m-%d')}")
    
    # Run local cleanup first (only show if action needed)
    cleaned_files = file_manager.cleanup_old_files(auto_confirm=args.auto_cleanup, dry_run=args.dry_run)
    invalid_files = file_manager.cleanup_invalid_files()
    
    if cleaned_files > 0 or invalid_files > 0:
        print()  # Add spacing only if cleanup messages were shown
    
    # Initialize downloader
    downloader = GuardianDownloader()
    
    # Determine which puzzle types to download
    if args.type:
        puzzle_types = [args.type]
    else:
        puzzle_types = downloader.get_available_crosswords(target_date)
    
    if not puzzle_types:
        print(f"❌ No crosswords available for {target_date.strftime('%Y-%m-%d')}")
        return
    
    print(f"🧩 Available: {', '.join(puzzle_types)}")
    print()
    
    # Download crosswords (simplified output)
    successful_downloads = []
    
    for puzzle_type in puzzle_types:
        filepath = downloader.download_crossword(puzzle_type, target_date)
        if filepath:
            successful_downloads.append((puzzle_type, filepath))
        else:
            print(f"❌ Failed to download {puzzle_type} crossword")
    
    if not successful_downloads:
        print("❌ No crosswords were successfully downloaded")
        return
    
    # Upload to SuperNote (unless --no-upload)
    if args.no_upload:
        print("\n⏭️ Skipping upload to SuperNote (--no-upload specified)")
        return
    
    # Load credentials and authenticate
    print()
    email, password = load_credentials()
    supernote = SuperNoteClient()
    
    if not supernote.authenticate(email, password):
        print("❌ Failed to authenticate with SuperNote")
        return
    
    # Ensure puzzles directory exists (silently)
    supernote.ensure_directory_exists(SUPERNOTE_PUZZLES_DIR)
    
    # Upload each successful download (simplified output)
    upload_count = 0
    exists_count = 0
    for puzzle_type, filepath in successful_downloads:
        success, status = supernote.upload_crossword(filepath, puzzle_type, target_date)
        if success:
            if status == "uploaded":
                upload_count += 1
            elif status == "exists":
                print(f"⏭️ Already exists: {os.path.basename(filepath)}")
                exists_count += 1
        else:
            print(f"❌ Failed to upload {os.path.basename(filepath)}")
    
    # Show summary based on what actually happened
    if upload_count > 0 and exists_count > 0:
        print(f"\n✅ Completed: {upload_count} uploaded, {exists_count} already existed")
    elif upload_count > 0:
        print(f"\n✅ Completed: {upload_count}/{len(successful_downloads)} files uploaded")
    elif exists_count > 0:
        print(f"\n✅ Completed: All {exists_count} files already existed on SuperNote")
    else:
        print(f"\n✅ Completed: 0/{len(successful_downloads)} files uploaded")
    
    # Run cloud cleanup (only show if action needed)
    supernote.cleanup_old_files(auto_confirm=args.auto_cleanup, dry_run=args.dry_run)
    
    print("\n🎉 All operations completed!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)