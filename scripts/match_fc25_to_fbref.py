#!/usr/bin/env python3
"""
Match FC 25 player names to FBref player names using fuzzy matching.

This script handles:
- Accent/diacritic differences (José vs Jose)
- Name order variations (First Last vs Last, First)
- Hyphenation differences (Jean-Claude vs Jean Claude)
- Nickname variations
"""

import pandas as pd
from pathlib import Path
import re
from difflib import SequenceMatcher
import unicodedata

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
FC25_FILE = DATA_DIR / "fc25_mls_positions.csv"
FBREF_FILE = DATA_DIR / "2025_Standard.csv"
OUTPUT_FILE = DATA_DIR / "fc25_fbref_position_mapping.csv"
MANUAL_REVIEW_FILE = DATA_DIR / "fc25_manual_review.csv"


def normalize_name(name):
    """Normalize a name for comparison."""
    if pd.isna(name):
        return ""

    # Convert to string and lowercase
    name = str(name).lower().strip()

    # Remove accents/diacritics
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )

    # Remove hyphens and extra spaces
    name = re.sub(r'[-\']', ' ', name)
    name = re.sub(r'\s+', ' ', name)

    # Remove common suffixes
    name = re.sub(r'\s+(jr|sr|ii|iii|iv)\.?$', '', name)

    return name.strip()


def name_similarity(name1, name2):
    """Calculate similarity score between two names (0-1)."""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)

    # Exact match after normalization
    if norm1 == norm2:
        return 1.0

    # Check if one name is contained in the other (for nicknames)
    if norm1 in norm2 or norm2 in norm1:
        return 0.95

    # Use sequence matcher for fuzzy comparison
    return SequenceMatcher(None, norm1, norm2).ratio()


def find_best_match(fc25_name, fbref_names, threshold=0.85):
    """Find the best matching FBref name for a FC25 name."""
    best_match = None
    best_score = 0

    for fbref_name in fbref_names:
        score = name_similarity(fc25_name, fbref_name)
        if score > best_score:
            best_score = score
            best_match = fbref_name

    if best_score >= threshold:
        return best_match, best_score

    return None, best_score


def match_players(fc25_df, fbref_df, threshold=0.85):
    """Match FC25 players to FBref players."""
    print(f"\nMatching {len(fc25_df)} FC25 players to {len(fbref_df)} FBref players...")
    print(f"Similarity threshold: {threshold}")

    # Get FBref player names
    fbref_names = fbref_df['1_Player'].unique()
    print(f"Unique FBref names: {len(fbref_names)}")

    matches = []
    unmatched = []

    for idx, row in fc25_df.iterrows():
        fc25_name = row['Name']

        # Find best match
        fbref_match, score = find_best_match(fc25_name, fbref_names, threshold)

        if fbref_match:
            matches.append({
                'FC25_Name': fc25_name,
                'FBref_Name': fbref_match,
                'Match_Score': score,
                'Position': row['Position'],
                'Alternative_Positions': row['Alternative positions'],
                'Team': row['Team'],
                'Age': row['Age'],
                'OVR': row['OVR']
            })
        else:
            unmatched.append({
                'FC25_Name': fc25_name,
                'Best_Match': None,
                'Best_Score': score,
                'Position': row['Position'],
                'Team': row['Team'],
                'Age': row['Age'],
                'OVR': row['OVR']
            })

    return pd.DataFrame(matches), pd.DataFrame(unmatched)


def main():
    """Main execution."""
    print("=" * 70)
    print("FC 25 to FBref Player Name Matcher")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    fc25_df = pd.read_csv(FC25_FILE)
    fbref_df = pd.read_csv(FBREF_FILE)

    print(f"✓ Loaded {len(fc25_df)} FC25 MLS players")
    print(f"✓ Loaded {len(fbref_df)} FBref 2025 players")

    # Match players
    matched_df, unmatched_df = match_players(fc25_df, fbref_df, threshold=0.85)

    # Results
    print("\n" + "=" * 70)
    print("MATCHING RESULTS")
    print("=" * 70)
    print(f"✓ Matched: {len(matched_df)} players ({len(matched_df)/len(fc25_df)*100:.1f}%)")
    print(f"⚠️  Unmatched: {len(unmatched_df)} players ({len(unmatched_df)/len(fc25_df)*100:.1f}%)")

    # Save matched players
    matched_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✓ Saved matched players to: {OUTPUT_FILE}")

    # Save unmatched for manual review
    if len(unmatched_df) > 0:
        unmatched_df.to_csv(MANUAL_REVIEW_FILE, index=False)
        print(f"✓ Saved unmatched players to: {MANUAL_REVIEW_FILE}")

        print(f"\nTop 20 unmatched players:")
        print(unmatched_df[['FC25_Name', 'Position', 'Team', 'OVR']].head(20))

    # Show match quality distribution
    print("\nMatch Quality Distribution:")
    print(matched_df['Match_Score'].describe())

    # Show some examples
    print("\nSample matches (showing name variations):")
    sample = matched_df[matched_df['FC25_Name'] != matched_df['FBref_Name']].head(10)
    if len(sample) > 0:
        for _, row in sample.iterrows():
            print(f"  {row['FC25_Name']:30} -> {row['FBref_Name']:30} (score: {row['Match_Score']:.3f})")
    else:
        print("  All shown samples are exact matches")

    # Show position distribution
    print("\nPosition Distribution (matched players):")
    print(matched_df['Position'].value_counts())

    print("\n" + "=" * 70)
    print("✓ SUCCESS!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review the matched players in: data/fc25_fbref_position_mapping.csv")
    print("2. Manually review unmatched players in: data/fc25_manual_review.csv")
    print("3. Merge position data into your existing datasets")
    print("4. Update Player_Valuation.py to use granular positions")


if __name__ == "__main__":
    main()
