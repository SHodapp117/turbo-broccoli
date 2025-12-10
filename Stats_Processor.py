"""
MLS Stats Processor

Consolidates FBref stats CSVs from multiple seasons (2023-2025) and stat categories
into unified dataframes for analysis.

Handles:
- Different stat categories per season (Standard, Passing, Shooting, etc.)
- Inconsistent file naming (e.g., "standardStats" vs "Standard", "Possesion" vs "Possession")
- Multi-team player records (players who transferred mid-season)
- Column name cleaning (removing descriptive suffixes from FBref exports)
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List


class StatsProcessor:
    """Process and consolidate MLS player statistics from FBref CSV exports"""

    # Map stat categories to canonical names
    STAT_CATEGORIES = {
        'standard': ['Standard', 'standardStats'],
        'passing': ['Passing'],
        'shooting': ['Shooting'],
        'possession': ['Possession', 'Possesion'],  # Handle typo
        'defensive': ['DefensiveActions'],
        'goalshot': ['GoalShotCreation', 'ShotGoalCreation'],
        'performance': ['Preformance', 'BoxPreformance'],  # Handle typo
        'goalkeeping': ['Goalkeeping']
    }

    def __init__(self, data_dir: str = None):
        """
        Initialize the processor

        Args:
            data_dir: Path to data directory. Defaults to ./data/
        """
        if data_dir is None:
            self.data_dir = Path(__file__).parent / 'data'
        else:
            self.data_dir = Path(data_dir)

        self.seasons = [2023, 2024, 2025]
        self.stats_by_season = {}

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean FBref column names by removing descriptive suffixes

        FBref exports include long descriptions after column names like:
        "xG: Expected GoalsExpected GoalsxG totals include penalty kicks..."

        This function extracts just the short column name.

        Args:
            df: DataFrame with FBref columns

        Returns:
            DataFrame with cleaned column names
        """
        new_columns = []

        for col in df.columns:
            # Handle the rank column
            if col.startswith('0_Rk'):
                new_columns.append('Rk')
                continue

            # Extract base column name (e.g., "1_Player" -> "Player")
            # Pattern: "number_columnName" or "category_columnName"
            parts = str(col).split('_', 1)
            if len(parts) == 2:
                base_name = parts[1]
            else:
                base_name = col

            # Try to extract just the short name before descriptions
            # Look for patterns like "Name: Description" or "NameDescription"
            # Keep only the part before colon or before capital letter that starts description
            if ':' in base_name:
                clean_name = base_name.split(':')[0].strip()
            elif re.search(r'[a-z][A-Z][a-z]', base_name):
                # Split at transition from lowercase to uppercase followed by lowercase
                # e.g., "90s Played90s played" -> "90s Played"
                clean_name = re.split(r'(?<=[a-z])(?=[A-Z][a-z])', base_name)[0]
            else:
                clean_name = base_name

            # Remove trailing punctuation and whitespace
            clean_name = clean_name.rstrip(': \t')

            new_columns.append(clean_name)

        df.columns = new_columns
        return df

    def find_stat_file(self, season: int, category_key: str) -> Path:
        """
        Find the stat file for a given season and category

        Handles naming inconsistencies across seasons

        Args:
            season: Year (2023, 2024, 2025)
            category_key: Category key from STAT_CATEGORIES

        Returns:
            Path to CSV file, or None if not found
        """
        possible_names = self.STAT_CATEGORIES[category_key]

        for name in possible_names:
            pattern = f"{season}_{name}.csv"
            matching_files = list(self.data_dir.glob(pattern))
            if matching_files:
                return matching_files[0]

        return None

    def load_stat_category(self, season: int, category_key: str) -> pd.DataFrame:
        """
        Load and clean a single stat category for a season

        Args:
            season: Year
            category_key: Category key from STAT_CATEGORIES

        Returns:
            DataFrame with cleaned columns, or None if file not found
        """
        file_path = self.find_stat_file(season, category_key)

        if not file_path:
            print(f"  Warning: No {category_key} file found for {season}")
            return None

        print(f"  Loading {file_path.name}")

        try:
            df = pd.read_csv(file_path)
            df = self.clean_column_names(df)

            # Add season column
            df['Season'] = season

            # Drop the Rk column (just a row number)
            if 'Rk' in df.columns:
                df = df.drop(columns=['Rk'])

            return df

        except Exception as e:
            print(f"  Error loading {file_path.name}: {e}")
            return None

    def merge_stat_categories(self, season: int, categories: List[str]) -> pd.DataFrame:
        """
        Merge multiple stat categories for a single season
        Position-aware: Only merges relevant stats for each position (GK vs outfield)

        Args:
            season: Year
            categories: List of category keys to merge

        Returns:
            Merged DataFrame
        """
        print(f"\nMerging {season} stats...")

        # Load first category as base
        base_df = None
        base_category = None

        for cat in categories:
            df = self.load_stat_category(season, cat)
            if df is not None:
                base_df = df
                base_category = cat
                break

        if base_df is None:
            print(f"  ERROR: Could not load any stats for {season}")
            return None

        print(f"  Base: {base_category} ({len(base_df)} rows)")

        # Merge keys - use player, nation, position, team, age
        merge_keys = ['Player', 'Nation', 'Pos', 'Squad', 'Age', 'Born', 'Season']

        # Split players by position
        gk_mask = base_df['Pos'] == 'GK'
        outfield_df = base_df[~gk_mask].copy()
        gk_df = base_df[gk_mask].copy()

        print(f"  Outfield players: {len(outfield_df)}, Goalkeepers: {len(gk_df)}")

        # Define position-specific categories
        outfield_categories = [cat for cat in categories if cat != 'goalkeeping']
        gk_categories = ['standard', 'goalkeeping']  # GKs only get standard stats + GK-specific stats

        # Merge outfield players with outfield stats
        for cat in outfield_categories:
            if cat == base_category:
                continue

            df = self.load_stat_category(season, cat)
            if df is None:
                continue

            # Filter to outfield players only
            df_outfield = df[df['Pos'] != 'GK'].copy()
            if len(df_outfield) == 0:
                continue

            # Find columns to merge (exclude merge keys and duplicates)
            cols_to_merge = merge_keys + [c for c in df_outfield.columns if c not in outfield_df.columns and c not in merge_keys]
            df_to_merge = df_outfield[cols_to_merge]

            # Merge
            before_count = len(outfield_df)
            outfield_df = outfield_df.merge(
                df_to_merge,
                on=merge_keys,
                how='left',
                suffixes=('', f'_{cat}')
            )

            new_cols = len(cols_to_merge) - len(merge_keys)

            if len(outfield_df) != before_count:
                print(f"  WARNING: Outfield merge with {cat} changed row count ({before_count} -> {len(outfield_df)})")
            else:
                print(f"  Merged outfield {cat} (+{new_cols} columns)")

        # Merge goalkeepers with GK-specific stats only
        for cat in gk_categories:
            if cat == base_category or len(gk_df) == 0:
                continue

            df = self.load_stat_category(season, cat)
            if df is None:
                continue

            # Filter to goalkeepers only
            df_gk = df[df['Pos'] == 'GK'].copy()
            if len(df_gk) == 0:
                continue

            # Find columns to merge (exclude merge keys and duplicates)
            cols_to_merge = merge_keys + [c for c in df_gk.columns if c not in gk_df.columns and c not in merge_keys]
            df_to_merge = df_gk[cols_to_merge]

            # Merge
            before_count = len(gk_df)
            gk_df = gk_df.merge(
                df_to_merge,
                on=merge_keys,
                how='left',
                suffixes=('', f'_{cat}')
            )

            new_cols = len(cols_to_merge) - len(merge_keys)

            if len(gk_df) != before_count:
                print(f"  WARNING: GK merge with {cat} changed row count ({before_count} -> {len(gk_df)})")
            else:
                print(f"  Merged GK {cat} (+{new_cols} columns)")

        # Remove duplicate columns (keep first occurrence)
        outfield_df = outfield_df.loc[:, ~outfield_df.columns.duplicated()]
        gk_df = gk_df.loc[:, ~gk_df.columns.duplicated()]

        # Combine outfield and GK dataframes
        # Fill missing columns with NaN for the position group that doesn't have them
        all_columns = list(set(outfield_df.columns) | set(gk_df.columns))

        # Add missing columns to outfield_df
        for col in gk_df.columns:
            if col not in outfield_df.columns:
                outfield_df[col] = pd.NA

        # Add missing columns to gk_df
        for col in outfield_df.columns:
            if col not in gk_df.columns:
                gk_df[col] = pd.NA

        # Ensure same column order
        gk_df = gk_df[outfield_df.columns]

        base_df = pd.concat([outfield_df, gk_df], ignore_index=True)

        print(f"  Final: {len(base_df)} rows, {len(base_df.columns)} columns")
        print(f"    Outfield: {len(outfield_df)} rows, {len(outfield_df.columns)} columns")
        print(f"    GK: {len(gk_df)} rows, {len(gk_df.columns)} columns")

        return base_df

    def process_all_seasons(self, categories: List[str] = None) -> Dict[int, pd.DataFrame]:
        """
        Process stats for all seasons

        Args:
            categories: List of category keys to include. If None, includes all available.

        Returns:
            Dictionary mapping season -> DataFrame
        """
        if categories is None:
            categories = list(self.STAT_CATEGORIES.keys())

        print("="*60)
        print("MLS STATS PROCESSOR")
        print("="*60)

        results = {}

        for season in self.seasons:
            df = self.merge_stat_categories(season, categories)
            if df is not None:
                results[season] = df

        self.stats_by_season = results

        return results

    def create_combined_dataframe(self, categories: List[str] = None) -> pd.DataFrame:
        """
        Create a single unified DataFrame with all seasons

        Args:
            categories: List of category keys to include

        Returns:
            Combined DataFrame with all seasons
        """
        if not self.stats_by_season:
            self.process_all_seasons(categories)

        print("\n" + "="*60)
        print("COMBINING SEASONS")
        print("="*60)

        # Stack all seasons
        all_seasons = []
        for season in self.seasons:
            if season in self.stats_by_season:
                df = self.stats_by_season[season].copy()
                all_seasons.append(df)
                print(f"  {season}: {len(df)} rows")

        if not all_seasons:
            print("  ERROR: No season data to combine")
            return None

        combined = pd.concat(all_seasons, ignore_index=True)

        print(f"\nCombined: {len(combined)} total rows")
        print(f"  Columns: {len(combined.columns)}")
        print(f"  Unique players: {combined['Player'].nunique()}")

        return combined

    def save_dataframes(self, output_dir: str = None):
        """
        Save processed dataframes to CSV

        Args:
            output_dir: Directory to save files. Defaults to data/processed/
        """
        if output_dir is None:
            output_dir = self.data_dir / 'processed'
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        print("\n" + "="*60)
        print("SAVING DATAFRAMES")
        print("="*60)

        # Save individual seasons
        for season, df in self.stats_by_season.items():
            output_file = output_dir / f'{season}_all_stats.csv'
            df.to_csv(output_file, index=False)
            print(f"  Saved {output_file.name} ({len(df)} rows)")

        # Save combined
        combined = self.create_combined_dataframe()
        if combined is not None:
            output_file = output_dir / 'all_seasons_combined.csv'
            combined.to_csv(output_file, index=False)
            print(f"  Saved {output_file.name} ({len(combined)} rows)")

        print("\n✓ All files saved to:", output_dir)

        return output_dir

    def get_summary_stats(self):
        """Print summary statistics about the processed data"""

        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)

        for season, df in self.stats_by_season.items():
            print(f"\n{season} Season:")
            print(f"  Total rows: {len(df)}")
            print(f"  Unique players: {df['Player'].nunique()}")
            print(f"  Teams: {df['Squad'].nunique()}")
            print(f"  Columns: {len(df.columns)}")

            # Position breakdown
            if 'Pos' in df.columns:
                print(f"\n  Players by position:")
                pos_counts = df['Pos'].value_counts().head(10)
                for pos, count in pos_counts.items():
                    print(f"    {pos}: {count}")

            # Top scorers
            try:
                if 'Goals' in df.columns or 'Gls' in df.columns:
                    goal_col = 'Goals' if 'Goals' in df.columns else 'Gls'

                    # Check if column is duplicated
                    if df.columns.duplicated().any() and goal_col in df.columns[df.columns.duplicated()]:
                        # Get first occurrence of the column
                        col_idx = df.columns.get_loc(goal_col)
                        if not isinstance(col_idx, int):
                            col_idx = col_idx[0]
                        goal_data = df.iloc[:, col_idx]
                        df_temp = pd.DataFrame({
                            'Player': df['Player'],
                            'Squad': df['Squad'],
                            'Goals': goal_data
                        })
                        df_sorted = df_temp.nlargest(5, 'Goals')
                    else:
                        df_sorted = df.nlargest(5, goal_col)

                    print(f"\n  Top 5 scorers:")
                    for _, row in df_sorted.iterrows():
                        goals = row['Goals'] if 'Goals' in row else row[goal_col]
                        print(f"    {row['Player']} ({row['Squad']}): {goals} goals")
            except Exception as e:
                print(f"\n  Could not display top scorers: {e}")


def main():
    """Main execution function"""

    # Initialize processor
    processor = StatsProcessor()

    # Process all stat categories for all seasons
    processor.process_all_seasons()

    # Save to processed directory
    processor.save_dataframes()

    # Print summary
    processor.get_summary_stats()

    print("\n" + "="*60)
    print("DONE!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
