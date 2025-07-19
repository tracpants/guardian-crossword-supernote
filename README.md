# Guardian Crossword to SuperNote Uploader

A Python application that automatically downloads The Guardian crosswords and uploads them to your SuperNote cloud storage. Perfect for crossword enthusiasts who want their daily puzzles seamlessly delivered to their SuperNote device.

## Features

- 🧩 **Multiple puzzle types**: Quick, Cryptic, Quick-Cryptic, and Weekend crosswords
- ☁️ **Cloud integration**: Automatic upload to SuperNote cloud in `Documents/puzzles`
- 🧹 **Smart cleanup**: Configurable retention policies (30 days local, 90 days cloud)
- ✅ **PDF validation**: Ensures downloaded files are valid PDFs
- 🚫 **Duplicate prevention**: Won't re-download existing files
- 📅 **Flexible scheduling**: Download for specific dates or today's puzzles
- 🏗️ **Modern architecture**: Clean Python package with multiple entry points

## Quick Start

### Prerequisites
- Python 3.8 or higher
- SuperNote cloud account
- Active internet connection

### Installation

#### Option 1: Install as Package (Recommended)
```bash
# Clone and install
git clone https://github.com/tracpants/guardian-crossword-supernote.git
cd guardian-crossword-supernote
pip install .

# Configure credentials
cp .env.template .env
# Edit .env with your SuperNote email and password
```

#### Option 2: Development Setup
```bash
# Clone repository
git clone https://github.com/tracpants/guardian-crossword-supernote.git
cd guardian-crossword-supernote

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .  # Install in development mode

# Configure credentials
cp .env.template .env
# Edit .env with your SuperNote email and password
```

### Configuration

1. **Copy environment template**:
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` file** with your SuperNote credentials:
   ```
   SUPERNOTE_EMAIL=your_email@example.com
   SUPERNOTE_PASSWORD=your_password_here
   ```

3. **Optional**: Customize settings in `src/guardian_crossword/config.py`:
   - Retention periods (local/cloud)
   - File limits
   - Download settings

## Usage

### Basic Commands

#### Download Today's Crosswords
```bash
# Using installed command (recommended)
guardian-crossword --today

# Using Python module
python -m guardian_crossword --today
```

#### Download Specific Date
```bash
guardian-crossword --date 2025-01-15
```

#### Download Specific Puzzle Type
```bash
guardian-crossword --date 2025-01-15 --type quick
guardian-crossword --today --type cryptic
```

#### Available Puzzle Types
- `quick` - Quick Crossword (Mon-Sat)
- `cryptic` - Cryptic Crossword (Mon-Fri)
- `quick-cryptic` - Quick-Cryptic Crossword (Sat only)
- `weekend` - Weekend Crossword (Sat only)

### Management Commands

#### Show Storage Information
```bash
guardian-crossword --info
```

#### Clean Up Old Files
```bash
guardian-crossword --cleanup                # Interactive cleanup
guardian-crossword --cleanup --auto-cleanup # Auto-confirm cleanup
guardian-crossword --cleanup --dry-run      # Preview cleanup
```

#### Download Only (Skip Upload)
```bash
guardian-crossword --today --no-upload
```

### Alternative Usage Methods

#### As Python Module
```bash
python -m guardian_crossword --today
python -m guardian_crossword --info
```

#### Development Mode
```bash
# From project root directory
python -m src.guardian_crossword.cli --today
./scripts/guardian-crossword --today
```

## File Storage

- **Local**: `downloads/` directory (30-day retention, max 150 files)
- **SuperNote Cloud**: `Documents/puzzles` (90-day retention, max 400 files)
- **Naming**: `guardian-{type}-{YYYYMMDD}.pdf`

## Configuration

### Environment Variables (`.env`)
```bash
SUPERNOTE_EMAIL=your_email@example.com
SUPERNOTE_PASSWORD=your_password_here
```

### Advanced Configuration
Edit `src/guardian_crossword/config.py` to customize:

- **Retention policies**: How long to keep files locally vs. cloud
- **File limits**: Maximum number of files to store
- **Download settings**: Retry attempts, timeouts, fallback behavior
- **Guardian URLs**: Base URLs and patterns (usually no need to change)

## Troubleshooting

### Common Issues

1. **Authentication failures**: Verify your SuperNote credentials in `.env`
2. **Download failures**: Check internet connection and Guardian website availability
3. **Module not found**: Ensure you've installed the package (`pip install .` or `pip install -e .`)
4. **Permission errors**: Check file permissions in downloads directory

### Getting Help
```bash
guardian-crossword --help
```

## Project Structure

```
guardian-crossword-supernote/
├── src/guardian_crossword/     # Main package
│   ├── __init__.py            # Package metadata
│   ├── __main__.py            # Entry point for python -m
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration settings
│   ├── downloader.py          # Guardian website integration
│   ├── client.py              # SuperNote cloud client
│   └── file_manager.py        # Local file management
├── scripts/                   # Executable scripts
├── tests/                     # Test directory
├── pyproject.toml             # Python packaging configuration
├── requirements.txt           # Dependencies
├── .env.template             # Environment template
└── README.md                 # This file
```

## Dependencies

- **[sncloud](https://pypi.org/project/sncloud/)** (0.2.1) - SuperNote cloud API client
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** (1.1.1) - Environment variable management
- **[requests](https://pypi.org/project/requests/)** (2.32.4) - HTTP library for downloads

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- The Guardian for providing freely accessible crossword PDFs
- SuperNote team for their cloud API
- Python packaging community for modern tooling standards