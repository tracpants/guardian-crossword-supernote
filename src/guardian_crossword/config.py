"""
Configuration file for the crossword downloader.
Contains constants, Guardian URL patterns, and retention policies.
"""

# File retention policies
LOCAL_RETENTION_DAYS = 30      # Keep 30 days of local files (~120 files)
CLOUD_RETENTION_DAYS = 90      # Keep 90 days on SuperNote (~360 files)
MAX_LOCAL_FILES = 150          # Fallback limit (very generous)
MAX_CLOUD_FILES = 400          # Fallback limit (very generous)

# Directory paths
import os

def get_downloads_dir(custom_dir: str = None) -> str:
    """
    Get the downloads directory path with support for custom directories.
    
    Args:
        custom_dir: Custom directory path (can be relative or absolute)
        
    Returns:
        Absolute path to downloads directory
    """
    if custom_dir:
        # Expand user home directory (~) and environment variables
        expanded_path = os.path.expanduser(os.path.expandvars(custom_dir))
        return os.path.abspath(expanded_path)
    
    # Check for environment variable
    env_dir = os.getenv('GUARDIAN_DOWNLOADS_DIR')
    if env_dir:
        expanded_path = os.path.expanduser(os.path.expandvars(env_dir))
        return os.path.abspath(expanded_path)
    
    # Default to relative downloads directory
    return "downloads"

DOWNLOADS_DIR = get_downloads_dir()  # Default value, can be overridden
LOGS_DIR = "logs"
SUPERNOTE_PUZZLES_DIR = "Document/puzzles"

# Guardian crossword configuration
GUARDIAN_BASE_URL = "https://crosswords-static.guim.co.uk"
GUARDIAN_URL_PATTERN = "{base_url}/gdn.{puzzle_type}.{date_str}.pdf"

# Guardian puzzle types and their availability
GUARDIAN_PUZZLE_TYPES = {
    "quick": {
        "days": [0, 1, 2, 3, 4, 5],  # Monday-Saturday
        "name": "Quick Crossword"
    },
    "cryptic": {
        "days": [0, 1, 2, 3, 4],     # Monday-Friday
        "name": "Cryptic Crossword"
    },
    "quick-cryptic": {
        "days": [5],                  # Saturday only
        "name": "Quick-Cryptic Crossword"
    },
    "weekend": {
        "days": [5],                  # Saturday only
        "name": "Weekend Crossword"
    }
}

# File naming convention
FILENAME_PATTERN = "guardian-{puzzle_type}-{date_str}.pdf"

# Download settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 30  # seconds
FALLBACK_DAYS = 3  # Try up to 3 previous days

# Environment variables
ENV_FILE = ".env"
SUPERNOTE_EMAIL_KEY = "SUPERNOTE_EMAIL"
SUPERNOTE_PASSWORD_KEY = "SUPERNOTE_PASSWORD"

