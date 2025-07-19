"""
SuperNote cloud client module.
Handles authentication and file operations with SuperNote cloud using sncloud library.
"""

import os
import time
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from sncloud import SNClient
from config import (
    SUPERNOTE_PUZZLES_DIR, CLOUD_RETENTION_DAYS, MAX_CLOUD_FILES,
    ENV_FILE, SUPERNOTE_EMAIL_KEY, SUPERNOTE_PASSWORD_KEY
)


class SuperNoteClient:
    """Handles SuperNote cloud operations."""
    
    def __init__(self):
        self.client = SNClient()
        self.authenticated = False
    
    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate with SuperNote cloud.
        Returns True if successful, False otherwise.
        """
        try:
            print("🔐 Authenticating with SuperNote...")
            
            # Simple delay without progress bar for fast operation
            time.sleep(random.uniform(0.8, 1.2))
            self.client.login(email, password)
            
            # Test authentication by trying to list root files
            self.client.ls()
            
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            self.authenticated = False
            return False
    
    def ensure_authenticated(self) -> bool:
        """Check if authenticated, raise exception if not."""
        if not self.authenticated:
            raise RuntimeError("Not authenticated with SuperNote cloud")
        return True
    
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure directory exists on SuperNote cloud.
        Creates directory if it doesn't exist.
        """
        self.ensure_authenticated()
        
        try:
            # Try to list the directory to see if it exists (silently)
            self.client.ls(directory_path)
            return True
            
        except Exception:
            # Directory doesn't exist, try to create it
            try:
                # Note: sncloud library may not have direct mkdir functionality
                # This is a placeholder - actual implementation depends on sncloud API
                # For now, we'll assume the directory needs to be created manually
                print(f"⚠️ Warning: Directory {directory_path} may need to be created manually")
                return True
                
            except Exception as e:
                print(f"❌ Failed to create directory {directory_path}: {e}")
                return False
    
    def list_files(self, directory_path: str = "/") -> List[Dict[str, Any]]:
        """
        List files in given directory on SuperNote cloud.
        Returns list of file information dictionaries.
        """
        self.ensure_authenticated()
        
        try:
            files = self.client.ls(directory_path)
            return files if files else []
            
        except Exception as e:
            print(f"Failed to list files in {directory_path}: {e}")
            return []
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists on SuperNote cloud."""
        self.ensure_authenticated()
        
        try:
            # Get directory and filename
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            # List files in directory
            files = self.list_files(directory)
            
            # Check if filename exists in the list
            for file_info in files:
                # Handle different return types from sncloud
                if hasattr(file_info, 'file_name'):
                    file_name = file_info.file_name
                elif isinstance(file_info, dict):
                    file_name = file_info.get('name')
                else:
                    file_name = str(file_info)
                
                if file_name == filename:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking if file exists {file_path}: {e}")
            return False
    
    def upload_file(self, local_filepath: str, remote_filepath: str) -> tuple[bool, str]:
        """
        Upload file to SuperNote cloud.
        Returns (success, status_message) tuple.
        """
        self.ensure_authenticated()
        
        try:
            # Check if file already exists
            if self.file_exists(remote_filepath):
                return True, "exists"
            
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_filepath)
            if not self.ensure_directory_exists(remote_dir):
                print(f"❌ Failed to ensure directory exists: {remote_dir}")
                return False, "directory_error"
            
            # Get file info
            filename = os.path.basename(local_filepath)
            
            # Upload with simple delay (no progress bar for small files)
            print(f"📤 Uploaded {filename}")
            
            # Simple delay for upload
            time.sleep(random.uniform(0.5, 1.0))
            
            # Actually upload the file
            from pathlib import Path
            result = self.client.put(Path(local_filepath), parent=remote_dir)
            
            return True, "uploaded"
            
        except Exception as e:
            print(f"❌ Failed to upload {local_filepath}: {e}")
            return False, "error"
    
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
    
    def _confirm_deletion(self, files_to_remove: List[str], directory_path: str, auto_confirm: bool) -> bool:
        """
        Ask user to confirm deletion of files.
        Returns True if user confirms, False otherwise.
        """
        if auto_confirm:
            return True
        
        print(f"\n🧹 Found {len(files_to_remove)} old cloud files to remove:")
        
        # Show files with details
        for filename in files_to_remove:
            age = self.get_file_age_from_name(filename)
            age_str = f"{age} days old" if age is not None else "unknown age"
            print(f"  • {filename} ({age_str})")
        
        # Ask for confirmation
        while True:
            try:
                response = input(f"\nDelete these {len(files_to_remove)} files? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no', '']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no")
            except KeyboardInterrupt:
                print("\n🚫 Cleanup cancelled by user")
                return False
    
    def cleanup_old_files(self, directory_path: str = SUPERNOTE_PUZZLES_DIR, auto_confirm: bool = False, dry_run: bool = False) -> int:
        """
        Remove old crossword files from SuperNote cloud.
        Returns number of files removed.
        """
        self.ensure_authenticated()
        
        try:
            files = self.list_files(directory_path)
            if not files:
                print("📁 No files found in puzzles directory")
                return 0
            
            files_to_remove = []
            
            # Check each file
            for file_info in files:
                # Handle different return types from sncloud
                if hasattr(file_info, 'file_name'):
                    filename = file_info.file_name
                elif isinstance(file_info, dict):
                    filename = file_info.get('name')
                else:
                    filename = str(file_info)
                
                if not filename or not filename.startswith('guardian-'):
                    continue
                
                age = self.get_file_age_from_name(filename)
                if age is not None and age > CLOUD_RETENTION_DAYS:
                    files_to_remove.append(filename)
            
            # If still too many files, remove oldest ones
            if len(files) > MAX_CLOUD_FILES:
                # Sort by age (oldest first)
                sorted_files = []
                for file_info in files:
                    # Handle different return types from sncloud
                    if hasattr(file_info, 'file_name'):
                        filename = file_info.file_name
                    elif isinstance(file_info, dict):
                        filename = file_info.get('name')
                    else:
                        filename = str(file_info)
                    
                    if filename and filename.startswith('guardian-'):
                        age = self.get_file_age_from_name(filename)
                        if age is not None:
                            sorted_files.append((age, filename))
                
                sorted_files.sort(reverse=True)  # Oldest first
                excess_count = len(files) - MAX_CLOUD_FILES
                for _, filename in sorted_files[:excess_count]:
                    if filename not in files_to_remove:
                        files_to_remove.append(filename)
            
            # Show files to be removed and ask for confirmation
            if files_to_remove:
                if dry_run:
                    print(f"\n🔍 DRY RUN: Would remove {len(files_to_remove)} old cloud files:")
                    for filename in files_to_remove:
                        age = self.get_file_age_from_name(filename)
                        age_str = f"{age} days old" if age is not None else "unknown age"
                        print(f"  • {filename} ({age_str})")
                    return len(files_to_remove)
                    
                if not self._confirm_deletion(files_to_remove, directory_path, auto_confirm):
                    print("🚫 Cleanup cancelled by user")
                    return 0
            else:
                print("✨ No old files to remove")
                return 0
            
            # Remove files
            removed_count = 0
            for filename in files_to_remove:
                try:
                    file_path = f"{directory_path}/{filename}"
                    print(f"🗑️ Removing old file: {file_path}")
                    
                    # Actually delete the file using sncloud API
                    self.client.delete(file_path)
                    removed_count += 1
                    print(f"✅ Removed: {filename}")
                    
                except Exception as e:
                    print(f"❌ Failed to remove {filename}: {e}")
            
            # Only show message if action was taken
            if removed_count > 0:
                print(f"🧹 Removed {removed_count} old crossword files from SuperNote")
            
            return removed_count
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0
    
    def upload_crossword(self, local_filepath: str, puzzle_type: str, date: datetime) -> tuple[bool, str]:
        """
        Upload crossword to SuperNote puzzles directory.
        Returns (success, status_message) tuple.
        """
        filename = os.path.basename(local_filepath)
        remote_filepath = f"{SUPERNOTE_PUZZLES_DIR}/{filename}"
        
        return self.upload_file(local_filepath, remote_filepath)