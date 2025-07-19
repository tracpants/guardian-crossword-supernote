# Guardian Crossword to SuperNote Uploader

Downloads The Guardian crosswords and uploads them to your SuperNote cloud automatically.

## Installation

```bash
git clone https://github.com/tracpants/guardian-crossword-supernote.git
cd guardian-crossword-supernote
pip install .
```

## Setup

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` with your SuperNote credentials:
   ```
   SUPERNOTE_EMAIL=your_email@example.com
   SUPERNOTE_PASSWORD=your_password_here
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