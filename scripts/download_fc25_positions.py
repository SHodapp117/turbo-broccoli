#!/usr/bin/env python3
"""
Download EA Sports FC 25 player data from Kaggle and extract MLS positions.

Requirements:
    pip install kaggle pandas

Setup:
    1. Create a Kaggle account at https://www.kaggle.com
    2. Go to https://www.kaggle.com/settings/account
    3. Click "Create New Token" - downloads kaggle.json
    4. Move kaggle.json to ~/.kaggle/ (create directory if needed)
    5. chmod 600 ~/.kaggle/kaggle.json
"""

import os
import pandas as pd
import json
from pathlib import Path

# Kaggle dataset identifier
DATASET = "nyagami/ea-sports-fc-25-database-ratings-and-stats"

# Output paths
DATA_DIR = Path(__file__).parent.parent / "data"
FC25_DIR = DATA_DIR / "fc25"
FC25_DIR.mkdir(exist_ok=True)

MLS_TEAMS = [
    "Atlanta United", "Austin FC", "Charlotte FC", "Chicago Fire",
    "FC Cincinnati", "Colorado Rapids", "Columbus Crew", "FC Dallas",
    "D.C. United", "Houston Dynamo", "Sporting Kansas City", "LA Galaxy",
    "Los Angeles FC", "Inter Miami CF", "Minnesota United", "CF Montréal",
    "Nashville SC", "New England Revolution", "New York City FC", "New York Red Bulls",
    "Orlando City", "Philadelphia Union", "Portland Timbers", "Real Salt Lake",
    "San Jose Earthquakes", "Seattle Sounders FC", "St. Louis City SC",
    "Toronto FC", "Vancouver Whitecaps FC"
]


def download_dataset():
    """Download EA Sports FC 25 dataset from Kaggle."""
    print("Downloading EA Sports FC 25 dataset from Kaggle...")

    try:
        import kaggle
    except ImportError:
        print("❌ Error: kaggle package not installed.")
        print("   Run: pip install kaggle")
        return False

    # Check if kaggle.json exists
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print("❌ Error: Kaggle credentials not found.")
        print("   Setup instructions:")
        print("   1. Go to https://www.kaggle.com/settings/account")
        print("   2. Click 'Create New Token' - downloads kaggle.json")
        print(f"   3. Move kaggle.json to {kaggle_json.parent}")
        print(f"   4. chmod 600 {kaggle_json}")
        return False

    try:
        kaggle.api.dataset_download_files(
            DATASET,
            path=FC25_DIR,
            unzip=True
        )
        print(f"✓ Dataset downloaded to {FC25_DIR}")
        return True
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return False


def find_dataset_file():
    """Find the main player data CSV file."""
    csv_files = list(FC25_DIR.glob("*.csv"))

    if not csv_files:
        print("❌ No CSV files found in dataset")
        return None

    # Look for files with 'player' or 'male' in the name
    for csv_file in csv_files:
        name_lower = csv_file.name.lower()
        if 'player' in name_lower or 'male' in name_lower:
            print(f"✓ Found player data: {csv_file.name}")
            return csv_file

    # If no specific file found, use the first/largest one
    largest = max(csv_files, key=lambda f: f.stat().st_size)
    print(f"✓ Using largest CSV: {largest.name}")
    return largest


def extract_mls_positions(csv_file):
    """Extract position data for MLS players."""
    print(f"\nReading {csv_file.name}...")

    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None

    print(f"Total players in dataset: {len(df):,}")
    print(f"\nColumns in dataset: {df.columns.tolist()}")

    # Find position-related columns
    position_cols = [col for col in df.columns if 'position' in col.lower() or 'pos' in col.lower()]
    print(f"\nPosition columns found: {position_cols}")

    # Find team/league columns
    team_cols = [col for col in df.columns if any(x in col.lower() for x in ['team', 'club', 'league'])]
    print(f"Team/League columns found: {team_cols}")

    # Try to filter for MLS players
    mls_df = None

    # Check if there's a league column
    if 'League' in df.columns or 'league' in df.columns:
        league_col = 'League' if 'League' in df.columns else 'league'
        mls_df = df[df[league_col].str.contains('MLS', case=False, na=False)]
        print(f"\n✓ Found {len(mls_df)} MLS players (filtered by league)")

    # Check if there's a team column
    elif 'Team' in df.columns or 'team' in df.columns or 'Club' in df.columns:
        team_col = 'Team' if 'Team' in df.columns else ('team' if 'team' in df.columns else 'Club')
        mls_df = df[df[team_col].isin(MLS_TEAMS)]
        print(f"\n✓ Found {len(mls_df)} MLS players (filtered by team)")

    if mls_df is None or len(mls_df) == 0:
        print("\n⚠️  Could not filter for MLS players automatically.")
        print("    Saving full dataset for manual filtering.")
        mls_df = df

    # Save the MLS player positions
    output_file = DATA_DIR / "fc25_mls_positions.csv"

    # Select relevant columns (name, position, team, etc.)
    name_cols = [col for col in df.columns if 'name' in col.lower()]
    keep_cols = name_cols + position_cols + team_cols + ['Age'] if 'Age' in df.columns else []
    keep_cols = [col for col in keep_cols if col in mls_df.columns]

    mls_positions = mls_df[keep_cols].copy()
    mls_positions.to_csv(output_file, index=False)

    print(f"\n✓ Saved MLS positions to: {output_file}")
    print(f"  Total players: {len(mls_positions)}")
    print(f"\nSample data:")
    print(mls_positions.head(10))

    # Show position distribution
    if position_cols:
        main_pos_col = position_cols[0]
        print(f"\nPosition distribution ({main_pos_col}):")
        print(mls_positions[main_pos_col].value_counts())

    return mls_positions


def main():
    """Main execution."""
    print("=" * 60)
    print("EA SPORTS FC 25 - MLS Position Data Extractor")
    print("=" * 60)

    # Check if dataset already downloaded
    csv_files = list(FC25_DIR.glob("*.csv"))

    if csv_files:
        print(f"\n✓ Dataset already exists in {FC25_DIR}")
        response = input("Re-download? (y/N): ").strip().lower()
        if response == 'y':
            if not download_dataset():
                return
    else:
        if not download_dataset():
            return

    # Find and process the dataset
    csv_file = find_dataset_file()
    if not csv_file:
        return

    # Extract MLS positions
    mls_positions = extract_mls_positions(csv_file)

    if mls_positions is not None:
        print("\n" + "=" * 60)
        print("✓ SUCCESS! MLS position data extracted.")
        print("=" * 60)
        print(f"\nNext steps:")
        print(f"1. Review the output file: data/fc25_mls_positions.csv")
        print(f"2. Run the name mapping script to match with your FBref data")
        print(f"3. Update Player_Valuation.py to use granular positions")


if __name__ == "__main__":
    main()
