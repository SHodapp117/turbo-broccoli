# turbo-broccoli

MLS Player Statistics, Roster Analysis & Free Agent Valuation System

## Overview

This project scrapes and analyzes Major League Soccer (MLS) player performance statistics from FBref.com, parses official MLS Club Roster Profile PDFs, and provides an interactive web application for valuing free agents using machine learning.

## Features

### Data Collection & Processing
- **Web Scraper** ([MLS_Stats.py](MLS_Stats.py)): Scrapes player stats from FBref using Selenium
- **PDF Parser** ([parse_roster_pdfs.py](parse_roster_pdfs.py)): Extracts structured roster data from MLS Club Roster Profile PDFs
- **Stats Processor** ([Stats_Processor.py](Stats_Processor.py)): Consolidates stats from multiple categories into unified dataframes
- **SCD2 Storage** ([SCD2_Storage.py](SCD2_Storage.py)): Memory-efficient storage with SCD Type 2 pattern for S3 and ML workflows
- **Player Clustering** ([Player_Clustering.py](Player_Clustering.py)): DBSCAN clustering to discover player archetypes

### Machine Learning & Valuation
- **Player Valuation System** ([Player_Valuation.py](Player_Valuation.py)): ML-based player contract valuation using K-NN peer comparison and Random Forest classification
- **Free Agent Analyzer** ([find_free_agents_2026.py](find_free_agents_2026.py)): Identifies all 2026 free agents from roster data
- **Contract Valuator App** ([app.py](app.py)): Interactive Streamlit web application for analyzing and valuing free agents

### Historical Data
- Maintains comprehensive datasets for 2023-2025 seasons
- Tracks 433 free agents for 2026 season

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

### Processing Stats Data

```bash
# Consolidate all stats categories into unified dataframes
python Stats_Processor.py
```

**Output Files:**
- `data/processed/2023_all_stats.csv` (855 players, 197 columns)
- `data/processed/2024_all_stats.csv` (819 players, 197 columns)
- `data/processed/2025_all_stats.csv` (882 players, 197 columns)
- `data/processed/all_seasons_combined.csv` (2,556 total records)

**Combines these stat categories:**
- Standard (Goals, Assists, Cards, Minutes, xG)
- Passing (Completion %, Progressive Passes, Key Passes)
- Shooting (Shots, Shots on Target, Conversion Rate)
- Possession (Touches, Dribbles, Carries)
- Defensive Actions (Tackles, Blocks, Interceptions)
- Goal/Shot Creation (Shot-Creating Actions, Goal-Creating Actions)
- Performance (Box-level performance metrics)
- Goalkeeping (Saves, Clean Sheets, PSxG)

### Creating SCD2 Storage (S3 & ML Ready)

```bash
# Create memory-efficient SCD Type 2 structure with Parquet format
python SCD2_Storage.py
```

**Output Structure:**
- `data/scd2/parquet/player_dimension.parquet` (56 KB - SCD2 temporal tracking)
- `data/scd2/parquet/stats_fact/season=YYYY/` (1.3 MB - Partitioned by season)
- `data/scd2/ml_current_season_2025.parquet` (467 KB - ML-ready denormalized view)
- `data/scd2/ml_timeseries_all_seasons.parquet` (850 KB - Time series features)

**Benefits:**
- **3.6x compression** (Parquet vs in-memory)
- **Columnar storage** for efficient ML feature loading
- **SCD Type 2** tracks player changes over time (team transfers, position changes)
- **S3-optimized** with partitioning for cost-effective queries
- **ML-ready** pre-built views for training

See [ML_WORKFLOW.md](ML_WORKFLOW.md) for detailed ML usage examples.

### Player Clustering (DBSCAN)

```bash
# Discover player archetypes using density-based clustering
python Player_Clustering.py
```

**Output:**
- `data/clustering/clustered_players_2025.csv` (669 players with cluster assignments)
- `data/clustering/clusters_outfield.png` (Visualization: all outfield players)
- `data/clustering/clusters_forwards.png` (Visualization: forwards only)
- `data/clustering/clusters_midfielders.png` (Visualization: midfielders only)
- `data/clustering/eps_optimization.png` (Parameter tuning graph)

**Results:**
- **1 major cluster** (82.7% - "typical" MLS players)
- **116 outliers** (17.3% - elite performers and specialists)
- **37.7% of Designated Players** are statistical outliers
- Position-specific clustering reveals archetype patterns

See [CLUSTERING_ANALYSIS.md](CLUSTERING_ANALYSIS.md) for detailed results and insights.

### Free Agent Valuation System

```bash
# 1. Generate free agents list
python find_free_agents_2026.py

# 2. Launch the interactive web application
streamlit run app.py
```

**The Streamlit app provides:**
- **433 Free Agents** with contracts expiring in 2025
- **Advanced Filtering** by team, position, designation, and option status
- **ML-Powered Valuations** using K-Nearest Neighbors and Random Forest
- **Contract Recommendations** including base salary and negotiation ranges
- **Statistical Peer Comparison** with 10 most similar players
- **Radar Charts** comparing performance across 5 categories (or 4 for goalkeepers)
- **Market Analysis** showing under/overpaid players
- **Automatic Name Mapping** handles 400+ player name variations

**Output:**
- `data/free_agents_2026.csv` (433 free agents with roster details)
- `data/player_name_mapping.json` (400 mapped names for stats lookup)
- Interactive web UI at `http://localhost:8501`

**Key Features:**
- Position-specific models (FW, MF, DF, GK)
- Goalkeeper-specific radar charts (Shot Stopping, Distribution, Sweeping, Passing Under Pressure)
- Outfield player radar charts (Shooting, Passing, Possession, Defensive, Creation)
- Dynamic filtering with real-time updates
- Contract tier predictions with confidence scores
- Player archetype classification

See [README_APP.md](README_APP.md), [QUICKSTART.md](QUICKSTART.md), and [FEATURES.md](FEATURES.md) for detailed app documentation.

## Project Structure

```
turbo-broccoli/
├── MLS_Stats.py                  # FBref web scraper
├── parse_roster_pdfs.py          # PDF roster parser
├── Stats_Processor.py            # Stats consolidation processor
├── SCD2_Storage.py               # SCD Type 2 storage manager
├── Player_Clustering.py          # DBSCAN clustering analysis
├── Player_Valuation.py           # ML-based contract valuation system
├── find_free_agents_2026.py      # Free agent identifier
├── app.py                        # Streamlit web application
├── Contract_Valuation.py         # Contract tier classification (legacy)
├── value_rothrock.py             # Single player valuation example
├── ML_WORKFLOW.md                # ML usage guide
├── CLUSTERING_ANALYSIS.md        # Clustering results & insights
├── README_APP.md                 # Web app documentation
├── QUICKSTART.md                 # Quick start guide for app
├── FEATURES.md                   # Detailed feature list
├── FILTERING_GUIDE.md            # App filtering documentation
├── requirements.txt              # Python dependencies
├── data/                     # CSV data directory
│   ├── 2023_*.csv           # 2023 season stats (8 files)
│   ├── 2024_*.csv           # 2024 season stats (8 files)
│   ├── 2025_*.csv           # 2025 season stats (7 files)
│   ├── mls_salaries_all_classified.csv
│   ├── 2024_roster_profiles_parsed.csv
│   ├── 2025_roster_profiles_parsed.csv
│   ├── free_agents_2026.csv          # 433 free agents for 2026
│   ├── player_name_mapping.json      # Name mapping for stats lookup
│   ├── processed/           # Processed unified stats
│   │   ├── 2023_all_stats.csv
│   │   ├── 2024_all_stats.csv
│   │   ├── 2025_all_stats.csv
│   │   └── all_seasons_combined.csv
│   ├── scd2/                # SCD2 optimized storage
│   │   ├── parquet/
│   │   │   ├── player_dimension.parquet
│   │   │   └── stats_fact/
│   │   │       ├── season=2023/
│   │   │       ├── season=2024/
│   │   │       └── season=2025/
│   │   ├── ml_current_season_2025.parquet
│   │   └── ml_timeseries_all_seasons.parquet
│   └── clustering/          # Clustering analysis
│       ├── clustered_players_2025.csv
│       ├── clusters_outfield.png
│       ├── clusters_forwards.png
│       ├── clusters_midfielders.png
│       └── eps_optimization.png
└── venv/                     # Virtual environment
```

## Dependencies

- **Web Scraping**: selenium, beautifulsoup4, requests, lxml, html5lib
- **Data Processing**: pandas, numpy
- **PDF Parsing**: pdfplumber
- **Storage & ML**: pyarrow (Parquet format), scikit-learn
- **Visualization**: matplotlib, seaborn
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