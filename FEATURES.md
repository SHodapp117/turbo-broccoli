# MLS Free Agent Valuator - Feature Overview

## 🎯 Core Functionality

### 1. Free Agent Database
- **433 players** with contracts expiring in 2025
- Complete roster information including teams, positions, and contract details
- Team option tracking (346 players with options)

### 2. Advanced Filtering System
Filter free agents by:
- **Team**: All 30 MLS teams
- **Contract Designation**:
  - Designated Player (17 players)
  - TAM Player (74 players)
  - Homegrown Player (62 players)
  - U22 Initiative (16 players)
  - Generation adidas (4 players)
  - Standard contracts
- **Option Status**:
  - All players
  - With team options (346)
  - No options (87 true free agents)

### 3. Contract Valuation Engine
Uses K-Nearest Neighbors algorithm to:
- Find 10 most statistically similar players
- Calculate recommended base salary
- Provide negotiation range (25th-75th percentile)
- Show peer market range (min-max)
- Predict contract tier with confidence scores

### 4. Statistical Peer Comparison

#### Radar Charts (5 Categories)
Visual percentile-based comparison showing how players rank vs their peers:

**🎯 Shooting Performance**
- Shots per 90 minutes
- Shot accuracy (SoT%)
- Goal conversion rate (G/Sh)
- Non-penalty xG per shot
- Expected goals (xG)

**⚽ Passing Ability**
- Overall pass accuracy
- Progressive passes
- Key passes
- Expected assists (xA)
- Medium pass completion rate

**🏃 Possession Skills**
- Touches per game
- Dribble success rate
- Total carries
- Progressive carries
- Carries into penalty area

**🛡️ Defensive Actions**
- Tackles + Interceptions
- Tackle success rate
- Blocks
- Interceptions
- Ball recoveries

**🎨 Chance Creation**
- Shot creating actions per 90
- Goal creating actions per 90
- Expected assisted goals (xAG)
- Passes to penalty area
- Crosses to penalty area

#### How Radar Charts Work
- **Black line**: Selected player's performance
- **Grey shaded area**: Average peer performance (50th percentile)
- **Values**: Percentile rank within peer group (0-100)
  - 100th percentile = best in peer group
  - 50th percentile = average peer
  - 0th percentile = lowest in peer group

### 5. Market Analysis Tools

#### Salary Visualizations
- **Range Chart**: Visual comparison of peer range, negotiation range, and recommended salary
- **Current vs Market**: Delta showing under/overpayment
- **Histogram**: Distribution of peer salaries with markers for recommended and current

#### Contract Tier Prediction
- Random Forest classification
- Position-specific models
- Confidence scores for each tier
- Visual probability breakdown

### 6. Player Profiling

#### Archetype Classification
- K-Means clustering by position
- Identifies "Elite/Specialist" outliers
- Standard archetypes for typical players
- Based on comprehensive performance metrics

#### Player Info Display
- Position and playing time
- Current contract details
- Team option information
- Salary data (when available)

## 📊 Data Pipeline

### Input Data Sources
1. **2025 Season Stats** (data/processed/2025_all_stats.csv)
   - Standard stats, shooting, passing, possession
   - Defensive actions, goal/shot creation
   - 685 players with 270+ minutes

2. **Roster Profiles** (data/2025_roster_profiles_parsed.csv)
   - Contract expiration dates
   - Team options
   - Designation categories

3. **Salary Database** (data/mls_salaries_all_classified.csv)
   - Base salary and compensation
   - Historical data
   - Classification by tier

### Processing Steps
1. Load and merge all data sources
2. Filter to 2026 free agents (contract_thru contains '2025')
3. Train position-specific models (900+ minute minimum)
4. Generate player archetypes via clustering
5. Calculate peer similarities using KNN

## 🎨 User Interface

### Layout Structure
1. **Header**: Metrics dashboard showing total FAs, filtered results, options
2. **Sidebar**: Filters and about information
3. **Player Selection**: Searchable dropdown with formatted display
4. **Valuation Results**:
   - Player info header (position, minutes, tier)
   - Contract recommendation section
   - Salary comparison visualizations
   - Peer list and statistics
   - **Radar charts** (tabbed interface)
   - Salary distribution
   - Tier confidence breakdown
5. **Footer**: Complete free agent table with current filters

### Interactive Elements
- Dynamic filtering with instant updates
- Tabbed radar charts for easy category switching
- Hover tooltips on all visualizations
- Sortable data tables
- Responsive layout for all screen sizes

## 🔧 Technical Stack

- **Frontend**: Streamlit 1.52+
- **Visualization**: Plotly (charts), Plotly Express (histograms)
- **ML Models**: scikit-learn (RandomForest, KNN, StandardScaler)
- **Data Processing**: pandas, numpy
- **Caching**: Streamlit resource/data caching for performance

## 📈 Performance Features

- Cached model training (runs once)
- Cached free agent data loading
- Efficient KNN queries
- Pre-computed archetypes
- Optimized dataframe operations

## 🎯 Use Cases

### For General Managers
- Identify undervalued free agents
- Set fair contract offers
- Compare players across teams
- Evaluate team options

### For Scouts
- Find statistical peers
- Profile player strengths/weaknesses
- Compare across positions
- Identify value opportunities

### For Analysts
- Market analysis
- Salary benchmarking
- Performance profiling
- Peer group analysis

### For Fans
- Understand player value
- Compare favorites
- Explore free agent market
- Learn statistical profiles

## 🚀 Future Enhancement Opportunities

- Add player images/photos
- Historical contract tracking
- Multi-year projections
- Age curve adjustments
- Injury history integration
- International player comparisons
- Export reports to PDF
- Save favorite players
- Compare multiple players side-by-side
