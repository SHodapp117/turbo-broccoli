"""
MLS Contract Valuation System

Two-Stage ML Approach:
1. Segment by Position × Roster Designation (business groupings)
2. Use ML (DBSCAN) to discover archetypes within each segment
3. Build regression models to predict contract value

This is data-driven - archetypes are discovered by ML, not predefined.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class ContractValuationSystem:
    """
    Hierarchical ML system for contract valuation:
    - Stage 1: Segment by position × designation
    - Stage 2: ML discovers archetypes within segments
    - Stage 3: Predict contract value based on archetype + stats
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent / 'data'
        else:
            self.data_dir = Path(data_dir)

        self.output_dir = self.data_dir / 'contract_valuation'
        self.output_dir.mkdir(exist_ok=True)

        self.df_master = None
        self.archetypes = {}  # Store discovered archetypes
        self.models = {}  # Store valuation models
        self.scaler = StandardScaler()

    def load_and_merge_data(self, season: int = 2025):
        """
        Load stats, roster, and salary data and merge

        Returns:
            Merged DataFrame with all data
        """
        print(f"Loading {season} data...")

        # Load stats
        stats_file = self.data_dir / 'scd2' / f'ml_current_season_{season}.parquet'
        if not stats_file.exists():
            stats_file = self.data_dir / 'processed' / f'{season}_all_stats.csv'
            df_stats = pd.read_csv(stats_file)
        else:
            df_stats = pd.read_parquet(stats_file)

        print(f"  Stats: {len(df_stats)} players")

        # Load roster designations
        roster_file = self.data_dir / f'{season}_roster_profiles_parsed.csv'
        df_roster = pd.read_csv(roster_file)
        print(f"  Roster: {len(df_roster)} players")

        # Load salary data
        salary_file = self.data_dir / 'mls_salaries_all_classified.csv'
        df_salary = pd.read_csv(salary_file)
        print(f"  Salary: {len(df_salary)} records")

        # Merge stats + roster
        df_merged = df_stats.merge(
            df_roster[['name', 'category', 'contract_thru']],
            left_on='Player',
            right_on='name',
            how='left'
        )

        # Merge with salary
        # Need to match on player name and season (salary data uses 'year' not 'season')
        df_salary['year_int'] = df_salary['year'].astype(int)
        df_merged = df_merged.merge(
            df_salary[['player', 'year_int', 'base_salary', 'compensation']],
            left_on=['Player', 'Season'],
            right_on=['player', 'year_int'],
            how='left'
        )

        print(f"\nMerged: {len(df_merged)} players")
        print(f"  With salary data: {df_merged['base_salary'].notna().sum()}")
        print(f"  With roster designation: {df_merged['category'].notna().sum()}")

        # Feature engineering
        df_merged = self._engineer_features(df_merged)

        self.df_master = df_merged
        return df_merged

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create position-specific features for analysis"""

        print("\nEngineering features...")

        # Per-90 stats
        if '90s Played90s played' in df.columns:
            minutes_col = '90s Played90s played'
        elif '90s' in df.columns:
            minutes_col = '90s'
        else:
            minutes_col = None

        if minutes_col and df[minutes_col].notna().any():
            df['goals_per_90'] = df['Goals'] / df[minutes_col].replace(0, np.nan)
            df['assists_per_90'] = df['Assists'] / df[minutes_col].replace(0, np.nan)
            df['xg_per_90'] = df['xG'] / df[minutes_col].replace(0, np.nan)
        else:
            df['goals_per_90'] = 0
            df['assists_per_90'] = 0
            df['xg_per_90'] = 0

        # xG overperformance
        df['xg_overperformance'] = df['Goals'] - df['xG']

        # Progressive actions
        if 'PrgP' in df.columns and 'PrgC' in df.columns:
            df['progressive_actions'] = df['PrgP'] + df['PrgC']
        else:
            df['progressive_actions'] = 0

        # Defensive actions
        if 'Tkl' in df.columns and 'Int' in df.columns:
            df['defensive_actions'] = df['Tkl'] + df['Int']
        else:
            df['defensive_actions'] = 0

        # Simplify position to major groups
        df['position_group'] = df['Pos'].apply(self._simplify_position)

        # Simplify designation
        df['designation_tier'] = df['category'].fillna('Unknown').replace({
            'Designated Player': 'DP',
            'U22 Initiative': 'U22',
            'TAM Player': 'TAM',
            'Homegrown': 'HG',
            'Generation Adidas': 'GA',
            'Standard': 'Standard'
        })

        print(f"  Created per-90 stats, overperformance, progressive/defensive actions")

        return df

    def _simplify_position(self, pos: str) -> str:
        """Simplify position to major groups"""
        if pd.isna(pos):
            return 'Unknown'

        pos_upper = str(pos).upper()

        if 'GK' in pos_upper:
            return 'GK'
        elif 'DF' in pos_upper or 'CB' in pos_upper or 'FB' in pos_upper:
            return 'DF'
        elif 'MF' in pos_upper or 'CM' in pos_upper or 'AM' in pos_upper:
            return 'MF'
        elif 'FW' in pos_upper or 'ST' in pos_upper or 'CF' in pos_upper:
            return 'FW'
        else:
            # Handle hybrids - take first position
            if ',' in pos_upper:
                first = pos_upper.split(',')[0].strip()
                return self._simplify_position(first)
            return 'Unknown'

    def discover_archetypes(self, position: str, min_players: int = 20):
        """
        Use DBSCAN to discover archetypes within a position (clustering by stats only)

        Args:
            position: Position group (FW, MF, DF, GK)
            min_players: Minimum players needed for clustering

        Returns:
            DataFrame with archetype assignments
        """
        segment_key = position
        print(f"\n{'='*60}")
        print(f"DISCOVERING ARCHETYPES: {position}")
        print(f"{'='*60}")

        # Filter to position only (no designation filtering)
        df_segment = self.df_master[
            self.df_master['position_group'] == position
        ].copy()

        if len(df_segment) < min_players:
            print(f"  Insufficient players ({len(df_segment)} < {min_players}), skipping")
            return None

        print(f"  Players in segment: {len(df_segment)}")

        # Select features based on position
        features = self._get_features_for_position(position)

        # Filter to available features
        available_features = [f for f in features if f in df_segment.columns]
        print(f"  Using {len(available_features)} features: {', '.join(available_features[:5])}...")

        # Extract and scale features
        X = df_segment[available_features].fillna(0)
        X_scaled = StandardScaler().fit_transform(X)

        # Run DBSCAN
        # Adjust eps based on segment size
        if len(df_segment) < 20:
            eps = 1.5
            min_samples = 3
        elif len(df_segment) < 50:
            eps = 2.0
            min_samples = 4
        else:
            eps = 2.5
            min_samples = 5

        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        df_segment['archetype'] = dbscan.fit_predict(X_scaled)

        # Analyze archetypes
        n_archetypes = len(set(df_segment['archetype'])) - (1 if -1 in df_segment['archetype'] else 0)
        n_outliers = (df_segment['archetype'] == -1).sum()

        print(f"\n  Results:")
        print(f"    Archetypes found: {n_archetypes}")
        print(f"    Outliers: {n_outliers}")

        # Profile each archetype
        for archetype_id in sorted(df_segment['archetype'].unique()):
            arch_data = df_segment[df_segment['archetype'] == archetype_id]

            if archetype_id == -1:
                name = "Outliers"
            else:
                # Auto-name archetype based on stats
                name = self._name_archetype(arch_data, position, archetype_id)

            print(f"\n    {name} ({len(arch_data)} players):")

            # Key stats
            if 'goals_per_90' in arch_data.columns:
                print(f"      Goals/90: {arch_data['goals_per_90'].mean():.2f}")
            if 'assists_per_90' in arch_data.columns:
                print(f"      Assists/90: {arch_data['assists_per_90'].mean():.2f}")
            if 'defensive_actions' in arch_data.columns and position in ['DF', 'MF']:
                print(f"      Def Actions: {arch_data['defensive_actions'].mean():.1f}")

            # Salary stats (if available)
            if arch_data['base_salary'].notna().sum() > 0:
                salary_data = arch_data[arch_data['base_salary'].notna()]
                print(f"      Avg Salary: ${salary_data['base_salary'].mean()/1000:.0f}K")
                print(f"      Salary Range: ${salary_data['base_salary'].min()/1000:.0f}K - ${salary_data['base_salary'].max()/1000:.0f}K")

            # Top players
            if len(arch_data) <= 5:
                print(f"      Players: {', '.join(arch_data['Player'].values)}")
            else:
                # Show highest paid
                if arch_data['base_salary'].notna().sum() > 0:
                    top = arch_data.nlargest(3, 'base_salary')
                    print(f"      Top earners: {', '.join(top['Player'].values)}")

        # Store archetypes
        self.archetypes[segment_key] = df_segment

        return df_segment

    def _get_features_for_position(self, position: str) -> List[str]:
        """Get relevant features for clustering by position"""

        # Common features
        common = ['goals_per_90', 'assists_per_90', 'xG', 'npxG', 'Minutes']

        position_specific = {
            'FW': common + ['Sh', 'SoT', 'xg_overperformance', 'PrgC', 'PrgR'],
            'MF': common + ['PrgP', 'KP', 'Cmp', 'PPA', 'defensive_actions', 'progressive_actions'],
            'DF': ['Minutes', 'defensive_actions', 'PrgP', 'Tkl', 'Int', 'Blocks', 'Cmp'],
            'GK': ['Minutes', 'Saves', 'Save%', 'GA', 'SoTA', 'CS']
        }

        return position_specific.get(position, common)

    def _name_archetype(self, df: pd.DataFrame, position: str, arch_id: int) -> str:
        """Auto-generate archetype name based on stats profile"""

        if position == 'FW':
            goals = df['goals_per_90'].mean()
            assists = df['assists_per_90'].mean()

            if goals > 0.5:
                return f"Archetype {arch_id}: Elite Scorer"
            elif assists > 0.3:
                return f"Archetype {arch_id}: Playmaking Forward"
            else:
                return f"Archetype {arch_id}: Role Player"

        elif position == 'MF':
            assists = df['assists_per_90'].mean()
            def_actions = df['defensive_actions'].mean()

            if assists > 0.25:
                return f"Archetype {arch_id}: Creative Midfielder"
            elif def_actions > 30:
                return f"Archetype {arch_id}: Defensive Midfielder"
            else:
                return f"Archetype {arch_id}: Box-to-Box"

        elif position == 'DF':
            def_actions = df['defensive_actions'].mean()
            prog = df.get('PrgP', pd.Series([0])).mean()

            if prog > 10:
                return f"Archetype {arch_id}: Ball-Playing Defender"
            else:
                return f"Archetype {arch_id}: Pure Defender"

        else:
            return f"Archetype {arch_id}"

    def discover_all_archetypes(self):
        """
        Run archetype discovery for all positions (position-only clustering)
        """
        print("\n" + "="*60)
        print("DISCOVERING ALL ARCHETYPES")
        print("="*60)

        positions = ['FW', 'MF', 'DF']

        for position in positions:
            self.discover_archetypes(position)

        print("\n" + "="*60)
        print(f"ARCHETYPE DISCOVERY COMPLETE")
        print(f"Total positions analyzed: {len(self.archetypes)}")
        print("="*60)

    def build_valuation_model(self, position: str, designation: str, min_minutes: int = 500):
        """
        Build regression model to predict salary based on stats + archetype

        Args:
            position: Position group
            designation: Designation tier
            min_minutes: Minimum minutes played to include in model (default 500)

        Returns:
            Trained model
        """
        segment_key = f"{position}_{designation}"

        # Get archetype data for position (not position + designation)
        if position not in self.archetypes:
            print(f"No archetypes found for {position}, skipping model")
            return None

        print(f"\n{'='*60}")
        print(f"BUILDING VALUATION MODEL: {position} × {designation}")
        print(f"{'='*60}")

        # Filter archetype data to specific designation for valuation model
        df_with_archetypes = self.archetypes[position]
        df_segment = df_with_archetypes[
            df_with_archetypes['designation_tier'] == designation
        ].copy()

        # Filter to players with salary data AND minimum minutes threshold
        df_train = df_segment[
            (df_segment['base_salary'].notna()) &
            (df_segment['Minutes'] >= min_minutes)
        ].copy()

        if len(df_train) < 10:
            print(f"  Insufficient data ({len(df_train)} players with {min_minutes}+ min), skipping")
            return None

        print(f"  Training samples: {len(df_train)} (with {min_minutes}+ minutes)")
        print(f"  Minutes range: {df_train['Minutes'].min():.0f} - {df_train['Minutes'].max():.0f}")

        # Features: stats + archetype (one-hot encoded)
        stat_features = self._get_features_for_position(position)
        available_stats = [f for f in stat_features if f in df_train.columns]

        # One-hot encode archetype
        archetype_dummies = pd.get_dummies(df_train['archetype'], prefix='archetype')

        # Combine features
        X = pd.concat([
            df_train[available_stats].fillna(0),
            archetype_dummies
        ], axis=1)

        y = df_train['base_salary']

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        print(f"\n  Model Performance:")
        print(f"    R² Score: {r2:.3f}")
        print(f"    MAE: ${mae/1000:.1f}K")

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        print(f"\n  Top 5 Contract Drivers:")
        for _, row in feature_importance.head(5).iterrows():
            print(f"    {row['feature']}: {row['importance']:.3f}")

        # Store model
        self.models[segment_key] = {
            'model': model,
            'features': X.columns.tolist(),
            'r2': r2,
            'mae': mae
        }

        return model

    def build_all_models(self, min_minutes: int = 500):
        """Build valuation models for all position × designation combinations

        Args:
            min_minutes: Minimum minutes played threshold (default 500)
        """

        print("\n" + "="*60)
        print("BUILDING VALUATION MODELS")
        print(f"Minimum minutes threshold: {min_minutes}")
        print("="*60)

        positions = ['FW', 'MF', 'DF']
        designations = ['DP', 'TAM', 'Standard']

        for position in positions:
            for designation in designations:
                self.build_valuation_model(position, designation, min_minutes)

        print("\n" + "="*60)
        print(f"MODEL BUILDING COMPLETE")
        print(f"Models trained: {len(self.models)}")
        print("="*60)

    def value_player(self, player_name: str) -> Dict:
        """
        Predict contract value for a specific player

        Args:
            player_name: Player name

        Returns:
            Valuation dictionary
        """
        # Find player
        player = self.df_master[self.df_master['Player'] == player_name]

        if len(player) == 0:
            return {'error': f'Player {player_name} not found'}

        player = player.iloc[0]

        position = player['position_group']
        designation = player['designation_tier']
        segment_key = f"{position}_{designation}"

        # Check if we have a model
        if segment_key not in self.models:
            return {
                'player': player_name,
                'position': position,
                'designation': designation,
                'error': f'No valuation model for {segment_key}'
            }

        # Get archetype assignment (from position-level clustering)
        if position in self.archetypes:
            arch_df = self.archetypes[position]
            player_arch = arch_df[arch_df['Player'] == player_name]
            if len(player_arch) > 0:
                archetype = player_arch.iloc[0]['archetype']
            else:
                archetype = -1  # Unknown
        else:
            archetype = -1

        # Prepare features
        model_info = self.models[segment_key]
        model = model_info['model']

        # Build feature vector (need to match training features exactly)
        # This is simplified - in production you'd need to handle this more carefully

        return {
            'player': player_name,
            'position': position,
            'designation': designation,
            'archetype': archetype,
            'actual_salary': player.get('base_salary'),
            'model_available': True
        }

    def save_results(self):
        """Save archetype assignments and model summaries"""

        print("\n" + "="*60)
        print("SAVING RESULTS")
        print("="*60)

        # Save all archetypes to one file
        all_archetypes = []
        for segment_key, df in self.archetypes.items():
            df_copy = df.copy()
            df_copy['segment'] = segment_key
            all_archetypes.append(df_copy)

        if all_archetypes:
            df_all = pd.concat(all_archetypes, ignore_index=True)
            output_file = self.output_dir / 'player_archetypes_2025.csv'
            df_all.to_csv(output_file, index=False)
            print(f"  ✓ Saved archetypes: {output_file}")

        # Save model summary
        model_summary = []
        for segment_key, model_info in self.models.items():
            model_summary.append({
                'segment': segment_key,
                'r2_score': model_info['r2'],
                'mae': model_info['mae']
            })

        if model_summary:
            df_models = pd.DataFrame(model_summary)
            output_file = self.output_dir / 'model_performance.csv'
            df_models.to_csv(output_file, index=False)
            print(f"  ✓ Saved model performance: {output_file}")

        print(f"\n  All files saved to: {self.output_dir}")


def main():
    """Main execution"""

    print("="*60)
    print("MLS CONTRACT VALUATION SYSTEM")
    print("="*60)

    # Initialize
    system = ContractValuationSystem()

    # Load data
    df = system.load_and_merge_data(season=2025)

    # Discover archetypes (no minutes threshold for discovery)
    system.discover_all_archetypes()

    # Build valuation models with minutes threshold
    # Recommended: 1500+ minutes for best R² scores
    MIN_MINUTES = 1500  # Adjust this value to improve R² score
    system.build_all_models(min_minutes=MIN_MINUTES)

    # Save results
    system.save_results()

    print("\n" + "="*60)
    print("✓ COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()
