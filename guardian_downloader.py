"""
Guardian crossword downloader module.
Handles downloading crossword PDFs from The Guardian website.
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from config import (
    GUARDIAN_BASE_URL, GUARDIAN_URL_PATTERN, GUARDIAN_PUZZLE_TYPES,
    FILENAME_PATTERN, MAX_RETRIES, RETRY_DELAY, REQUEST_TIMEOUT,
    FALLBACK_DAYS, DOWNLOADS_DIR
)


class GuardianDownloader:
    """Handles downloading Guardian crossword PDFs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def generate_url(self, puzzle_type: str, date: datetime) -> str:
        """Generate Guardian crossword URL for given type and date."""
        date_str = date.strftime('%Y%m%d')
        return GUARDIAN_URL_PATTERN.format(
            base_url=GUARDIAN_BASE_URL,
            puzzle_type=puzzle_type,
            date_str=date_str
        )
    
    def generate_filename(self, puzzle_type: str, date: datetime) -> str:
        """Generate local filename for crossword PDF."""
        date_str = date.strftime('%Y%m%d')
        return FILENAME_PATTERN.format(
            puzzle_type=puzzle_type,
            date_str=date_str
        )
    
    def is_puzzle_available_on_day(self, puzzle_type: str, date: datetime) -> bool:
        """Check if puzzle type is available on given day of week."""
        if puzzle_type not in GUARDIAN_PUZZLE_TYPES:
            return False
        
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        return weekday in GUARDIAN_PUZZLE_TYPES[puzzle_type]["days"]
    
    def get_fallback_dates(self, puzzle_type: str, target_date: datetime) -> List[datetime]:
        """Get list of fallback dates for puzzle type."""
        fallback_dates = []
        current_date = target_date
        
        for _ in range(FALLBACK_DAYS):
            if self.is_puzzle_available_on_day(puzzle_type, current_date):
                fallback_dates.append(current_date)
            
            # Move to previous day
            current_date -= timedelta(days=1)
        
        return fallback_dates
    
    def validate_pdf(self, filepath: str) -> bool:
        """Validate that downloaded file is a valid PDF."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(8)
                return header.startswith(b'%PDF-')
        except Exception:
            return False
    
    def download_with_retries(self, url: str, filepath: str) -> bool:
        """Download file with retry logic."""
        filename = os.path.basename(filepath)
        
        for attempt in range(MAX_RETRIES):
            try:
                # Get file size first if possible
                try:
                    head_response = self.session.head(url, timeout=REQUEST_TIMEOUT)
                    total_size = int(head_response.headers.get('content-length', 0))
                except:
                    total_size = 50000  # Estimate for Guardian crosswords
                
                # Simple download without progress bar for small files
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                # Write to file
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Validate PDF
                if self.validate_pdf(filepath):
                    print(f"📥 Downloaded {filename}")
                    return True
                else:
                    print(f"❌ Downloaded file is not a valid PDF: {filename}")
                    os.remove(filepath)
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Download failed (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    return False
            except Exception as e:
                print(f"❌ Unexpected error during download: {e}")
                return False
        
        return False
    
    def download_crossword(self, puzzle_type: str, target_date: datetime) -> Optional[str]:
        """
        Download Guardian crossword for given type and date.
        Returns local filepath if successful, None otherwise.
        """
        if puzzle_type not in GUARDIAN_PUZZLE_TYPES:
            print(f"Unknown puzzle type: {puzzle_type}")
            return None
        
        # Ensure downloads directory exists
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        
        # Get fallback dates (including target date)
        fallback_dates = self.get_fallback_dates(puzzle_type, target_date)
        
        if not fallback_dates:
            print(f"No available dates for {puzzle_type} around {target_date.strftime('%Y-%m-%d')}")
            return None
        
        # Try each fallback date
        for date in fallback_dates:
            url = self.generate_url(puzzle_type, date)
            filename = self.generate_filename(puzzle_type, date)
            filepath = os.path.join(DOWNLOADS_DIR, filename)
            
            # Check if file already exists locally
            if os.path.exists(filepath) and self.validate_pdf(filepath):
                print(f"File already exists: {filepath}")
                return filepath
            
            # Try to download
            if self.download_with_retries(url, filepath):
                return filepath
            
            print(f"Failed to download {puzzle_type} for {date.strftime('%Y-%m-%d')}")
        
        print(f"Failed to download {puzzle_type} for any fallback date")
        return None
    
    def get_available_crosswords(self, date: datetime) -> List[str]:
        """Get list of crossword types available for given date."""
        available = []
        weekday = date.weekday()
        
        for puzzle_type, config in GUARDIAN_PUZZLE_TYPES.items():
            if weekday in config["days"]:
                available.append(puzzle_type)
        
        return available
    
    def download_all_for_date(self, date: datetime) -> List[Tuple[str, str]]:
        """
        Download all available crosswords for given date.
        Returns list of (puzzle_type, filepath) tuples for successful downloads.
        """
        available_types = self.get_available_crosswords(date)
        successful_downloads = []
        
        for puzzle_type in available_types:
            filepath = self.download_crossword(puzzle_type, date)
            if filepath:
                successful_downloads.append((puzzle_type, filepath))
        
        return successful_downloads