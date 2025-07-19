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
DOWNLOADS_DIR = "downloads"
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

