# MLS Player Clustering Analysis (DBSCAN)

## Overview

Used **DBSCAN (Density-Based Spatial Clustering)** to discover natural player archetypes in MLS based on performance statistics, position, and roster designation.

**Key Results:**
- **669 outfield players** analyzed (270+ minutes played in 2025)
- **1 major cluster** + **116 outliers** discovered
- **37.7% of Designated Players** are statistical outliers
- Clustering correlates strongly with roster designation tiers

---

## Why DBSCAN?

### Advantages over K-Means

| Feature | DBSCAN | K-Means |
|---------|--------|---------|
| Number of clusters | Auto-discovered | Must specify K |
| Outlier detection | Built-in (noise points) | No outlier detection |
| Cluster shape | Arbitrary shapes | Spherical only |
| Cluster size | Variable | Similar sizes |

### Perfect for MLS Players

1. **No need to guess cluster count** - Lets data reveal natural groupings
2. **Identifies superstars** - Messi, Busquets, etc. flagged as outliers
3. **Handles roster tiers** - DP vs TAM vs Standard have different density
4. **Position flexibility** - Hybrid positions (FW,MF) handled naturally

---

## Results Summary

### All Outfield Players (669 total)

| Group | Count | % | Avg Goals | Avg Assists | Avg Minutes | Top Positions |
|-------|-------|---|-----------|-------------|-------------|---------------|
| **Cluster 0** (Typical) | 553 | 82.7% | 0.10 | 0.08 | 1,445 | DF, MF, FW,MF |
| **Outliers** (Elite/Specialist) | 116 | 17.3% | 0.38 | 0.24 | 1,154 | MF,FW, FW,MF, FW |

#### Cluster 0: "Workhorses"
- **Characteristics**: Lower production stats, higher minutes
- **Composition**: 40% Defenders, 35% Standard designation
- **Interpretation**: Typical MLS players - consistent contributors
- **Examples**: Most defenders, rotational midfielders

#### Outliers: "Game Changers"
- **Characteristics**: Higher goals/assists despite fewer minutes
- **Composition**: 71% attacking players (FW/MF hybrids), 20% Designated Players
- **Interpretation**: Elite performers with unique statistical profiles
- **Examples**: Jordi Alba, Denis Bouanga, Sergio Busquets, Lionel Messi

---

### Forwards Only (256 total)

| Group | Count | % | Avg Goals | Avg Assists | Top Designation |
|-------|-------|---|-----------|-------------|-----------------|
| **Cluster 0** | 210 | 82.0% | 0.26 | 0.16 | Designated Player (48) |
| **Outliers** | 46 | 18.0% | 0.42 | 0.23 | Standard (9) |

**Top Forwards in Cluster 0:**
- Lionel Messi (Inter Miami) - 1.1 G, 0.6 A
- Brian White (Vancouver) - 0.9 G, 0.1 A
- Denis Bouanga (LAFC) - 0.8 G, 0.2 A

**Insight**: Even among forwards, DBSCAN identifies a "typical" striker cluster and separates elite/specialist forwards.

---

### Midfielders Only (355 total)

| Group | Count | % | Avg Goals | Avg Assists | Top Positions |
|-------|-------|---|-----------|-------------|---------------|
| **Cluster 0** | 288 | 81.1% | 0.13 | 0.12 | MF, FW,MF, MF,FW |
| **Outliers** | 67 | 18.9% | 0.27 | 0.20 | FW,MF, MF,FW, MF |

**Top Midfielders in Cluster 0:**
- Lionel Messi (Inter Miami) - 1.1 G, 0.6 A
- Evander (FC Cincinnati) - 0.6 G, 0.5 A
- Diego Rossi (Columbus Crew) - 0.6 G, 0.1 A

**Insight**: Attacking midfielders (FW,MF) dominate outliers. Pure midfielders (MF) tend toward typical cluster.

---

## Key Insights

### 1. Roster Designation Strongly Correlates with Outlier Status

| Designation | Outlier % | Interpretation |
|-------------|-----------|----------------|
| **Designated Player** | **37.7%** | Elite tier - many are statistical outliers |
| TAM Player | 17.1% | Above average, some outliers |
| U22 Initiative | 10.2% | Development tier |
| Standard | 10.6% | Baseline performance |

**Finding**: DPs are 3.5x more likely to be outliers than standard roster players.

### 2. Position Influences Outlier Likelihood

**Outlier Composition:**
- 71% are attacking players (FW, MF,FW, FW,MF)
- 29% are defenders/pure midfielders

**Interpretation**:
- Attacking stats (goals, assists) have higher variance
- Defensive stats are more "normalized" across players
- Hybrid positions create unique stat profiles

### 3. DBSCAN Reveals "Specialists"

**Outliers include:**
- **Elite DPs**: Messi, Busquets, Alba - exceptional across all metrics
- **High-variance players**: Few minutes but high goals/90
- **Positional specialists**: Unique role players (e.g., super-subs)

This is valuable for **scouting** and **roster construction** - identifies players who don't fit traditional molds but provide unique value.

---

## Technical Details

### Features Used (Position-Specific)

**All Outfield Players (14 features):**
- `Goals`, `Assists`, `xG`, `npxG`, `xAG`
- `Minutes`, `Sh` (Shots), `SoT` (Shots on Target)
- `Cmp` (Passes Completed), `PrgP` (Progressive Passes), `PrgC` (Progressive Carries)
- `Tkl` (Tackles), `Int` (Interceptions), `Blocks`

**Forwards (15 features):**
- All common features +
- `Gls`, `SoT%`, `G/Sh`, `G/SoT`, `PrgR` (Progressive Runs)

**Midfielders (16 features):**
- All common features +
- `Ast`, `KP` (Key Passes), `PrgP`, `PPA` (Passes into Penalty Area)
- `Cmp%` (Pass Completion %)

### DBSCAN Parameters

**Optimization Method**: K-distance graph (90th percentile)

| Analysis | Eps | Min Samples | Players | Clusters | Outliers |
|----------|-----|-------------|---------|----------|----------|
| All Outfield | 2.21 | 5 | 669 | 1 | 116 (17.3%) |
| Forwards | 2.30 | 4 | 256 | 2 | 46 (18.0%) |
| Midfielders | 2.37 | 4 | 355 | 2 | 67 (18.9%) |

**Preprocessing:**
1. Normalized stats per 90 minutes (fair comparison)
2. StandardScaler (mean=0, std=1)
3. PCA for visualization (2D projection)

### Visualization

**PCA Explained Variance:**
- PC1: ~25-35% of variance
- PC2: ~15-20% of variance
- Total: ~40-50% captured in 2D plots

**Interpretation**: 2D plots show general structure, but full clustering uses all 14-16 dimensions.

---

## Applications

### 1. Scouting & Recruitment

**Find Undervalued Players:**
```python
# Load clustered data
df = pd.read_csv('data/clustering/clustered_players_2025.csv')

# Find "Standard" players who are outliers (hidden gems)
hidden_gems = df[
    (df['cluster'] == -1) &  # Outlier performance
    (df['category'] == 'Standard')  # Not expensive DP/TAM
]

# Sort by goals per minute
hidden_gems['goals_per_min'] = hidden_gems['Goals'] / hidden_gems['Minutes']
top_gems = hidden_gems.nlargest(10, 'goals_per_min')
```

**Output**: Standard roster players with elite statistical profiles → potential bargains

### 2. Roster Construction

**Analyze Team Composition:**
```python
# How many outliers does each team have?
team_outliers = df[df['cluster'] == -1].groupby('Squad').size()

# Top teams by outlier count
print(team_outliers.nlargest(10))
```

**Insight**: Teams with more outliers may have "star-driven" strategies vs. balanced rosters.

### 3. Player Comparison

**Find Similar Players:**
```python
# Get cluster for a specific player
messi_cluster = df[df['Player'] == 'Lionel Messi']['cluster'].values[0]

# If Messi is an outlier, use nearest neighbors
if messi_cluster == -1:
    from sklearn.neighbors import NearestNeighbors

    # Find 5 most similar players
    X = df[features].fillna(0)
    nn = NearestNeighbors(n_neighbors=6)
    nn.fit(X)

    messi_idx = df[df['Player'] == 'Lionel Messi'].index[0]
    distances, indices = nn.kneighbors([X.iloc[messi_idx]])

    similar_players = df.iloc[indices[0][1:]]  # Exclude Messi himself
```

### 4. Contract Valuation

**DP Designation Validation:**
```python
# Are all DPs actually outliers?
dps = df[df['category'] == 'Designated Player']
dp_outlier_rate = (dps['cluster'] == -1).mean()

print(f"DP outlier rate: {dp_outlier_rate:.1%}")
# → 37.7% are outliers

# Which DPs are NOT outliers? (potential overvaluation)
overvalued = dps[dps['cluster'] != -1].sort_values('Goals', ascending=False)
```

---

## Visualizations Generated

### 1. K-Distance Graph (`eps_optimization.png`)
- Shows optimal `eps` parameter
- Elbow in curve = suggested eps value
- Used to auto-tune DBSCAN

### 2. Cluster Scatter Plots
- **`clusters_outfield.png`**: All outfield players (2D PCA projection)
- **`clusters_forwards.png`**: Forward-specific clustering
- **`clusters_midfielders.png`**: Midfielder-specific clustering

**Each plot shows:**
- **Left panel**: Colored by DBSCAN cluster assignment
- **Right panel**: Colored by roster designation (DP, TAM, etc.)
- **Outliers annotated** (if < 20 players)

### 3. Clustered Data CSV (`clustered_players_2025.csv`)
- 716 KB, 669 players
- Includes all original stats + `cluster` column
- Use for further analysis in Excel, Tableau, etc.

---

## Limitations & Future Work

### Current Limitations

1. **Single season analysis** - Doesn't track player evolution over time
2. **Minutes threshold** - Excludes young/backup players (270+ min filter)
3. **Name-based merge** - Roster designation matching could improve with fuzzy matching
4. **2D visualization** - PCA projection loses ~50% of variance

### Future Enhancements

1. **Temporal clustering** - Track cluster membership changes across seasons
   ```python
   # Did player move from Cluster 0 → Outlier after DP signing?
   ```

2. **Hierarchical DBSCAN (HDBSCAN)** - Better handles varying density
3. **Feature importance** - Which stats drive cluster separation?
4. **Team-level clustering** - Cluster entire team rosters
5. **Transfer prediction** - Do outliers get transferred more often?

---

## Conclusion

**DBSCAN successfully identified natural player groupings in MLS:**

1. **One dominant "typical player" cluster** (82.7% of players)
   - Lower production, higher minutes
   - Balanced across positions
   - Represents MLS baseline performance

2. **Elite outliers** (17.3% of players)
   - Higher goals/assists, often in fewer minutes
   - 71% attacking players
   - 37.7% of Designated Players fall here

3. **Strong roster designation correlation**
   - DPs are 3.5x more likely to be outliers than standard players
   - Validates MLS salary structure (paying premium for elite performers)

**Value for Portfolio:**
- Demonstrates unsupervised ML techniques
- Combines multiple data sources (stats + roster)
- Produces actionable insights for scouting/recruitment
- Shows parameter tuning (eps optimization)
- Professional visualizations with interpretation

**Next Steps:**
- Apply to historical seasons (2023-2024)
- Build "player archetype" taxonomy from clusters
- Create interactive dashboard (Streamlit/Plotly)
- Integrate with transfer/salary data for valuation models
