# Quick Start Guide

## Launch the App (Easiest Method)

Simply run:
```bash
./run_app.sh
```

This will:
1. Activate the virtual environment
2. Check/generate free agents data if needed
3. Launch the Streamlit app in your browser

## Manual Launch

If you prefer to run manually:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Generate free agents data (first time only)
python find_free_agents_2026.py

# 3. Launch the app
streamlit run app.py
```

## Using the App

### 1. Filter Free Agents (Sidebar)
- **Team**: Select a specific team or "All Teams"
- **Contract Designation**: Filter by TAM, DP, Homegrown, etc.
- **Contract Status**: Show all, only players with options, or only without options

### 2. Select a Player
- Choose from the dropdown (shows team and designation)
- Players are listed from your filtered results

### 3. View Contract Valuation
The app will display:
- **Recommended Base Salary**: Fair market value based on peer comparison
- **Negotiation Range**: 25th-75th percentile of peer salaries
- **Peer Market Range**: Min-max salary range of similar players
- **Contract Tier**: Predicted designation (TAM, DP, etc.)
- **Player Archetype**: Statistical cluster or "Elite/Specialist"
- **Current vs Market Value**: Comparison if salary data available

### 4. Analyze Peers
- See the 10 most statistically similar players
- Compare their salaries
- View detailed **radar charts** comparing player vs peers across:
  - Shooting performance
  - Passing ability
  - Possession skills
  - Defensive actions
  - Chance creation
- View salary distribution charts

## Example Use Cases

### Find Undervalued Free Agents
1. Filter: "No Team Option"
2. Look for players where Market Value > Current Salary
3. Review their statistical peers

### Evaluate Team Options
1. Filter by your team: "SEATTLE SOUNDERS FC"
2. Filter: "With Team Option"
3. See which players are worth exercising options on

### Scout Comparable Players
1. Select a player you're interested in
2. Review their statistical peers
3. Identify similar players from other teams

## Key Features

✅ **433 Free Agents** - All players with contracts expiring 2025
✅ **Smart Filtering** - By team, designation, and option status
✅ **K-NN Algorithm** - Finds statistically similar players
✅ **Market Analysis** - Compare current vs recommended salary
✅ **Radar Charts** - Visual comparison across 5 statistical categories
✅ **Visual Charts** - Salary ranges and distributions
✅ **Peer Comparison** - See similar players and their contracts

## Tips

- Players need 900+ minutes for full statistical analysis
- Peer comparisons are position-specific
- Team options allow clubs to extend contracts
- Salary recommendations reflect current MLS market
- Archetype "Elite/Specialist" means unique statistical profile

## Troubleshooting

**"Free agents data not found"**
- Run: `python find_free_agents_2026.py`

**"Error: Player not found"**
- Player may not have enough playing time (< 900 minutes)
- Try filtering by different criteria

**App won't start**
- Make sure virtual environment is activated
- Check that streamlit is installed: `pip install streamlit plotly`

## Need Help?

Check the full documentation in [README_APP.md](README_APP.md)
