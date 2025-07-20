"""
File manager module for local file operations.
Handles cleanup, validation, and management of local crossword files.
"""

import os
import glob
from datetime import datetime
from typing import List, Optional, Tuple
from .config import (
    LOCAL_RETENTION_DAYS, MAX_LOCAL_FILES,
    FILENAME_PATTERN, get_downloads_dir
)


class FileManager:
    """Handles local file management operations."""
    
    def __init__(self, downloads_dir: str = None):
        """
        Initialize FileManager with optional custom downloads directory.
        
        Args:
            downloads_dir: Custom downloads directory path (supports ~ expansion)
        """
        self.downloads_dir = get_downloads_dir(downloads_dir)
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def get_local_files(self) -> List[str]:
        """Get list of all Guardian crossword files in downloads directory."""
        pattern = os.path.join(self.downloads_dir, "guardian-*.pdf")
        files = glob.glob(pattern)
        return sorted(files)
    
    def file_exists_locally(self, filename: str) -> bool:
        """Check if file exists in local downloads directory."""
        filepath = os.path.join(self.downloads_dir, filename)
        return os.path.exists(filepath) and os.path.isfile(filepath)
    
    def get_file_age_from_name(self, filename: str) -> Optional[int]:
        """
        Extract date from Guardian crossword filename and calculate age in days.
        Filename format: guardian-{type}-{YYYYMMDD}.pdf
        """
        try:
            # Extract date part from filename
            parts = filename.split('-')
            if len(parts) >= 3 and filename.startswith('guardian-'):
                date_str = parts[2].replace('.pdf', '')
                if len(date_str) == 8 and date_str.isdigit():
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    age = (datetime.now() - file_date).days
                    return age
            
            return None
            
        except Exception:
            return None
    
    def get_file_date_from_name(self, filename: str) -> Optional[datetime]:
        """
        Extract date from Guardian crossword filename.
        Filename format: guardian-{type}-{YYYYMMDD}.pdf
        """
        try:
            parts = filename.split('-')
            if len(parts) >= 3 and filename.startswith('guardian-'):
                date_str = parts[2].replace('.pdf', '')
                if len(date_str) == 8 and date_str.isdigit():
                    return datetime.strptime(date_str, '%Y%m%d')
            
            return None
            
        except Exception:
            return None
    
    def _confirm_deletion(self, files_to_remove: List[str], auto_confirm: bool) -> bool:
        """
        Ask user to confirm deletion of local files.
        Returns True if user confirms, False otherwise.
        """
        if auto_confirm:
            return True
        
        print(f"\n🧹 Found {len(files_to_remove)} old local files to remove:")
        
        # Show files with details
        for filepath in files_to_remove:
            filename = os.path.basename(filepath)
            age = self.get_file_age_from_name(filename)
            age_str = f"{age} days old" if age is not None else "unknown age"
            
            try:
                size = os.path.getsize(filepath)
                size_str = f"{size:,} bytes"
            except:
                size_str = "unknown size"
            
            print(f"  • {filename} ({age_str}, {size_str})")
        
        # Ask for confirmation
        while True:
            try:
                response = input(f"\nDelete these {len(files_to_remove)} local files? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no', '']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no")
            except KeyboardInterrupt:
                print("\n🚫 Local cleanup cancelled by user")
                return False
    
    def validate_pdf(self, filepath: str) -> bool:
        """Validate that file is a valid PDF."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(8)
                return header.startswith(b'%PDF-')
        except Exception:
            return False
    
    def get_file_info(self, filepath: str) -> dict:
        """Get detailed information about a file."""
        filename = os.path.basename(filepath)
        try:
            stat = os.stat(filepath)
            return {
                'filepath': filepath,
                'filename': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'age_days': self.get_file_age_from_name(filename),
                'file_date': self.get_file_date_from_name(filename),
                'is_valid_pdf': self.validate_pdf(filepath)
            }
        except Exception as e:
            return {
                'filepath': filepath,
                'filename': filename,
                'error': str(e)
            }
    
    def cleanup_old_files(self, auto_confirm: bool = False, dry_run: bool = False) -> int:
        """
        Remove old crossword files from local downloads directory.
        Returns number of files removed.
        """
        files = self.get_local_files()
        if not files:
            return 0
        
        files_to_remove = []
        
        # Check each file for age
        for filepath in files:
            filename = os.path.basename(filepath)
            age = self.get_file_age_from_name(filename)
            
            if age is not None and age > LOCAL_RETENTION_DAYS:
                files_to_remove.append(filepath)
        
        # If still too many files, remove oldest ones
        if len(files) > MAX_LOCAL_FILES:
            # Get file info with dates
            file_info_list = []
            for filepath in files:
                filename = os.path.basename(filepath)
                age = self.get_file_age_from_name(filename)
                if age is not None:
                    file_info_list.append((age, filepath))
            
            # Sort by age (oldest first)
            file_info_list.sort(reverse=True)
            
            # Add excess files to removal list
            excess_count = len(files) - MAX_LOCAL_FILES
            for age, filepath in file_info_list[:excess_count]:
                if filepath not in files_to_remove:
                    files_to_remove.append(filepath)
        
        # Show files to be removed and ask for confirmation
        if files_to_remove:
            if dry_run:
                print(f"\n🔍 DRY RUN: Would remove {len(files_to_remove)} old local files:")
                for filepath in files_to_remove:
                    filename = os.path.basename(filepath)
                    age = self.get_file_age_from_name(filename)
                    age_str = f"{age} days old" if age is not None else "unknown age"
                    
                    try:
                        size = os.path.getsize(filepath)
                        size_str = f"{size:,} bytes"
                    except:
                        size_str = "unknown size"
                    
                    print(f"  • {filename} ({age_str}, {size_str})")
                return len(files_to_remove)
                
            if not self._confirm_deletion(files_to_remove, auto_confirm):
                print("🚫 Local cleanup cancelled by user")
                return 0
        else:
            print("✨ No old local files to remove")
            return 0
        
        # Remove files
        removed_count = 0
        for filepath in files_to_remove:
            try:
                os.remove(filepath)
                print(f"Removed old file: {os.path.basename(filepath)}")
                removed_count += 1
            except Exception as e:
                print(f"Failed to remove {filepath}: {e}")
        
        # Only show message if action was taken
        if removed_count > 0:
            print(f"🧹 Removed {removed_count} old local files")
        
        return removed_count
    
    def cleanup_invalid_files(self) -> int:
        """
        Remove invalid PDF files from downloads directory.
        Returns number of files removed.
        """
        files = self.get_local_files()
        if not files:
            return 0
            
        removed_count = 0
        
        # Validate files silently, only report if issues found
        for filepath in files:
            if not self.validate_pdf(filepath):
                try:
                    os.remove(filepath)
                    print(f"🗑️ Removed invalid PDF: {os.path.basename(filepath)}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove invalid PDF {filepath}: {e}")
        
        # Only show message if action was taken
        if removed_count > 0:
            print(f"🧹 Removed {removed_count} invalid PDF files")
        
        return removed_count
    
    def get_storage_info(self) -> dict:
        """Get information about local storage usage."""
        files = self.get_local_files()
        total_size = 0
        valid_files = 0
        invalid_files = 0
        oldest_date = None
        newest_date = None
        
        for filepath in files:
            try:
                size = os.path.getsize(filepath)
                total_size += size
                
                if self.validate_pdf(filepath):
                    valid_files += 1
                else:
                    invalid_files += 1
                
                # Track date range
                filename = os.path.basename(filepath)
                file_date = self.get_file_date_from_name(filename)
                if file_date:
                    if oldest_date is None or file_date < oldest_date:
                        oldest_date = file_date
                    if newest_date is None or file_date > newest_date:
                        newest_date = file_date
                        
            except Exception:
                invalid_files += 1
        
        return {
            'total_files': len(files),
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_date': oldest_date,
            'newest_date': newest_date,
            'downloads_dir': self.downloads_dir
        }
    
    def print_storage_info(self):
        """Print formatted storage information."""
        info = self.get_storage_info()
        
        print(f"\n=== Local Storage Info ===")
        print(f"Directory: {info['downloads_dir']}")
        print(f"Total files: {info['total_files']}")
        print(f"Valid PDFs: {info['valid_files']}")
        print(f"Invalid files: {info['invalid_files']}")
        print(f"Total size: {info['total_size_mb']:.2f} MB")
        
        if info['oldest_date'] and info['newest_date']:
            print(f"Date range: {info['oldest_date'].strftime('%Y-%m-%d')} to {info['newest_date'].strftime('%Y-%m-%d')}")
        
        print(f"Retention policy: {LOCAL_RETENTION_DAYS} days (max {MAX_LOCAL_FILES} files)")
        print("="*26)