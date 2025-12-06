"""
MLS Player Clustering Analysis

Uses DBSCAN to discover player archetypes based on:
- Performance statistics (goals, assists, defensive actions, etc.)
- Position (FW, MF, DF, GK)
- Roster designation (DP, U22, TAM, Homegrown)

DBSCAN advantages:
- Discovers natural number of clusters
- Identifies outliers (superstars, specialists)
- Handles non-spherical cluster shapes
- No assumption about cluster sizes
"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class PlayerClusteringAnalysis:
    """
    Cluster MLS players using DBSCAN to discover archetypes
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent / 'data'
        else:
            self.data_dir = Path(data_dir)

        self.output_dir = self.data_dir / 'clustering'
        self.output_dir.mkdir(exist_ok=True)

        self.df = None
        self.df_clustered = None
        self.scaler = StandardScaler()
        self.pca = None

    def load_data(self, season: int = 2025, min_minutes: int = 90):
        """
        Load player data and merge with roster designations

        Args:
            season: Season to analyze
            min_minutes: Minimum minutes played to include player
        """
        print(f"Loading {season} season data...")

        # Load stats
        stats_file = self.data_dir / 'scd2' / f'ml_current_season_{season}.parquet'
        if not stats_file.exists():
            # Fallback to processed CSV
            stats_file = self.data_dir / 'processed' / f'{season}_all_stats.csv'
            df_stats = pd.read_csv(stats_file)
        else:
            df_stats = pd.read_parquet(stats_file)

        # Filter by minutes played
        df_stats = df_stats[df_stats['Minutes'] >= min_minutes].copy()

        # Load roster designations
        roster_file = self.data_dir / f'{season}_roster_profiles_parsed.csv'
        if roster_file.exists():
            df_roster = pd.read_csv(roster_file)

            # Merge on player name (fuzzy matching could improve this)
            df_stats = df_stats.merge(
                df_roster[['name', 'roster_designation', 'category']],
                left_on='Player',
                right_on='name',
                how='left'
            )
            print(f"  Merged roster designations: {df_stats['category'].notna().sum()} matches")
        else:
            print(f"  Warning: Roster file not found, proceeding without designations")
            df_stats['roster_designation'] = None
            df_stats['category'] = 'Unknown'

        self.df = df_stats
        print(f"  Loaded {len(self.df)} players with {min_minutes}+ minutes")

        return self.df

    def select_features_by_position(self, position_group: str) -> List[str]:
        """
        Select relevant features based on position group

        Args:
            position_group: 'FW', 'MF', 'DF', or 'GK'

        Returns:
            List of feature column names
        """
        # Common features for all outfield players
        common_features = [
            'Goals', 'Assists', 'xG', 'npxG', 'xAG',
            'Minutes', '90s Played90s played'
        ]

        # Position-specific features
        position_features = {
            'FW': [
                'Gls', 'Sh', 'SoT', 'SoT%', 'G/Sh', 'G/SoT',
                'PrgC', 'PrgR',  # Progressive carries/runs
            ],
            'MF': [
                'Ast', 'KP', 'PrgP', 'PPA',  # Passing
                'Cmp', 'Cmp%', 'xAG',  # Pass completion
                'PrgC', 'PrgR',  # Ball progression
            ],
            'DF': [
                'Tkl', 'TklW', 'Blocks', 'Int', 'Clr',  # Defensive actions
                'PrgP',  # Progressive passes from back
            ],
            'GK': [
                'GA', 'SoTA', 'Saves', 'Save%', 'CS', 'CS%',
                'PSxG', 'PSxG/SoT', 'PSxG+/-'
            ]
        }

        # Get features for this position
        if position_group == 'GK':
            return position_features['GK']
        else:
            features = common_features.copy()
            features.extend(position_features.get(position_group, []))
            return features

    def prepare_clustering_data(self, position_filter: str = None) -> pd.DataFrame:
        """
        Prepare data for clustering by selecting features and scaling

        Args:
            position_filter: Filter to specific position group (FW, MF, DF, GK)
                           If None, clusters all outfield players together

        Returns:
            DataFrame with scaled features
        """
        print(f"\nPreparing data for clustering...")

        # Filter by position if specified
        if position_filter:
            if position_filter == 'GK':
                df_filtered = self.df[self.df['Pos'].str.contains('GK', na=False)].copy()
            else:
                df_filtered = self.df[self.df['Pos'].str.contains(position_filter, na=False)].copy()
            print(f"  Filtered to {len(df_filtered)} {position_filter} players")
        else:
            # Exclude goalkeepers for outfield clustering
            df_filtered = self.df[~self.df['Pos'].str.contains('GK', na=False)].copy()
            print(f"  Using {len(df_filtered)} outfield players")

        # Select features
        if position_filter:
            feature_cols = self.select_features_by_position(position_filter)
        else:
            # General outfield features
            feature_cols = [
                'Goals', 'Assists', 'xG', 'npxG', 'xAG',
                'Minutes', 'Sh', 'SoT', 'Cmp', 'PrgP', 'PrgC',
                'Tkl', 'Int', 'Blocks'
            ]

        # Filter to available columns
        available_features = [f for f in feature_cols if f in df_filtered.columns]
        print(f"  Using {len(available_features)} features: {', '.join(available_features[:5])}...")

        # Extract features and handle missing values
        X = df_filtered[available_features].fillna(0)

        # Normalize per 90 minutes for fair comparison
        if '90s Played90s played' in X.columns:
            minutes_col = '90s Played90s played'
        elif '90s' in X.columns:
            minutes_col = '90s'
        else:
            minutes_col = None

        if minutes_col and minutes_col in X.columns:
            # Don't normalize minutes itself
            cols_to_normalize = [c for c in X.columns if c != minutes_col]
            for col in cols_to_normalize:
                X[col] = X[col].div(X[minutes_col], axis=0).replace([np.inf, -np.inf], 0)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Store for later
        df_filtered['_features'] = list(X_scaled)

        return df_filtered

    def perform_dbscan(
        self,
        df_filtered: pd.DataFrame,
        eps: float = 0.5,
        min_samples: int = 5,
        metric: str = 'euclidean'
    ) -> pd.DataFrame:
        """
        Perform DBSCAN clustering

        Args:
            df_filtered: DataFrame with prepared features
            eps: Maximum distance between samples for core points
            min_samples: Minimum samples in neighborhood for core point
            metric: Distance metric

        Returns:
            DataFrame with cluster labels
        """
        print(f"\nPerforming DBSCAN clustering...")
        print(f"  Parameters: eps={eps}, min_samples={min_samples}, metric={metric}")

        # Extract scaled features
        X_scaled = np.vstack(df_filtered['_features'].values)

        # Run DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
        df_filtered['cluster'] = dbscan.fit_predict(X_scaled)

        # Analyze results
        n_clusters = len(set(df_filtered['cluster'])) - (1 if -1 in df_filtered['cluster'] else 0)
        n_noise = list(df_filtered['cluster']).count(-1)

        print(f"\n  Results:")
        print(f"    Clusters found: {n_clusters}")
        print(f"    Noise points (outliers): {n_noise}")

        if n_clusters > 0:
            cluster_sizes = df_filtered[df_filtered['cluster'] != -1]['cluster'].value_counts().sort_index()
            print(f"    Cluster sizes:")
            for cluster_id, size in cluster_sizes.items():
                print(f"      Cluster {cluster_id}: {size} players")

        return df_filtered

    def analyze_clusters(self, df_clustered: pd.DataFrame) -> Dict:
        """
        Analyze cluster characteristics

        Args:
            df_clustered: DataFrame with cluster assignments

        Returns:
            Dictionary with cluster analysis
        """
        print("\n" + "="*60)
        print("CLUSTER ANALYSIS")
        print("="*60)

        analysis = {}

        # Analyze each cluster
        for cluster_id in sorted(df_clustered['cluster'].unique()):
            if cluster_id == -1:
                cluster_name = "Outliers/Noise"
            else:
                cluster_name = f"Cluster {cluster_id}"

            cluster_data = df_clustered[df_clustered['cluster'] == cluster_id]

            print(f"\n{cluster_name} ({len(cluster_data)} players)")
            print("-" * 60)

            # Position distribution
            if 'Pos' in cluster_data.columns:
                pos_dist = cluster_data['Pos'].value_counts().head(3)
                print(f"  Top positions: {dict(pos_dist)}")

            # Roster designation distribution
            if 'category' in cluster_data.columns:
                cat_dist = cluster_data['category'].value_counts().head(3)
                print(f"  Designations: {dict(cat_dist)}")

            # Average stats
            stat_cols = ['Goals', 'Assists', 'xG', 'Minutes']
            available_stats = [c for c in stat_cols if c in cluster_data.columns]
            if available_stats:
                avg_stats = cluster_data[available_stats].mean()
                print(f"  Avg stats:")
                for stat, value in avg_stats.items():
                    print(f"    {stat}: {value:.2f}")

            # Top players in cluster
            if cluster_id != -1 and 'Goals' in cluster_data.columns:
                top_players = cluster_data.nlargest(3, 'Goals')[['Player', 'Squad', 'Pos', 'Goals', 'Assists']]
                print(f"  Top players:")
                for _, player in top_players.iterrows():
                    print(f"    {player['Player']} ({player['Squad']}) - {player['Pos']}: {player['Goals']:.1f}G, {player['Assists']:.1f}A")

            analysis[cluster_id] = {
                'size': len(cluster_data),
                'avg_stats': avg_stats.to_dict() if available_stats else {},
                'positions': pos_dist.to_dict() if 'Pos' in cluster_data.columns else {},
                'categories': cat_dist.to_dict() if 'category' in cluster_data.columns else {}
            }

        return analysis

    def visualize_clusters(self, df_clustered: pd.DataFrame, position_label: str = "All"):
        """
        Create visualizations of clusters using PCA

        Args:
            df_clustered: DataFrame with cluster assignments
            position_label: Label for the plot
        """
        print("\nCreating visualizations...")

        # Extract scaled features
        X_scaled = np.vstack(df_clustered['_features'].values)

        # PCA for visualization (2D)
        self.pca = PCA(n_components=2)
        X_pca = self.pca.fit_transform(X_scaled)

        df_clustered['pca1'] = X_pca[:, 0]
        df_clustered['pca2'] = X_pca[:, 1]

        # Create figure with subplots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Plot 1: Clusters colored by DBSCAN assignment
        scatter = axes[0].scatter(
            df_clustered['pca1'],
            df_clustered['pca2'],
            c=df_clustered['cluster'],
            cmap='viridis',
            alpha=0.6,
            s=100,
            edgecolors='black',
            linewidths=0.5
        )
        axes[0].set_xlabel(f'PC1 ({self.pca.explained_variance_ratio_[0]:.1%} variance)')
        axes[0].set_ylabel(f'PC2 ({self.pca.explained_variance_ratio_[1]:.1%} variance)')
        axes[0].set_title(f'DBSCAN Clusters - {position_label} Players')
        plt.colorbar(scatter, ax=axes[0], label='Cluster')

        # Annotate outliers
        outliers = df_clustered[df_clustered['cluster'] == -1]
        if len(outliers) > 0 and len(outliers) < 20:
            for _, player in outliers.iterrows():
                axes[0].annotate(
                    player['Player'],
                    (player['pca1'], player['pca2']),
                    fontsize=8,
                    alpha=0.7
                )

        # Plot 2: Colored by roster designation (if available)
        if 'category' in df_clustered.columns and df_clustered['category'].notna().any():
            categories = df_clustered['category'].fillna('Unknown')
            unique_cats = categories.unique()
            colors = sns.color_palette('Set2', len(unique_cats))
            cat_colors = {cat: colors[i] for i, cat in enumerate(unique_cats)}

            for cat in unique_cats:
                mask = categories == cat
                axes[1].scatter(
                    df_clustered.loc[mask, 'pca1'],
                    df_clustered.loc[mask, 'pca2'],
                    c=[cat_colors[cat]],
                    label=cat,
                    alpha=0.6,
                    s=100,
                    edgecolors='black',
                    linewidths=0.5
                )

            axes[1].set_xlabel(f'PC1 ({self.pca.explained_variance_ratio_[0]:.1%} variance)')
            axes[1].set_ylabel(f'PC2 ({self.pca.explained_variance_ratio_[1]:.1%} variance)')
            axes[1].set_title(f'Players by Roster Designation - {position_label}')
            axes[1].legend(loc='best', fontsize=8)
        else:
            axes[1].text(0.5, 0.5, 'Roster designation data not available',
                        ha='center', va='center', transform=axes[1].transAxes)

        plt.tight_layout()
        output_file = self.output_dir / f'clusters_{position_label.lower()}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"  Saved visualization: {output_file}")

        return fig

    def find_optimal_eps(self, df_filtered: pd.DataFrame, k: int = 5):
        """
        Find optimal eps parameter using k-distance graph

        Args:
            df_filtered: Prepared data
            k: Number of nearest neighbors (typically = min_samples)

        Returns:
            Suggested eps value
        """
        from sklearn.neighbors import NearestNeighbors

        print("\nFinding optimal eps parameter...")

        X_scaled = np.vstack(df_filtered['_features'].values)

        # Compute k-nearest neighbors
        neighbors = NearestNeighbors(n_neighbors=k)
        neighbors.fit(X_scaled)
        distances, indices = neighbors.kneighbors(X_scaled)

        # Sort distances
        k_distances = np.sort(distances[:, k-1])

        # Plot k-distance graph
        plt.figure(figsize=(10, 6))
        plt.plot(k_distances)
        plt.xlabel('Points sorted by distance')
        plt.ylabel(f'{k}-NN Distance')
        plt.title('K-Distance Graph (Elbow = Optimal Eps)')
        plt.grid(True, alpha=0.3)

        output_file = self.output_dir / 'eps_optimization.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"  Saved k-distance graph: {output_file}")

        # Suggest eps as 90th percentile
        suggested_eps = np.percentile(k_distances, 90)
        print(f"  Suggested eps: {suggested_eps:.3f} (90th percentile)")

        return suggested_eps


def main():
    """Main execution"""

    print("="*60)
    print("MLS PLAYER CLUSTERING ANALYSIS (DBSCAN)")
    print("="*60)

    # Initialize
    analyzer = PlayerClusteringAnalysis()

    # Load data
    df = analyzer.load_data(season=2025, min_minutes=270)  # ~3 full games

    # Analysis 1: Cluster all outfield players
    print("\n" + "="*60)
    print("CLUSTERING: ALL OUTFIELD PLAYERS")
    print("="*60)

    df_outfield = analyzer.prepare_clustering_data(position_filter=None)

    # Find optimal eps
    suggested_eps = analyzer.find_optimal_eps(df_outfield, k=5)

    # Run DBSCAN
    df_clustered = analyzer.perform_dbscan(
        df_outfield,
        eps=suggested_eps * 0.8,  # Slightly tighter than suggested
        min_samples=5
    )

    # Analyze
    analysis = analyzer.analyze_clusters(df_clustered)

    # Visualize
    analyzer.visualize_clusters(df_clustered, position_label="Outfield")

    # Analysis 2: Cluster forwards separately
    print("\n" + "="*60)
    print("CLUSTERING: FORWARDS ONLY")
    print("="*60)

    df_forwards = analyzer.prepare_clustering_data(position_filter='FW')

    if len(df_forwards) >= 15:  # Need enough players
        eps_fw = analyzer.find_optimal_eps(df_forwards, k=4)

        df_fw_clustered = analyzer.perform_dbscan(
            df_forwards,
            eps=eps_fw * 0.7,
            min_samples=4
        )

        analyzer.analyze_clusters(df_fw_clustered)
        analyzer.visualize_clusters(df_fw_clustered, position_label="Forwards")
    else:
        print("  Not enough forwards for separate clustering")

    # Analysis 3: Cluster midfielders separately
    print("\n" + "="*60)
    print("CLUSTERING: MIDFIELDERS ONLY")
    print("="*60)

    df_midfielders = analyzer.prepare_clustering_data(position_filter='MF')

    if len(df_midfielders) >= 15:
        eps_mf = analyzer.find_optimal_eps(df_midfielders, k=4)

        df_mf_clustered = analyzer.perform_dbscan(
            df_midfielders,
            eps=eps_mf * 0.7,
            min_samples=4
        )

        analyzer.analyze_clusters(df_mf_clustered)
        analyzer.visualize_clusters(df_mf_clustered, position_label="Midfielders")
    else:
        print("  Not enough midfielders for separate clustering")

    # Save results
    output_file = analyzer.output_dir / 'clustered_players_2025.csv'
    df_clustered.to_csv(output_file, index=False)
    print(f"\n✓ Saved clustered data: {output_file}")

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print(f"\nOutputs saved to: {analyzer.output_dir}")
    print("  - Cluster visualizations (PNG)")
    print("  - Eps optimization graphs (PNG)")
    print("  - Clustered player data (CSV)")


if __name__ == '__main__':
    main()
