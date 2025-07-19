# Guardian Crossword to SuperNote Uploader

Downloads Guardian crosswords and uploads them to SuperNote cloud automatically.

## Features

- Downloads Guardian crosswords (Quick, Cryptic, Quick-Cryptic, Weekend)
- Uploads to SuperNote cloud in `Documents/puzzles`
- Automatic cleanup of old files
- PDF validation and duplicate prevention

## Setup

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure credentials
cp .env.template .env
# Edit .env with your SuperNote email and password
```

## Usage

```bash
# Download today's crosswords
python main.py --today

# Download specific date or type
python main.py --date 2025-01-15
python main.py --date 2025-01-15 --type quick

# Other options
python main.py --info          # Show storage info
python main.py --cleanup       # Clean old files
python main.py --no-upload     # Download only
```

## Configuration

Edit `config.py` to customize retention periods and limits.

**Files**: Stored in `downloads/` locally (30 days) and `Documents/puzzles` on SuperNote (90 days).

## Dependencies

- `sncloud` - SuperNote cloud API
- `python-dotenv` - Environment variables  
- `requests` - HTTP downloads