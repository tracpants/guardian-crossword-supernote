# Guardian Crossword to SuperNote Uploader

Downloads The Guardian crosswords and uploads them to your SuperNote cloud automatically.

## Installation

```bash
git clone https://github.com/tracpants/guardian-crossword-supernote.git
cd guardian-crossword-supernote
pip install .
```

## Setup

**Option 1: Environment Variables (Recommended)**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export SUPERNOTE_EMAIL="your_email@example.com"
export SUPERNOTE_PASSWORD="your_password_here"

# Then reload your shell or run:
source ~/.bashrc  # or ~/.zshrc
```

**Option 2: .env File**
```bash
cp .env.template .env
# Edit .env with your SuperNote credentials
```

## Usage

```bash
# Download today's crosswords
guardian-crossword --today

# Download specific date
guardian-crossword --date 2025-01-15

# Download specific puzzle type
guardian-crossword --today --type quick

# Show storage info
guardian-crossword --info

# Clean up old files
guardian-crossword --cleanup
```

## Automation

To automatically download crosswords daily, add to your crontab:

```bash
# Edit crontab
crontab -e

# Add this line to download at 9 AM daily
0 9 * * * /usr/local/bin/guardian-crossword --today
```

**Note**: Use full paths in cron jobs. Find your path with `which guardian-crossword`

## Puzzle Types

- `quick` - Quick Crossword (Mon-Sat)
- `cryptic` - Cryptic Crossword (Mon-Fri)  
- `quick-cryptic` - Quick-Cryptic Crossword (Sat only)
- `weekend` - Weekend Crossword (Sat only)

## Troubleshooting

**Authentication fails**: Check your SuperNote credentials in `.env`  
**Download fails**: Verify internet connection and Guardian website is accessible  
**Command not found**: Run `pip install .` again

For more options: `guardian-crossword --help`