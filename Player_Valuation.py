"""
Player Valuation System

Predicts player designation tier, archetype, and contract value based on performance stats.

Author: Spencer Hodapp
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import json
import warnings
warnings.filterwarnings('ignore')


class PlayerValuationSystem:
    """
    Complete player valuation system:
    1. Predicts designation tier (DP/TAM/Standard) from stats
    2. Assigns archetype based on position clustering
    3. Estimates salary range using peer comparison
    """

    def __init__(self):
        self.data_dir = Path('data')
        self.processed_dir = self.data_dir / 'processed'
        self.output_dir = self.data_dir / 'player_valuation'
        self.output_dir.mkdir(exist_ok=True)

        # Models
        self.designation_classifiers = {}  # position -> classifier
        self.archetypes = {}  # position -> DataFrame with archetypes
        self.salary_models = {}  # position_designation -> model

        # Data
        self.df_master = None

        # Load player name mapping
        self.name_mapping = {}
        mapping_file = self.data_dir / 'player_name_mapping.json'
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                self.name_mapping = json.load(f)

        # Load granular position data (FC 25)
        self.position_data = None
        self._load_granular_positions()

    def _load_granular_positions(self):
        """Load FC 25 granular position data."""
        position_file = self.data_dir / 'player_positions_granular.csv'
        if position_file.exists():
            self.position_data = pd.read_csv(position_file)
            print(f"✓ Loaded granular positions for {len(self.position_data)} players")
        else:
            print("⚠️  Granular position data not found. Using FBref positions only.")

    def get_player_position(self, player_name: str, fbref_position: str = None) -> Dict[str, str]:
        """
        Get granular position data for a player.

        Returns:
            Dict with 'granular_position', 'alternative_positions', 'position_group'
        """
        result = {
            'granular_position': None,
            'alternative_positions': None,
            'position_group': self._simplify_position(fbref_position) if fbref_position else 'Unknown'
        }

        # Try to find granular position
        if self.position_data is not None:
            match = self.position_data[self.position_data['FBref_Name'] == player_name]
            if len(match) > 0:
                result['granular_position'] = match.iloc[0]['Position']
                result['alternative_positions'] = match.iloc[0]['Alternative_Positions']

        return result

    def _get_age_adjustment_factor(self, age: int, position_group: str, granular_position: str = None) -> float:
        """
        Calculate age-based salary adjustment factor using position-specific age curves.
        Based on academic research showing peak performance ages vary by position.

        Returns:
            Multiplier (0.8 to 1.2) to adjust base salary recommendation
        """

        # Position-specific peak age ranges (from academic research)
        peak_ages = {
            # Forwards peak earlier (pace-dependent)
            'FW': {'start': 24, 'peak': 27, 'decline': 30},
            'ST': {'start': 24, 'peak': 27, 'decline': 30},
            'CF': {'start': 24, 'peak': 27, 'decline': 30},
            'LW': {'start': 23, 'peak': 26, 'decline': 29},
            'RW': {'start': 23, 'peak': 26, 'decline': 29},

            # Attacking midfielders (balanced)
            'CAM': {'start': 24, 'peak': 27, 'decline': 30},
            'LM': {'start': 23, 'peak': 26, 'decline': 29},
            'RM': {'start': 23, 'peak': 26, 'decline': 29},

            # Central midfielders peak slightly later (experience matters)
            'MF': {'start': 25, 'peak': 28, 'decline': 31},
            'CM': {'start': 25, 'peak': 28, 'decline': 31},
            'CDM': {'start': 26, 'peak': 29, 'decline': 32},

            # Defenders peak latest (positioning/experience key)
            'DF': {'start': 26, 'peak': 29, 'decline': 32},
            'CB': {'start': 26, 'peak': 29, 'decline': 33},
            'LB': {'start': 24, 'peak': 27, 'decline': 30},
            'RB': {'start': 24, 'peak': 27, 'decline': 30},

            # Goalkeepers have longest careers
            'GK': {'start': 26, 'peak': 30, 'decline': 35}
        }

        # Use granular position if available, else position group
        position_key = granular_position if granular_position in peak_ages else position_group
        peaks = peak_ages.get(position_key, {'start': 24, 'peak': 27, 'decline': 30})

        # Calculate adjustment factor
        if age < peaks['start']:
            # Young player - potential but unproven (90-95% of peak value)
            years_to_peak = peaks['start'] - age
            factor = 0.90 + (0.05 * (1 - min(years_to_peak / 3, 1)))

        elif peaks['start'] <= age <= peaks['peak']:
            # Prime years - premium value (100-120%)
            # Peak at optimal age, taper at edges
            if age == peaks['peak']:
                factor = 1.20
            elif age == peaks['start']:
                factor = 1.05
            else:
                # Linear interpolation to peak
                progress = (age - peaks['start']) / (peaks['peak'] - peaks['start'])
                factor = 1.05 + (0.15 * progress)

        elif peaks['peak'] < age <= peaks['decline']:
            # Post-peak but still valuable (95-105%)
            years_past_peak = age - peaks['peak']
            decline_range = peaks['decline'] - peaks['peak']
            factor = 1.20 - (0.25 * (years_past_peak / decline_range))

        else:
            # Past decline age - diminishing value (70-90%)
            years_past_decline = age - peaks['decline']
            factor = max(0.70, 0.95 - (0.05 * min(years_past_decline, 5)))

        return factor

    def _optimize_contract_structure(self, base_salary: float, age: int) -> Dict:
        """
        Suggest optimal MLS contract structure based on salary and age.
        Uses 2025 MLS salary cap rules.

        Returns:
            Dict with designation, GAM/TAM usage, and budget charge
        """

        # 2025 MLS Thresholds
        MAX_BUDGET_CHARGE = 683_750
        TAM_THRESHOLD = 1_683_750

        # Age-based DP budget charges
        if age <= 20:
            DP_CHARGE = 150_000
        elif 21 <= age <= 23:
            DP_CHARGE = 200_000
        else:
            DP_CHARGE = MAX_BUDGET_CHARGE

        result = {
            'base_salary': base_salary,
            'designation': None,
            'budget_charge': 0,
            'allocation_money_needed': 0,
            'allocation_type': None,
            'description': ''
        }

        # Determine designation and structure
        if base_salary <= MAX_BUDGET_CHARGE:
            # Standard roster player
            result['designation'] = 'Standard'
            result['budget_charge'] = base_salary
            result['description'] = f"Standard roster player. Budget charge: ${base_salary:,.0f}"

        elif base_salary <= TAM_THRESHOLD:
            # TAM player (buy down to max budget charge)
            tam_needed = base_salary - MAX_BUDGET_CHARGE
            result['designation'] = 'TAM'
            result['budget_charge'] = MAX_BUDGET_CHARGE
            result['allocation_money_needed'] = tam_needed
            result['allocation_type'] = 'TAM'
            result['description'] = (
                f"TAM player. Use ${tam_needed:,.0f} TAM to buy down from "
                f"${base_salary:,.0f} to ${MAX_BUDGET_CHARGE:,.0f} budget charge"
            )

        else:
            # Designated Player
            result['designation'] = 'DP'
            result['budget_charge'] = DP_CHARGE
            result['description'] = (
                f"Designated Player. Salary ${base_salary:,.0f} "
                f"counts as ${DP_CHARGE:,.0f} against cap (age {age})"
            )

            # Check if can buy down with TAM
            if base_salary <= (MAX_BUDGET_CHARGE + 1_000_000):
                # Within $1M of max charge - eligible for TAM buydown
                tam_to_buydown = base_salary - MAX_BUDGET_CHARGE
                result['tam_buydown_option'] = {
                    'tam_needed': tam_to_buydown,
                    'new_designation': 'TAM',
                    'new_budget_charge': MAX_BUDGET_CHARGE,
                    'description': (
                        f"Option: Use ${tam_to_buydown:,.0f} TAM to remove DP tag, "
                        f"making them a TAM player with ${MAX_BUDGET_CHARGE:,.0f} charge"
                    )
                }

        return result

    def load_and_merge_data(self, seasons: list = [2025, 2024, 2023]):
        """
        Load stats, roster, and salary data from multiple seasons.

        Args:
            seasons: List of seasons to load, in priority order (most recent first)

        Notes:
            - Loads data from all specified seasons
            - For each player, keeps only their most recent season with sufficient data
            - Tracks which season's data is being used per player
        """

        all_data = []

        for season in seasons:
            print(f"\nLoading {season} data...")

            # Load processed stats
            stats_file = self.processed_dir / f'{season}_all_stats.csv'
            if not stats_file.exists():
                print(f"  Stats file not found, skipping {season}")
                continue

            df_stats = pd.read_csv(stats_file)
            print(f"  Stats: {len(df_stats)} players")

            # Load roster data
            roster_file = self.data_dir / f'{season}_roster_profiles_parsed.csv'
            if roster_file.exists():
                df_roster = pd.read_csv(roster_file)
                print(f"  Roster: {len(df_roster)} players")
            else:
                df_roster = pd.DataFrame()  # Empty dataframe if no roster data
                print(f"  Roster data not found")

            # Load salary data
            salary_file = self.data_dir / 'mls_salaries_all_classified.csv'
            df_salary = pd.read_csv(salary_file)
            print(f"  Salary: {len(df_salary)} records")

            # Add Season column to stats if missing
            if 'Season' not in df_stats.columns:
                df_stats['Season'] = season

            # Merge stats + roster
            if not df_roster.empty:
                df_merged = df_stats.merge(
                    df_roster[['name', 'category', 'contract_thru']],
                    left_on='Player',
                    right_on='name',
                    how='left'
                )
            else:
                df_merged = df_stats.copy()

            # Merge with salary
            df_salary['year_int'] = df_salary['year'].astype(int)
            df_merged = df_merged.merge(
                df_salary[['player', 'year_int', 'base_salary', 'compensation']],
                left_on=['Player', 'Season'],
                right_on=['player', 'year_int'],
                how='left'
            )

            print(f"  Merged: {len(df_merged)} players")
            print(f"  With salary data: {df_merged['base_salary'].notna().sum()}")

            # Feature engineering
            df_merged = self._engineer_features(df_merged)

            # Filter to players with sufficient minutes for reliable stats
            df_merged = df_merged[df_merged['Minutes'] >= 270].copy()  # ~3 full games minimum
            print(f"  After minutes filter (270+): {len(df_merged)} players")

            all_data.append(df_merged)

        # Combine all seasons
        if not all_data:
            raise ValueError("No data could be loaded from any season")

        df_combined = pd.concat(all_data, ignore_index=True)
        print(f"\n{'='*60}")
        print(f"Combined data from {len(seasons)} seasons: {len(df_combined)} total records")

        # For each player, keep only their most recent season with data
        # Sort by season (descending) so most recent is first
        df_combined = df_combined.sort_values('Season', ascending=False)

        # Keep first occurrence of each player (most recent season)
        df_combined = df_combined.drop_duplicates(subset=['Player'], keep='first')
        print(f"Unique players (using most recent season): {len(df_combined)}")

        # Add a flag to indicate which season's data is being used
        df_combined['data_season'] = df_combined['Season']

        self.df_master = df_combined
        return df_combined

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create position-specific features"""

        print("\nEngineering features...")

        # Note: FBref data is already in per-90 format for Goals, Assists, xG, etc.
        # No need to divide by 90s again
        df['goals_per_90'] = df['Goals']
        df['assists_per_90'] = df['Assists']
        df['xg_per_90'] = df['xG']

        # Performance metrics
        df['xg_overperformance'] = df['Goals'] - df['xG']
        df['progressive_actions'] = df['PrgC'] + df['PrgP']
        df['defensive_actions'] = df['Tkl'] + df['Int']

        # Simplify FBref position to groups (backup)
        df['position_group'] = df['Pos'].apply(self._simplify_position)

        # Merge granular positions from FC 25
        if self.position_data is not None:
            df = df.merge(
                self.position_data,
                left_on='Player',
                right_on='FBref_Name',
                how='left'
            )
            # Rename columns for clarity
            df = df.rename(columns={
                'Position': 'granular_position',
                'Alternative_Positions': 'alternative_positions'
            })
            print(f"  ✓ Merged granular positions: {df['granular_position'].notna().sum()} players have FC25 data")
        else:
            df['granular_position'] = None
            df['alternative_positions'] = None

        # Map roster designation to tiers (if category column exists)
        if 'category' in df.columns:
            df['designation_tier'] = df['category'].apply(self._map_designation)
        else:
            # If no roster data, set designation_tier to None
            df['designation_tier'] = None

        print(f"  Created per-90 stats, overperformance, progressive/defensive actions")

        return df

    def _simplify_position(self, pos: str) -> str:
        """Simplify position to main groups"""
        if pd.isna(pos):
            return 'Unknown'

        pos_upper = str(pos).upper()

        if 'GK' in pos_upper:
            return 'GK'
        elif 'DF' in pos_upper or 'FB' in pos_upper or 'CB' in pos_upper:
            return 'DF'
        elif 'MF' in pos_upper:
            return 'MF'
        elif 'FW' in pos_upper:
            return 'FW'
        else:
            # Handle hybrids
            if ',' in pos_upper:
                first = pos_upper.split(',')[0].strip()
                return self._simplify_position(first)
            return 'Unknown'

    def _map_designation(self, category: str) -> str:
        """Map roster designation to standard tiers"""
        if pd.isna(category):
            return 'Unknown'

        cat_upper = str(category).upper()

        if 'DESIGNATED' in cat_upper or 'DP' in cat_upper:
            return 'DP'
        elif 'TAM' in cat_upper:
            return 'TAM'
        elif 'U22' in cat_upper or 'U-22' in cat_upper:
            return 'U22'
        elif 'HOMEGROWN' in cat_upper or 'HG' in cat_upper:
            return 'HG'
        elif 'GENERATION ADIDAS' in cat_upper or 'GA' in cat_upper:
            return 'GA'
        else:
            return 'Standard'

    def train_designation_classifiers(self, min_minutes: int = 900):
        """
        Train classifiers to predict designation tier from stats
        One classifier per position
        """

        print("\n" + "="*60)
        print("TRAINING DESIGNATION CLASSIFIERS")
        print(f"Minimum minutes: {min_minutes}")
        print("="*60)

        positions = ['FW', 'MF', 'DF']

        for position in positions:
            print(f"\n{position} Designation Classifier:")
            print("-" * 40)

            # Filter to position with known designation and salary
            df_pos = self.df_master[
                (self.df_master['position_group'] == position) &
                (self.df_master['designation_tier'].isin(['DP', 'TAM', 'Standard'])) &
                (self.df_master['Minutes'] >= min_minutes) &
                (self.df_master['base_salary'].notna())
            ].copy()

            if len(df_pos) < 30:
                print(f"  Insufficient data ({len(df_pos)} players), skipping")
                continue

            # Features: performance stats only
            feature_cols = self._get_features_for_position(position)
            X = df_pos[feature_cols].fillna(0)
            y = df_pos['designation_tier']

            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=42, stratify=y
            )

            # Train classifier
            clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            clf.fit(X_train, y_train)

            # Evaluate
            y_pred = clf.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            print(f"  Training samples: {len(df_pos)}")
            print(f"  Accuracy: {accuracy:.3f}")
            print(f"  Class distribution:")
            for tier in ['DP', 'TAM', 'Standard']:
                count = (y == tier).sum()
                pct = count / len(y) * 100
                print(f"    {tier}: {count} ({pct:.1f}%)")

            # Store model
            self.designation_classifiers[position] = {
                'model': clf,
                'features': feature_cols,
                'accuracy': accuracy,
                'scaler': StandardScaler().fit(X_train)
            }

        print("\n" + "="*60)
        print(f"CLASSIFIERS TRAINED: {len(self.designation_classifiers)}")
        print("="*60)

    def _get_features_for_position(self, position: str, granular_position: str = None) -> List[str]:
        """
        Get relevant features for position, using granular position if available.
        Goes from specific (FC25 positions) to broad (FBref groups).
        """

        # Define granular position-specific feature sets
        granular_features = {
            # Forwards
            'ST': ['goals_per_90', 'xG', 'npxG', 'Sh', 'SoT', 'G/Sh', 'npxG/Shot', 'xg_overperformance', 'Touches', 'CPA'],
            'CF': ['goals_per_90', 'assists_per_90', 'xG', 'xAG', 'SCA90', 'GCA90', 'Touches', 'Succ%', 'PrgC'],
            'LW': ['goals_per_90', 'assists_per_90', 'xG', 'xAG', 'Succ%', 'PrgC', 'CPA', 'CrsPA', 'SCA90'],
            'RW': ['goals_per_90', 'assists_per_90', 'xG', 'xAG', 'Succ%', 'PrgC', 'CPA', 'CrsPA', 'SCA90'],

            # Midfielders - Attacking
            'CAM': ['assists_per_90', 'xAG', 'KP', 'SCA90', 'GCA90', 'PPA', 'CrsPA', 'xG', 'Sh/90'],
            'LM': ['assists_per_90', 'xAG', 'PrgC', 'PrgP', 'Succ%', 'CrsPA', 'SCA90', 'KP'],
            'RM': ['assists_per_90', 'xAG', 'PrgC', 'PrgP', 'Succ%', 'CrsPA', 'SCA90', 'KP'],

            # Midfielders - Central
            'CM': ['PrgP', 'Cmp%', 'KP', 'xAG', 'Tkl+Int', 'progressive_actions', 'defensive_actions', 'Ball Recoveries'],
            'CDM': ['defensive_actions', 'Tkl+Int', 'Tkl%', 'Int', 'Ball Recoveries', 'PrgP', 'Cmp%', 'Blocks'],

            # Defenders
            'CB': ['defensive_actions', 'Tkl+Int', 'Int', 'Blocks', 'Ball Recoveries', 'Cmp%', 'PrgP', 'Aerials won%'],
            'LB': ['defensive_actions', 'Tkl+Int', 'PrgC', 'PrgP', 'Cmp%', 'CrsPA', 'Succ%', 'Ball Recoveries'],
            'RB': ['defensive_actions', 'Tkl+Int', 'PrgC', 'PrgP', 'Cmp%', 'CrsPA', 'Succ%', 'Ball Recoveries'],

            # Goalkeeper
            'GK': ['Saves', 'Save%', 'CS%', 'GA', 'SoTA', 'Post-Shot Expected Goals', 'Cmp%', 'Launch%']
        }

        # Try granular position first
        if granular_position and granular_position in granular_features:
            return granular_features[granular_position]

        # Fallback to broad position groups
        common = ['goals_per_90', 'assists_per_90', 'xG', 'npxG', 'Minutes',
                  'xg_overperformance', 'progressive_actions']

        position_specific = {
            'FW': common + ['Sh', 'SoT', 'PrgC', 'PrgR'],
            'MF': common + ['PrgP', 'KP', 'Cmp', 'PPA', 'defensive_actions'],
            'DF': ['Minutes', 'defensive_actions', 'PrgP', 'Tkl', 'Int', 'Blocks', 'Cmp'],
            'GK': ['Minutes', 'Saves', 'GA', 'SoTA', 'CS']
        }

        return position_specific.get(position, common)

    def load_archetypes(self):
        """Load pre-computed archetypes from Contract_Valuation.py output"""

        print("\nLoading archetypes...")

        archetype_file = self.data_dir / 'contract_valuation' / 'player_archetypes_2025.csv'

        if not archetype_file.exists():
            print(f"  Archetype file not found. Run Contract_Valuation.py first.")
            return

        df_arch = pd.read_csv(archetype_file)

        # Split by position
        for position in ['FW', 'MF', 'DF']:
            df_pos = df_arch[df_arch['segment'] == position].copy()
            self.archetypes[position] = df_pos
            print(f"  {position}: {len(df_pos)} players with archetypes")

    def estimate_salary_range(self, player_stats: pd.Series, n_peers: int = 10) -> Dict:
        """
        Estimate salary range using K-nearest neighbors approach

        Args:
            player_stats: Player's statistics
            n_peers: Number of similar players to compare

        Returns:
            Dictionary with salary estimates
        """

        position = player_stats['position_group']
        granular_position = player_stats.get('granular_position')
        designation = player_stats.get('predicted_designation', player_stats.get('designation_tier'))

        # Get peers: Try granular position first, then fall back to position group
        if granular_position and pd.notna(granular_position):
            # Try to find peers with same granular position first
            df_peers = self.df_master[
                (self.df_master['granular_position'] == granular_position) &
                (self.df_master['designation_tier'] == designation) &
                (self.df_master['base_salary'].notna()) &
                (self.df_master['Minutes'] >= 900)
            ].copy()

            # If not enough granular peers, fall back to position group
            if len(df_peers) < 5:
                df_peers = self.df_master[
                    (self.df_master['position_group'] == position) &
                    (self.df_master['designation_tier'] == designation) &
                    (self.df_master['base_salary'].notna()) &
                    (self.df_master['Minutes'] >= 900)
                ].copy()
                peer_level = 'position_group'
            else:
                peer_level = 'granular_position'
        else:
            # No granular position, use position group
            df_peers = self.df_master[
                (self.df_master['position_group'] == position) &
                (self.df_master['designation_tier'] == designation) &
                (self.df_master['base_salary'].notna()) &
                (self.df_master['Minutes'] >= 900)
            ].copy()
            peer_level = 'position_group'

        if len(df_peers) < 5:
            return {
                'error': f'Insufficient peer data ({len(df_peers)} players)',
                'peers_found': len(df_peers)
            }

        # Features for similarity - use granular position features if available
        feature_cols = self._get_features_for_position(position, granular_position)

        # Filter to features that exist in the data
        available_features = [f for f in feature_cols if f in df_peers.columns]
        if not available_features:
            return {'error': 'No matching features available for comparison'}

        X_peers = df_peers[available_features].fillna(0)
        X_player = player_stats[available_features].fillna(0).values.reshape(1, -1)

        # Find nearest neighbors
        nn = NearestNeighbors(n_neighbors=min(n_peers, len(df_peers)))
        nn.fit(X_peers)
        distances, indices = nn.kneighbors(X_player)

        # Get peer salaries
        peer_players = df_peers.iloc[indices[0]]
        peer_salaries = peer_players['base_salary'].values

        return {
            'predicted_salary': np.median(peer_salaries),
            'salary_range_low': np.percentile(peer_salaries, 25),
            'salary_range_high': np.percentile(peer_salaries, 75),
            'peer_min': peer_salaries.min(),
            'peer_max': peer_salaries.max(),
            'n_peers': len(peer_players),
            'peer_names': peer_players['Player'].tolist()[:5],  # Top 5 most similar
            'peer_salaries': peer_salaries[:5].tolist(),
            'peer_level': peer_level,  # 'granular_position' or 'position_group'
            'features_used': available_features  # Track which features were used for comparison
        }

    def value_player(self, player_name: str) -> Dict:
        """
        Complete valuation for a player

        Returns:
            - Predicted designation tier
            - Archetype assignment
            - Estimated salary range
            - Statistical peers
        """

        # Map player name to stats database name if needed
        stats_name = self.name_mapping.get(player_name, player_name)

        # Find player
        player = self.df_master[self.df_master['Player'] == stats_name]

        if len(player) == 0:
            return {'error': f'Player "{player_name}" not found in stats database (searched as "{stats_name}")'}

        player = player.iloc[0]
        position = player['position_group']
        data_season = int(player['data_season']) if 'data_season' in player else 2025

        print(f"\n{'='*60}")
        print(f"VALUATION: {player_name}")
        print(f"{'='*60}")

        # Display granular position if available, with position_group as backup
        granular_pos = player.get('granular_position', None)
        if granular_pos and pd.notna(granular_pos):
            print(f"Position: {granular_pos} (Group: {position})")
            alt_pos = player.get('alternative_positions', None)
            if alt_pos and pd.notna(alt_pos):
                print(f"Alternative Positions: {alt_pos}")
        else:
            print(f"Position: {position} (FBref group)")

        print(f"Minutes Played: {player['Minutes']:.0f}")
        print(f"Data Season: {data_season}")

        result = {
            'player': player_name,
            'position': position,
            'granular_position': player.get('granular_position', None) if pd.notna(player.get('granular_position', None)) else None,
            'alternative_positions': player.get('alternative_positions', None) if pd.notna(player.get('alternative_positions', None)) else None,
            'minutes': player['Minutes'],
            'data_season': data_season,
            'actual_designation': player['designation_tier'] if 'designation_tier' in player else None,
            'actual_salary': player['base_salary'] if 'base_salary' in player and pd.notna(player['base_salary']) else None
        }

        # Step 1: Predict designation tier
        if position in self.designation_classifiers:
            clf_info = self.designation_classifiers[position]
            features = clf_info['features']
            X = player[features].fillna(0).values.reshape(1, -1)

            predicted_designation = clf_info['model'].predict(X)[0]
            proba = clf_info['model'].predict_proba(X)[0]

            result['predicted_designation'] = predicted_designation
            result['designation_confidence'] = {
                cls: prob for cls, prob in zip(clf_info['model'].classes_, proba)
            }

            print(f"\nPredicted Designation: {predicted_designation}")
            print(f"  Confidence: {max(proba):.1%}")
            for cls, prob in zip(clf_info['model'].classes_, proba):
                print(f"    {cls}: {prob:.1%}")
        else:
            result['predicted_designation'] = player.get('designation_tier', 'Unknown')
            print(f"\nDesignation: {result['predicted_designation']} (actual)")

        # Step 2: Get archetype
        if position in self.archetypes:
            arch_df = self.archetypes[position]
            player_arch = arch_df[arch_df['Player'] == player_name]

            if len(player_arch) > 0:
                archetype = player_arch.iloc[0]['archetype']
                result['archetype'] = int(archetype)
                result['is_outlier'] = archetype == -1

                print(f"\nArchetype: {archetype}")
                if archetype == -1:
                    print(f"  Status: Statistical Outlier (elite/specialist)")
                else:
                    print(f"  Status: Archetype {archetype}")

        # Step 3: Estimate salary range using peers
        player_with_prediction = player.copy()
        if 'predicted_designation' in result:
            player_with_prediction['predicted_designation'] = result['predicted_designation']

        salary_est = self.estimate_salary_range(player_with_prediction)
        result['salary_estimate'] = salary_est

        if 'error' not in salary_est:
            print(f"\nEstimated Salary Range (Base Statistical Model):")
            print(f"  Median: ${salary_est['predicted_salary']/1000:.0f}K")
            print(f"  Range (25th-75th): ${salary_est['salary_range_low']/1000:.0f}K - ${salary_est['salary_range_high']/1000:.0f}K")

            # Show peer matching level
            peer_level = salary_est.get('peer_level', 'position_group')
            if peer_level == 'granular_position':
                print(f"  Peer Match: Granular position ({player.get('granular_position', 'N/A')})")
            else:
                print(f"  Peer Match: Position group ({position})")
            print(f"  Peer Range: ${salary_est['peer_min']/1000:.0f}K - ${salary_est['peer_max']/1000:.0f}K")
            print(f"  Based on {salary_est['n_peers']} similar players")

            print(f"\nTop 5 Statistical Peers:")
            for i, (name, salary) in enumerate(zip(salary_est['peer_names'], salary_est['peer_salaries']), 1):
                print(f"  {i}. {name}: ${salary/1000:.0f}K")

            # Apply age adjustment - parse age from FBref format (e.g., "26-329" = 26 years, 329 days)
            age_value = player.get('Age', '27')
            if pd.notna(age_value):
                # Extract just the year portion (before the hyphen)
                age_str = str(age_value).split('-')[0]
                try:
                    player_age = int(age_str)
                except ValueError:
                    player_age = 27  # Default if parsing fails
            else:
                player_age = 27
            age_factor = self._get_age_adjustment_factor(
                player_age,
                position,
                player.get('granular_position') if pd.notna(player.get('granular_position')) else None
            )

            age_adjusted_salary = salary_est['predicted_salary'] * age_factor
            age_adjusted_low = salary_est['salary_range_low'] * age_factor
            age_adjusted_high = salary_est['salary_range_high'] * age_factor

            print(f"\nAge-Adjusted Valuation (Age {player_age}):")
            print(f"  Adjustment Factor: {age_factor:.2f}x ({(age_factor-1)*100:+.1f}%)")
            print(f"  Recommended Salary: ${age_adjusted_salary/1000:.0f}K")
            print(f"  Adjusted Range: ${age_adjusted_low/1000:.0f}K - ${age_adjusted_high/1000:.0f}K")

            # Store age-adjusted values
            result['age'] = player_age
            result['age_adjustment_factor'] = age_factor
            result['age_adjusted_salary'] = age_adjusted_salary
            result['age_adjusted_range_low'] = age_adjusted_low
            result['age_adjusted_range_high'] = age_adjusted_high

            # Contract structure optimization
            contract_structure = self._optimize_contract_structure(age_adjusted_salary, player_age)
            result['contract_structure'] = contract_structure

            print(f"\nMLS Contract Structure Recommendation:")
            print(f"  {contract_structure['description']}")
            if 'tam_buydown_option' in contract_structure:
                print(f"  {contract_structure['tam_buydown_option']['description']}")

            if result['actual_salary']:
                error = abs(result['actual_salary'] - age_adjusted_salary)
                error_pct = error / result['actual_salary'] * 100
                print(f"\nActual Salary: ${result['actual_salary']/1000:.0f}K")
                print(f"Prediction Error: ${error/1000:.0f}K ({error_pct:.1f}%)")

        return result

    def batch_validate(self, n_samples: int = 20):
        """
        Validate the system on random players
        """

        print("\n" + "="*60)
        print(f"BATCH VALIDATION ({n_samples} players)")
        print("="*60)

        # Sample players with salary data
        df_sample = self.df_master[
            (self.df_master['base_salary'].notna()) &
            (self.df_master['Minutes'] >= 900)
        ].sample(n=min(n_samples, len(self.df_master)), random_state=42)

        results = []

        for _, player in df_sample.iterrows():
            result = self.value_player(player['Player'])

            if 'salary_estimate' in result and 'predicted_salary' in result['salary_estimate']:
                results.append({
                    'player': result['player'],
                    'actual': result['actual_salary'],
                    'predicted': result['salary_estimate']['predicted_salary'],
                    'error': abs(result['actual_salary'] - result['salary_estimate']['predicted_salary']),
                    'error_pct': abs(result['actual_salary'] - result['salary_estimate']['predicted_salary']) / result['actual_salary'] * 100
                })

        if results:
            df_results = pd.DataFrame(results)

            print(f"\n{'='*60}")
            print("VALIDATION SUMMARY")
            print(f"{'='*60}")
            print(f"Mean Absolute Error: ${df_results['error'].mean()/1000:.0f}K")
            print(f"Median Error: ${df_results['error'].median()/1000:.0f}K")
            print(f"Mean Error %: {df_results['error_pct'].mean():.1f}%")
            print(f"Median Error %: {df_results['error_pct'].median():.1f}%")


def main():
    """Main execution"""

    print("="*60)
    print("PLAYER VALUATION SYSTEM")
    print("="*60)

    # Initialize
    system = PlayerValuationSystem()

    # Load data
    system.load_and_merge_data(season=2025)

    # Train designation classifiers
    system.train_designation_classifiers(min_minutes=900)

    # Load archetypes (from previous Contract_Valuation.py run)
    system.load_archetypes()

    # Test valuation on specific players
    test_players = [
        'Lionel Messi',
        'Sergio Busquets',
        'Denis Bouanga',
        'Cucho Hernández',
        'Diego Rossi'
    ]

    print("\n" + "="*60)
    print("TESTING PLAYER VALUATIONS")
    print("="*60)

    for player_name in test_players:
        try:
            result = system.value_player(player_name)
        except Exception as e:
            print(f"\nError valuing {player_name}: {e}")

    # Batch validation
    system.batch_validate(n_samples=15)

    print("\n" + "="*60)
    print("✓ COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()
