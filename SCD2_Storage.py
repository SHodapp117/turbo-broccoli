"""
SCD Type 2 Storage Strategy for MLS Player Stats

Implements Slowly Changing Dimension Type 2 pattern with memory-efficient
storage formats for S3 and local analysis.

Storage Strategies:
1. Parquet format (60-80% smaller than CSV, column-oriented)
2. Partitioning by season/team for query performance
3. SCD2 temporal tracking with effective dates
4. Separate fact and dimension tables for efficiency
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional
import json


class SCD2StorageManager:
    """
    Manages SCD Type 2 storage of MLS player statistics

    SCD2 Pattern:
    - Each record has effective_date and end_date
    - Current records have end_date = None or '9999-12-31'
    - Historical records preserved with their effective date range
    - Surrogate keys (player_sk) for tracking across changes
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent / 'data'
        else:
            self.data_dir = Path(data_dir)

        self.scd2_dir = self.data_dir / 'scd2'
        self.scd2_dir.mkdir(exist_ok=True)

        # Storage paths
        self.parquet_dir = self.scd2_dir / 'parquet'
        self.parquet_dir.mkdir(exist_ok=True)

    def create_player_dimension(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create player dimension table with SCD2 structure

        This is memory-efficient because player attributes that rarely change
        (name, nation, birth year) are stored separately from stats.

        Args:
            df: Combined stats dataframe

        Returns:
            Player dimension with SCD2 fields
        """
        print("Creating Player Dimension (SCD2)...")

        # Sort by player and season to track changes
        df_sorted = df.sort_values(['Player', 'Season']).copy()

        # Player attributes (slowly changing)
        player_attrs = ['Player', 'Nation', 'Born', 'Pos', 'Squad']

        # Create surrogate key (hash of player + nation + born for uniqueness)
        df_sorted['player_sk'] = (
            df_sorted['Player'].astype(str) + '_' +
            df_sorted['Nation'].astype(str) + '_' +
            df_sorted['Born'].astype(str)
        ).apply(lambda x: abs(hash(x)) % (10 ** 10))

        # Track changes in position or team (SCD2 triggers)
        df_sorted['pos_team_key'] = df_sorted['Pos'].astype(str) + '_' + df_sorted['Squad'].astype(str)

        # Detect changes
        df_sorted['is_changed'] = (
            df_sorted.groupby('player_sk')['pos_team_key']
            .shift(1) != df_sorted['pos_team_key']
        )

        # Create version number for each change
        df_sorted['version'] = df_sorted.groupby('player_sk')['is_changed'].cumsum()

        # Create effective dates based on season
        # Simplified: use season year as effective date
        df_sorted['effective_date'] = pd.to_datetime(df_sorted['Season'].astype(str) + '-01-01')

        # End date is start of next record, or NULL for current
        df_sorted['end_date'] = df_sorted.groupby('player_sk')['effective_date'].shift(-1)
        df_sorted['is_current'] = df_sorted['end_date'].isna()
        # Use 2099 instead of 2999 (pandas datetime limit)
        df_sorted.loc[df_sorted['is_current'], 'end_date'] = pd.to_datetime('2099-12-31')

        # Create dimension table
        player_dim = df_sorted[[
            'player_sk', 'version', 'Player', 'Nation', 'Born',
            'Pos', 'Squad', 'Age', 'Season',
            'effective_date', 'end_date', 'is_current'
        ]].copy()

        print(f"  Player dimension: {len(player_dim)} records")
        print(f"  Unique players: {player_dim['player_sk'].nunique()}")
        print(f"  Current records: {player_dim['is_current'].sum()}")

        return player_dim

    def create_stats_fact_table(self, df: pd.DataFrame, player_dim: pd.DataFrame) -> pd.DataFrame:
        """
        Create fact table with just stats (memory efficient)

        Fact tables contain measures (numeric stats) and foreign keys.
        This is much more memory-efficient than repeating player attributes.

        Args:
            df: Combined stats dataframe
            player_dim: Player dimension table

        Returns:
            Stats fact table
        """
        print("Creating Stats Fact Table...")

        # Create matching key for joining
        df['player_sk'] = (
            df['Player'].astype(str) + '_' +
            df['Nation'].astype(str) + '_' +
            df['Born'].astype(str)
        ).apply(lambda x: abs(hash(x)) % (10 ** 10))

        # Merge to get version from dimension
        df_with_dim = df.merge(
            player_dim[['player_sk', 'Season', 'version']],
            on=['player_sk', 'Season'],
            how='left'
        )

        # Select only numeric stat columns (measures)
        numeric_cols = df_with_dim.select_dtypes(include=[np.number]).columns.tolist()

        # Exclude key/dimension columns from numeric list
        exclude_cols = ['player_sk', 'version', 'Age', 'Born', 'Season']
        stat_cols = [c for c in numeric_cols if c not in exclude_cols]

        # Build fact table
        fact_cols = ['player_sk', 'version', 'Season'] + stat_cols
        stats_fact = df_with_dim[fact_cols].copy()

        print(f"  Stats fact table: {len(stats_fact)} records")
        print(f"  Stat columns: {len(stat_cols)}")

        return stats_fact

    def save_to_parquet(self, player_dim: pd.DataFrame, stats_fact: pd.DataFrame):
        """
        Save to Parquet format with partitioning for S3 efficiency

        Parquet benefits:
        - Columnar format (60-80% compression vs CSV)
        - Schema evolution support
        - Predicate pushdown for faster queries
        - Efficient for analytics (ML training)

        Partitioning benefits:
        - Query only relevant partitions
        - Parallel processing
        - Cost-effective S3 scanning
        """
        print("\nSaving to Parquet format...")

        # Save player dimension (not partitioned - it's small)
        player_path = self.parquet_dir / 'player_dimension.parquet'
        player_dim.to_parquet(
            player_path,
            engine='pyarrow',
            compression='snappy',  # Good balance of speed and compression
            index=False
        )
        print(f"  ✓ Player dimension: {player_path}")
        print(f"    Size: {player_path.stat().st_size / 1024:.1f} KB")

        # Save stats fact table - partitioned by season for efficient querying
        stats_partitioned_dir = self.parquet_dir / 'stats_fact'
        stats_partitioned_dir.mkdir(exist_ok=True)

        # Partition by season
        for season in sorted(stats_fact['Season'].unique()):
            season_data = stats_fact[stats_fact['Season'] == season].copy()
            season_path = stats_partitioned_dir / f'season={season}' / 'data.parquet'
            season_path.parent.mkdir(exist_ok=True)

            season_data.to_parquet(
                season_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )
            size_kb = season_path.stat().st_size / 1024
            print(f"  ✓ Season {season}: {len(season_data)} records, {size_kb:.1f} KB")

        print(f"\n  Total stats fact directory: {stats_partitioned_dir}")

    def save_optimized_csv(self, player_dim: pd.DataFrame, stats_fact: pd.DataFrame):
        """
        Save optimized CSV versions (for compatibility)

        Optimizations:
        - Use category dtype for low-cardinality columns
        - Use float32 instead of float64 where appropriate
        - Compress with gzip
        """
        print("\nSaving optimized CSV (gzip compressed)...")

        # Optimize data types
        player_dim_opt = self._optimize_dtypes(player_dim)
        stats_fact_opt = self._optimize_dtypes(stats_fact)

        # Save with gzip compression
        player_csv = self.scd2_dir / 'player_dimension.csv.gz'
        player_dim_opt.to_csv(player_csv, index=False, compression='gzip')
        print(f"  ✓ Player dimension: {player_csv}")
        print(f"    Size: {player_csv.stat().st_size / 1024:.1f} KB")

        stats_csv = self.scd2_dir / 'stats_fact.csv.gz'
        stats_fact_opt.to_csv(stats_csv, index=False, compression='gzip')
        print(f"  ✓ Stats fact: {stats_csv}")
        print(f"    Size: {stats_csv.stat().st_size / 1024:.1f} KB")

    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types for memory efficiency"""
        df_opt = df.copy()

        for col in df_opt.columns:
            col_type = df_opt[col].dtype

            # Convert object columns with low cardinality to category
            if col_type == 'object':
                num_unique = df_opt[col].nunique()
                num_total = len(df_opt[col])
                if num_unique / num_total < 0.5:  # Less than 50% unique
                    df_opt[col] = df_opt[col].astype('category')

            # Downcast numeric columns
            elif col_type == 'float64':
                df_opt[col] = pd.to_numeric(df_opt[col], downcast='float')
            elif col_type == 'int64':
                df_opt[col] = pd.to_numeric(df_opt[col], downcast='integer')

        return df_opt

    def generate_storage_summary(self, player_dim: pd.DataFrame, stats_fact: pd.DataFrame):
        """Generate summary of storage efficiency"""
        print("\n" + "="*60)
        print("STORAGE SUMMARY")
        print("="*60)

        # Memory usage
        player_mem = player_dim.memory_usage(deep=True).sum() / 1024**2
        stats_mem = stats_fact.memory_usage(deep=True).sum() / 1024**2

        print(f"\nIn-Memory Size:")
        print(f"  Player Dimension: {player_mem:.2f} MB")
        print(f"  Stats Fact Table: {stats_mem:.2f} MB")
        print(f"  Total: {player_mem + stats_mem:.2f} MB")

        # Disk usage comparison
        print(f"\nDisk Storage Comparison:")

        # Parquet
        parquet_player = self.parquet_dir / 'player_dimension.parquet'
        if parquet_player.exists():
            parquet_size = parquet_player.stat().st_size / 1024**2
            print(f"  Parquet (player dim): {parquet_size:.2f} MB")

        parquet_stats_dir = self.parquet_dir / 'stats_fact'
        if parquet_stats_dir.exists():
            parquet_stats_size = sum(
                f.stat().st_size for f in parquet_stats_dir.rglob('*.parquet')
            ) / 1024**2
            print(f"  Parquet (stats fact): {parquet_stats_size:.2f} MB")
            print(f"  Parquet Total: {parquet_size + parquet_stats_size:.2f} MB")

        # CSV comparison
        csv_player = self.scd2_dir / 'player_dimension.csv.gz'
        csv_stats = self.scd2_dir / 'stats_fact.csv.gz'
        if csv_player.exists() and csv_stats.exists():
            csv_size = (csv_player.stat().st_size + csv_stats.stat().st_size) / 1024**2
            print(f"  CSV (gzipped): {csv_size:.2f} MB")

        # S3 recommendations
        print(f"\n" + "="*60)
        print("S3 STORAGE RECOMMENDATIONS")
        print("="*60)
        print("""
1. **Format**: Use Parquet (columnar, compressed, schema evolution)
   - 60-80% smaller than CSV
   - Faster for ML feature engineering (column reads)
   - Supports predicate pushdown (query only needed data)

2. **Partitioning Strategy**:
   - Partition by: season=YYYY/team=TEAM_NAME/
   - Enables efficient querying: "Give me all 2025 data"
   - S3 Select can query partitions without downloading all data

3. **File Organization**:
   ```
   s3://your-bucket/mls-stats/
   ├── dimensions/
   │   ├── player_dimension.parquet
   │   └── team_dimension.parquet
   └── facts/
       └── stats/
           ├── season=2023/
           │   ├── team=atlanta_utd/data.parquet
           │   └── team=inter_miami/data.parquet
           ├── season=2024/...
           └── season=2025/...
   ```

4. **For ML Workflows**:
   - Use AWS Glue to catalog Parquet files
   - Query with Amazon Athena (serverless SQL)
   - Load directly into SageMaker with PyArrow
   - Use S3 Select to filter data before download

5. **Cost Optimization**:
   - Lifecycle policy: Archive old seasons to Glacier
   - Current season in S3 Standard
   - Compress with Snappy (good balance)
   - Partition pruning reduces data scanned

6. **Memory Efficiency for ML**:
   - Load only needed columns (Parquet columnar format)
   - Use Dask/Vaex for larger-than-memory datasets
   - Stream from S3 instead of loading all data
   - Feature store pattern: precompute features, store separately
        """)

    def create_ml_optimized_views(self, player_dim: pd.DataFrame, stats_fact: pd.DataFrame):
        """
        Create ML-optimized denormalized views for specific use cases

        While normalized tables are efficient for storage, ML often needs
        denormalized views. Create these on-demand rather than storing them.
        """
        print("\n" + "="*60)
        print("CREATING ML-OPTIMIZED VIEWS")
        print("="*60)

        # View 1: Current season snapshot (for predictions)
        current_season = stats_fact['Season'].max()
        current_players = player_dim[player_dim['is_current'] == True]

        ml_current = stats_fact[stats_fact['Season'] == current_season].merge(
            current_players[['player_sk', 'Player', 'Pos', 'Squad', 'Age']],
            on='player_sk',
            how='left'
        )

        ml_current_path = self.scd2_dir / f'ml_current_season_{current_season}.parquet'
        ml_current.to_parquet(ml_current_path, compression='snappy', index=False)
        print(f"\n✓ Current Season View ({current_season}): {len(ml_current)} records")
        print(f"  File: {ml_current_path}")
        print(f"  Size: {ml_current_path.stat().st_size / 1024:.1f} KB")

        # View 2: Time series features (historical stats per player)
        ml_timeseries = stats_fact.merge(
            player_dim[['player_sk', 'version', 'Player', 'Season']],
            on=['player_sk', 'version', 'Season'],
            how='left'
        ).sort_values(['player_sk', 'Season'])

        ml_ts_path = self.scd2_dir / 'ml_timeseries_all_seasons.parquet'
        ml_timeseries.to_parquet(ml_ts_path, compression='snappy', index=False)
        print(f"\n✓ Time Series View: {len(ml_timeseries)} records")
        print(f"  File: {ml_ts_path}")
        print(f"  Size: {ml_ts_path.stat().st_size / 1024:.1f} KB")

        return ml_current, ml_timeseries


def main():
    """Main execution"""

    print("="*60)
    print("SCD TYPE 2 STORAGE MANAGER")
    print("="*60)

    # Initialize manager
    manager = SCD2StorageManager()

    # Load combined stats
    print("\nLoading combined stats...")
    combined_path = manager.data_dir / 'processed' / 'all_seasons_combined.csv'
    if not combined_path.exists():
        print(f"ERROR: {combined_path} not found")
        print("Run Stats_Processor.py first to generate combined stats")
        return

    df = pd.read_csv(combined_path)
    print(f"  Loaded {len(df)} records")

    # Create SCD2 structure
    player_dim = manager.create_player_dimension(df)
    stats_fact = manager.create_stats_fact_table(df, player_dim)

    # Save in multiple formats
    manager.save_to_parquet(player_dim, stats_fact)
    manager.save_optimized_csv(player_dim, stats_fact)

    # Create ML-optimized views
    manager.create_ml_optimized_views(player_dim, stats_fact)

    # Generate summary
    manager.generate_storage_summary(player_dim, stats_fact)

    print("\n" + "="*60)
    print("✓ COMPLETE!")
    print("="*60)
    print(f"\nSCD2 data saved to: {manager.scd2_dir}")
    print(f"Parquet files: {manager.parquet_dir}")


if __name__ == '__main__':
    main()
