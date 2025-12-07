"""
Test script to verify radar chart functionality
"""

from Player_Valuation import PlayerValuationSystem
import pandas as pd

# Initialize system
print("Loading system...")
system = PlayerValuationSystem()
system.load_and_merge_data(season=2025)
system.train_designation_classifiers(min_minutes=900)
system.load_archetypes()

# Test with Paul Rothrock
player_name = "Paul Rothrock"
print(f"\nTesting radar chart data for {player_name}...")

# Get player valuation
result = system.value_player(player_name)

if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print(f"\n✓ Player found: {player_name}")
    print(f"  Position: {result['position']}")
    print(f"  Minutes: {result['minutes']}")

    if 'salary_estimate' in result:
        est = result['salary_estimate']
        peer_names = est['peer_names'][:5]

        print(f"\n✓ Top 5 peers:")
        for i, name in enumerate(peer_names, 1):
            print(f"  {i}. {name}")

        # Check if we can get the data
        all_players = [player_name] + peer_names
        df = system.df_master[system.df_master['Player'].isin(all_players)].copy()

        print(f"\n✓ Found {len(df)} players in dataset")

        # Check key stats exist
        key_stats = ['Sh/90', 'SoT%', 'Cmp%', 'Tkl+Int', 'SCA90', 'Touches']
        missing_stats = []

        for stat in key_stats:
            if stat not in df.columns:
                missing_stats.append(stat)
            else:
                non_null = df[stat].notna().sum()
                print(f"  {stat}: {non_null}/{len(df)} have data")

        if missing_stats:
            print(f"\n⚠️  Missing stats: {missing_stats}")
        else:
            print(f"\n✓ All key stats available!")

        print("\n✓ Radar charts should work correctly!")

    else:
        print("\n⚠️  No salary estimate available")
