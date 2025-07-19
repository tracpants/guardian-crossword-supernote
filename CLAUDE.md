# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Guardian Crossword to SuperNote Uploader - a Python application that downloads The Guardian crosswords and uploads them to SuperNote cloud storage automatically. The application handles Quick, Cryptic, Quick-Cryptic, and Weekend crosswords with automatic cleanup and duplicate prevention.

## Development Commands

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure credentials
cp .env.template .env
# Edit .env with SuperNote email and password

# Run the application
python main.py --today                    # Download today's crosswords
python main.py --date 2025-01-15          # Download for specific date
python main.py --date 2025-01-15 --type quick  # Download specific type
python main.py --cleanup                  # Clean old files
python main.py --info                     # Show storage info
python main.py --no-upload               # Download only, no upload

# Cleanup operations
python main.py --cleanup --auto-cleanup   # Auto-confirm cleanup
python main.py --cleanup --dry-run        # Preview cleanup without deletion
```

## Architecture

The application uses a modular architecture with clear separation of concerns:

### Core Modules

- **main.py**: Main orchestrator script handling CLI arguments, credential loading, and workflow coordination
- **guardian_downloader.py**: Downloads crossword PDFs from The Guardian using requests with retry logic and fallback mechanisms
- **supernote_client.py**: Manages SuperNote cloud authentication and file operations using the sncloud library
- **file_manager.py**: Handles local file management, validation, cleanup, and storage tracking
- **config.py**: Centralized configuration including URL patterns, retention policies, and puzzle type schedules

### Data Flow

1. CLI argument parsing determines date and puzzle types
2. Local cleanup removes old files based on retention policy (30 days)
3. Guardian downloader fetches available crosswords with fallback for missing dates
4. File validation ensures PDF integrity and prevents duplicates
5. SuperNote client authenticates and uploads to `Documents/puzzles` directory
6. Cloud cleanup maintains 90-day retention policy

### Configuration System

- **Retention Policies**: Local files kept 30 days (~120 files), cloud files 90 days (~360 files)
- **Puzzle Types**: Quick (Mon-Sat), Cryptic (Mon-Fri), Quick-Cryptic (Sat), Weekend (Sat)
- **File Naming**: `guardian-{puzzle_type}-{YYYYMMDD}.pdf`
- **Error Handling**: 3 retries with 2-second delays, 30-second timeouts

### Dependencies

- `sncloud==0.2.1` - SuperNote cloud API client
- `python-dotenv==1.1.1` - Environment variable management  
- `requests==2.32.4` - HTTP downloads and Guardian website interaction

## Key Implementation Details

- Uses session-based requests with proper User-Agent headers for Guardian downloads
- Implements intelligent fallback (tries up to 3 previous days) for missing crosswords
- File integrity validation prevents uploading corrupted PDFs
- Duplicate detection works across both local and cloud storage
- Cleanup operations require confirmation unless `--auto-cleanup` is specified
- All operations support `--dry-run` for safe preview