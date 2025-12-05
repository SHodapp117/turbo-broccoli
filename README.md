# turbo-broccoli

MLS Player Statistics & Roster Analysis Project

## Overview

This project scrapes and analyzes Major League Soccer (MLS) player performance statistics from FBref.com and parses official MLS Club Roster Profile PDFs.

## Features

- **Web Scraper** ([MLS_Stats.py](MLS_Stats.py)): Scrapes player stats from FBref using Selenium
- **PDF Parser** ([parse_roster_pdfs.py](parse_roster_pdfs.py)): Extracts structured roster data from MLS Club Roster Profile PDFs
- **Historical Data**: Maintains datasets for 2023-2025 seasons

## Data Sources

1. **Performance Stats** (via FBref scraper):
   - Standard Stats, Passing, Shooting, Possession
   - Defensive Actions, Goal/Shot Creation, Performance, Goalkeeping

2. **Roster Data** (via PDF parser):
   - Player names, designations (DP, U22, TAM, Homegrown)
   - Contract years, option years, current status
   - Team roster construction model, GAM available

3. **Salary Data**: `mls_salaries_all_classified.csv` (2,779 rows)

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Scraping FBref Stats

```bash
# Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Navigate to https://fbref.com/en/comps/22/stats/Major-League-Soccer-Stats
# Click "Show" to reveal the Player Standard Stats table

# Run the scraper
python MLS_Stats.py
```

### Parsing Roster PDFs

```bash
# Place Club Roster Profile PDFs in the data/ directory
python parse_roster_pdfs.py
```

**Output Files:**
- `data/2024_roster_profiles_parsed.csv` (866 players, 27 teams)
- `data/2025_roster_profiles_parsed.csv` (875 players, 29 teams)

**Columns:**
- team, name, roster_designation, current_status
- contract_thru, option_years, category
- roster_model, team_gam_2025

## Project Structure

```
turbo-broccoli/
├── MLS_Stats.py              # FBref web scraper
├── parse_roster_pdfs.py      # PDF roster parser
├── 2023_PayData.py          # (Empty - future salary analysis)
├── requirements.txt          # Python dependencies
├── data/                     # CSV data directory
│   ├── 2023_*.csv           # 2023 season stats (8 files)
│   ├── 2024_*.csv           # 2024 season stats (8 files)
│   ├── 2025_*.csv           # 2025 season stats (7 files)
│   ├── mls_salaries_all_classified.csv
│   ├── 2024_roster_profiles_parsed.csv
│   └── 2025_roster_profiles_parsed.csv
└── venv/                     # Virtual environment
```

## Dependencies

- **Web Scraping**: selenium, beautifulsoup4, requests, lxml, html5lib
- **Data Processing**: pandas, numpy
- **PDF Parsing**: pdfplumber
- **Utilities**: python-dateutil, pytz, python-dotenv

## Statistics Summary (2025 Roster)

- **Total Teams**: 29 MLS clubs
- **Total Players**: 875
- **Designated Players**: 68
- **U22 Initiative Players**: 69
- **TAM Players**: 162
- **Homegrown Players**: 157
- **Generation Adidas**: 7

## Author

Spencer Hodapp (spencerhodapp@outlook.com)

## Repository

https://github.com/SHodapp117/turbo-broccoli.git