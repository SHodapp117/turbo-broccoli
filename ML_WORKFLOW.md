# MLS Stats ML Workflow Guide

## Storage Architecture Overview

### SCD Type 2 Structure

**Why SCD2?**
- Tracks player changes over time (team transfers, position changes)
- Preserves historical context for time-series ML models
- Efficient storage with dimension/fact separation

**Structure:**
```
data/scd2/
├── parquet/                          # Optimized for S3 & ML
│   ├── player_dimension.parquet      # 56 KB - Player attributes with temporal tracking
│   └── stats_fact/                   # 1.3 MB - Partitioned by season
│       ├── season=2023/
│       ├── season=2024/
│       └── season=2025/
├── player_dimension.csv.gz           # 44 KB - Backup/compatibility
├── stats_fact.csv.gz                 # 443 KB
├── ml_current_season_2025.parquet    # 467 KB - Ready for training
└── ml_timeseries_all_seasons.parquet # 850 KB - Time series features
```

### Memory Efficiency Achieved

| Format | Size | Compression Ratio |
|--------|------|-------------------|
| In-Memory (full load) | 4.80 MB | Baseline |
| Parquet (on disk) | 1.33 MB | **3.6x** |
| CSV gzipped | 0.48 MB | **10x** |

**Key Benefits:**
- **3.6x compression** with Parquet (columnar format)
- **Columnar storage** = load only needed features for ML
- **Partitioning** = query by season without loading all data
- **Schema evolution** = add new stats without breaking existing pipelines

## ML Workflow Examples

### 1. Quick Start: Load Current Season for Training

```python
import pandas as pd

# Load pre-built ML view (denormalized, ready to use)
df = pd.read_parquet('data/scd2/ml_current_season_2025.parquet')

# All player stats + attributes in one table
print(df.columns)
# ['player_sk', 'version', 'Season', 'Goals', 'Assists', 'xG',
#  'Player', 'Pos', 'Squad', 'Age', ...]

# Example: Predict goals from other stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

features = ['Assists', 'xG', 'Minutes', 'Age']
X = df[features].fillna(0)
y = df['Goals']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor()
model.fit(X_train, y_train)
print(f"R² Score: {model.score(X_test, y_test)}")
```

### 2. Memory-Efficient: Load Only Needed Columns

```python
import pyarrow.parquet as pq

# Read only specific columns (columnar format benefit)
columns = ['player_sk', 'Season', 'Goals', 'Assists', 'xG', 'Minutes']

# Load from partitioned fact table
df_2025 = pd.read_parquet(
    'data/scd2/parquet/stats_fact/season=2025/data.parquet',
    columns=columns
)

# Memory usage: ~200 KB instead of 467 KB (56% reduction)
print(f"Memory: {df_2025.memory_usage().sum() / 1024:.1f} KB")
```

### 3. Time Series: Player Performance Trends

```python
# Load historical data for time series modeling
df_ts = pd.read_parquet('data/scd2/ml_timeseries_all_seasons.parquet')

# Get player's performance across seasons
player_history = df_ts[df_ts['Player'] == 'Lionel Messi'].sort_values('Season')

# Calculate rolling averages, trends
player_history['goals_ma'] = player_history['Goals'].rolling(2).mean()
player_history['improving'] = player_history['Goals'].diff() > 0

# Predict next season's performance
# ... (ARIMA, LSTM, Prophet, etc.)
```

### 4. Join Dimension & Fact (For Custom Queries)

```python
# Load dimension and fact separately (normalized storage)
player_dim = pd.read_parquet('data/scd2/parquet/player_dimension.parquet')
stats_2025 = pd.read_parquet('data/scd2/parquet/stats_fact/season=2025/data.parquet')

# Join on demand
current_players = player_dim[player_dim['is_current'] == True]
df = stats_2025.merge(
    current_players[['player_sk', 'Player', 'Squad', 'Pos']],
    on='player_sk'
)

# Query: Top goal scorers by position
top_by_pos = df.groupby('Pos')['Goals'].nlargest(5)
```

### 5. Larger-Than-Memory: Use Dask

```python
import dask.dataframe as dd

# For huge datasets, use Dask (lazy loading)
df_dask = dd.read_parquet('data/scd2/parquet/stats_fact/season=*/data.parquet')

# Compute aggregations without loading all into memory
avg_goals_by_team = df_dask.groupby('Squad')['Goals'].mean().compute()
```

## S3 Deployment Strategy

### Upload to S3

```bash
# Install AWS CLI
pip install awscli

# Upload with server-side encryption
aws s3 sync data/scd2/parquet/ s3://your-bucket/mls-stats/parquet/ \
    --storage-class STANDARD \
    --metadata-directive REPLACE \
    --sse AES256

# Lifecycle policy (optional): Archive old seasons
aws s3api put-bucket-lifecycle-configuration \
    --bucket your-bucket \
    --lifecycle-configuration file://lifecycle.json
```

**lifecycle.json:**
```json
{
  "Rules": [
    {
      "Id": "Archive-Old-Seasons",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "mls-stats/parquet/stats_fact/season=2023/"
      },
      "Transitions": [
        {
          "Days": 365,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

### Query from S3 (AWS Athena)

```sql
-- 1. Create Glue/Athena table from S3 Parquet
CREATE EXTERNAL TABLE mls_stats (
    player_sk BIGINT,
    version INT,
    season INT,
    goals DOUBLE,
    assists DOUBLE,
    xg DOUBLE
    -- ... other columns
)
PARTITIONED BY (season INT)
STORED AS PARQUET
LOCATION 's3://your-bucket/mls-stats/parquet/stats_fact/'
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- 2. Add partitions
MSCK REPAIR TABLE mls_stats;

-- 3. Query (only scans needed partition)
SELECT player_sk, SUM(goals) as total_goals
FROM mls_stats
WHERE season = 2025
GROUP BY player_sk
ORDER BY total_goals DESC
LIMIT 10;
```

### Load into SageMaker

```python
import sagemaker
import boto3

# Direct S3 read with PyArrow
s3 = boto3.client('s3')
df = pd.read_parquet('s3://your-bucket/mls-stats/parquet/stats_fact/season=2025/data.parquet')

# Or use SageMaker Data Wrangler
from sagemaker.feature_store.feature_group import FeatureGroup

# Create feature store from Parquet
fg = FeatureGroup(name='mls-player-stats', sagemaker_session=sagemaker_session)
fg.ingest(data_frame=df, max_workers=3, wait=True)
```

## ML Use Cases

### 1. Player Valuation Model

**Goal:** Predict fair market value based on performance stats

```python
# Features: Goals, Assists, Age, Minutes, Position, Team strength
# Target: Salary (from mls_salaries_all_classified.csv)

df_stats = pd.read_parquet('data/scd2/ml_current_season_2025.parquet')
df_salary = pd.read_csv('data/mls_salaries_all_classified.csv')

# Join stats with salary
df_ml = df_stats.merge(df_salary, left_on='Player', right_on='player_name')

# Model: XGBoost regression
from xgboost import XGBRegressor
# ... training code
```

### 2. Goal Prediction (Classification)

**Goal:** Predict if player will score 10+ goals next season

```python
# Historical data for training
df_ts = pd.read_parquet('data/scd2/ml_timeseries_all_seasons.parquet')

# Feature engineering: previous season stats
df_ts['goals_next_season'] = df_ts.groupby('player_sk')['Goals'].shift(-1)
df_ts['will_score_10_plus'] = (df_ts['goals_next_season'] >= 10).astype(int)

# Features: Current season stats
# Target: will_score_10_plus
```

### 3. Transfer Prediction

**Goal:** Predict if player will change teams

```python
# SCD2 dimension tracks team changes
player_dim = pd.read_parquet('data/scd2/parquet/player_dimension.parquet')

# Count team changes per player
transfers = player_dim.groupby('player_sk').agg({
    'Squad': 'nunique',
    'version': 'max'
}).rename(columns={'Squad': 'num_teams'})

# Feature: Players with multiple versions likely to transfer
df_ml['transfer_risk'] = transfers['num_teams'] > 1
```

### 4. Position Clustering

**Goal:** Discover player archetypes based on stats

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

df = pd.read_parquet('data/scd2/ml_current_season_2025.parquet')

# Select stat features
stat_cols = ['Goals', 'Assists', 'xG', 'Tackles', 'Passes', 'Dribbles']
X = df[stat_cols].fillna(0)

# Standardize and cluster
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=5, random_state=42)
df['cluster'] = kmeans.fit_predict(X_scaled)

# Analyze clusters (e.g., "Goal Scorers", "Playmakers", "Defenders")
print(df.groupby('cluster')[stat_cols].mean())
```

## Feature Engineering Patterns

### Rolling Statistics

```python
df_ts = pd.read_parquet('data/scd2/ml_timeseries_all_seasons.parquet')

# Per-player rolling stats
df_ts = df_ts.sort_values(['player_sk', 'Season'])
df_ts['goals_rolling_avg'] = df_ts.groupby('player_sk')['Goals'].transform(
    lambda x: x.rolling(2, min_periods=1).mean()
)
```

### Year-over-Year Change

```python
df_ts['goals_yoy_change'] = df_ts.groupby('player_sk')['Goals'].diff()
df_ts['is_improving'] = df_ts['goals_yoy_change'] > 0
```

### Aggregate Team Stats

```python
# Team offensive strength
team_offense = df.groupby('Squad').agg({
    'Goals': 'sum',
    'xG': 'sum'
}).rename(columns={'Goals': 'team_goals'})

df = df.merge(team_offense, on='Squad')
df['pct_team_goals'] = df['Goals'] / df['team_goals']
```

## Best Practices

### 1. Memory Efficiency
- ✅ Use Parquet for columnar access (load only needed features)
- ✅ Filter partitions before loading (e.g., `season=2025`)
- ✅ Use `columns` parameter in `read_parquet()`
- ✅ Downcasting: `pd.to_numeric(downcast='float')`
- ❌ Avoid loading entire CSV into memory

### 2. S3 Cost Optimization
- ✅ Partition by time (season, month)
- ✅ Compress with Snappy (good compression + fast reads)
- ✅ Use Lifecycle policies (archive old data to Glacier)
- ✅ Athena queries scan only needed partitions
- ❌ Don't create too many small files (<128 MB ideal)

### 3. Reproducibility
- ✅ Version datasets (e.g., `v1/`, `v2/` in S3)
- ✅ Log feature engineering in MLflow/Weights&Biases
- ✅ Save preprocessing pipelines with `joblib.dump(scaler, 'scaler.pkl')`
- ✅ Use SCD2 effective dates for point-in-time training data

### 4. Model Deployment
- ✅ Use ML-optimized views for inference (denormalized)
- ✅ Cache frequently used data in Redis/DynamoDB
- ✅ API: Load from S3, predict, return result
- ✅ Batch predictions: Use Athena to filter new players, predict in bulk

## Summary

**SCD2 + Parquet** gives you:
1. **3.6x compression** (1.3 MB vs 4.8 MB in memory)
2. **Fast ML training** (load only needed columns)
3. **Historical tracking** (temporal player changes)
4. **S3-ready** (partitioned, compressed, queryable)
5. **Scalable** (Dask/Athena for larger datasets)

Your data is now optimized for both **storage efficiency** and **ML performance**!
