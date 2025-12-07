"""
Test script to verify multi-season data loading logic
"""

from Player_Valuation import PlayerValuationSystem

# Initialize system
system = PlayerValuationSystem()

# Load multi-season data
print("Loading data from multiple seasons...")
system.load_and_merge_data(seasons=[2025, 2024, 2023])

# Check a few players to see which season's data is being used
test_players = [
    "Kim Kee-hee",  # Should use 2025 (has 1035 minutes)
    "Paul Rothrock",  # Should use 2025 (regular starter)
]

print("\n" + "="*80)
print("TESTING SEASON SELECTION")
print("="*80)

for player_name in test_players:
    # Look up in master dataframe
    player_data = system.df_master[system.df_master['Player'] == player_name]

    if len(player_data) > 0:
        player = player_data.iloc[0]
        print(f"\n{player_name}:")
        print(f"  Data Season: {player['data_season']}")
        print(f"  Minutes: {player['Minutes']:.0f}")
        print(f"  Position: {player['position_group']}")
    else:
        print(f"\n{player_name}: NOT FOUND")

# Now test the value_player function
print("\n" + "="*80)
print("TESTING VALUATION WITH SEASON TRACKING")
print("="*80)

# Train models first
system.train_designation_classifiers(min_minutes=900)
system.load_archetypes()

# Value Kim Kee-hee
result = system.value_player("Kim Kee-hee")

if 'error' not in result:
    print(f"\nValuation Result:")
    print(f"  Player: {result['player']}")
    print(f"  Data Season: {result['data_season']}")
    print(f"  Minutes: {result['minutes']:.0f}")
    print(f"  Position: {result['position']}")
else:
    print(f"\nError: {result['error']}")
