# Guardian Crossword URLs and Scheduling

## Guardian

### URL Structure
- **Base URL**: `https://crosswords-static.guim.co.uk/gdn.{puzzle_type}.{date_str}.pdf`

### Date Format
- Uses `YYYYMMDD` format (e.g., `20250716` for July 16, 2025)
- Generated using: `date.strftime('%Y%m%d')`

### Puzzle Types & Availability

#### Quick Crossword
- **Type**: `quick`
- **Availability**: Monday-Saturday (weekdays + Saturday)
- **Days**: Monday=0 to Saturday=5
- **URL Example**: `https://crosswords-static.guim.co.uk/gdn.quick.20250716.pdf`

#### Cryptic Crossword
- **Type**: `cryptic`
- **Availability**: Monday-Friday (weekdays only)
- **Days**: Monday=0 to Friday=4
- **URL Example**: `https://crosswords-static.guim.co.uk/gdn.cryptic.20250716.pdf`

#### Quick-Cryptic Crossword
- **Type**: `quick-cryptic`
- **Availability**: Saturday only
- **Days**: Saturday=5
- **URL Example**: `https://crosswords-static.guim.co.uk/gdn.quick-cryptic.20250716.pdf`

#### Weekend Crossword
- **Type**: `weekend`
- **Availability**: Saturday only
- **Days**: Saturday=5
- **URL Example**: `https://crosswords-static.guim.co.uk/gdn.weekend.20250716.pdf`

### Implementation Details
- Saves as: `guardian-{puzzle_type}-{YYYYMMDD}.pdf`
- Falls back to previous available days if current day's puzzle isn't available
- Tries up to 3 previous available days for each puzzle type

## Scheduling Configuration

### Default Schedule (config.yaml)
```yaml
crosswords:
  schedule:
    monday: ['guardian-quick', 'guardian-cryptic']
    tuesday: ['guardian-quick', 'guardian-cryptic']
    wednesday: ['guardian-quick', 'guardian-cryptic']
    thursday: ['guardian-quick', 'guardian-cryptic']
    friday: ['guardian-quick', 'guardian-cryptic']
    saturday: ['guardian-quick', 'guardian-quick-cryptic', 'guardian-weekend']
    sunday: []
  enabled: ['guardian-quick', 'guardian-cryptic', 'guardian-quick-cryptic', 'guardian-weekend']

timing:
  timezone: 'Australia/Sydney'
  preferred_download_time: '09:30'
```

### Scheduling Logic
- Uses timezone-aware datetime: `datetime.datetime.now(tz)`
- Filters scheduled crosswords by enabled ones
- Default behavior uses scheduled mode if no specific type is requested
- Fallback hierarchy: quick � quick-cryptic � weekend � cryptic

### Publication Times
- **Guardian Quick**: Monday-Saturday
- **Guardian Cryptic**: Monday-Friday
- **Guardian Quick-Cryptic**: Saturday only
- **Guardian Weekend**: Saturday only

### Download Strategy
- Tries current day first if puzzle type is available
- Falls back to most recent available day if current day doesn't have the puzzle
- Attempts up to 3 previous available days before giving up
- For Saturday-only puzzles, goes back to previous Saturdays (7 days back)