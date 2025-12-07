# MLS Free Agent Contract Valuator

A Streamlit web application for analyzing and valuing 2026 MLS free agents using statistical peer comparison and machine learning.

## Features

- **Free Agent Database**: Browse 433 players whose contracts expire in 2025
- **Advanced Filtering**: Filter by team, contract designation, and option status
- **Contract Valuation**: Get recommended salary based on peer comparison using K-Nearest Neighbors
- **Peer Analysis**: See statistical peers and their salaries
- **Radar Charts**: Visual statistical comparison across 5 performance categories (Shooting, Passing, Possession, Defensive, Creation)
- **Interactive Visualizations**: Salary ranges, peer distributions, and tier probabilities
- **Market Comparison**: Compare current salary vs. recommended market value

## Installation

1. Make sure you have the virtual environment activated:
```bash
source venv/bin/activate
```

2. Install required packages (if not already installed):
```bash
pip install streamlit plotly
```

## Running the App

### Generate Free Agents Data (First Time Only)

Before running the app for the first time, generate the free agents dataset:

```bash
python find_free_agents_2026.py
```

This creates `data/free_agents_2026.csv` with all players whose contracts expire in 2025.

### Launch the Streamlit App

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Usage

1. **Filter Free Agents**: Use the sidebar to filter by:
   - Team
   - Contract designation (TAM, Designated Player, Homegrown, etc.)
   - Contract status (with/without team options)

2. **Select a Player**: Choose a free agent from the dropdown menu

3. **View Valuation**: See:
   - Recommended base salary
   - Negotiation range (25th-75th percentile)
   - Peer market range
   - Contract tier prediction
   - Player archetype
   - Statistical peer comparison

4. **Explore Radar Charts**: Compare player performance vs peers across:
   - **Shooting**: Shots/90, accuracy, conversion, xG metrics
   - **Passing**: Accuracy, progressive passes, key passes, xA
   - **Possession**: Touches, dribbles, carries, progressive actions
   - **Defensive**: Tackles, interceptions, blocks, recoveries
   - **Creation**: Shot/goal creation actions, penalty area involvement

5. **Analyze Market Position**: Compare current salary vs. market value to identify underpaid/overpaid players

## Data Sources

- **Player Stats**: 2025 MLS season performance data
- **Contract Info**: 2025 roster profiles with contract expiration dates
- **Salary Data**: MLS Players Association salary database

## Model Details

- **Peer Matching**: K-Nearest Neighbors algorithm based on performance statistics
- **Tier Classification**: Random Forest classifier for contract designation prediction
- **Archetype Clustering**: K-Means clustering for player style identification

## Key Statistics

- 433 total free agents identified for 2026
- 346 players with team options
- 74 TAM players, 17 Designated Players, 62 Homegrown Players
- Data from all 30 MLS teams

## Notable Free Agents

- Lionel Messi (Inter Miami)
- Sergio Busquets (Inter Miami)
- Luis Suárez (Inter Miami)
- Walker Zimmerman (Nashville SC)
- Paul Rothrock (Seattle Sounders)
- And many more...

## Notes

- Players need minimum playing time (900 minutes) for full statistical analysis
- Peer comparisons are position-specific
- Salary recommendations are based on current MLS market conditions
- Team options may allow clubs to retain players beyond 2025
