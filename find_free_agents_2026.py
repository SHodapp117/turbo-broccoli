"""
Script to identify free agents in 2026 from current roster data
"""

import pandas as pd

# Load the 2025 roster data
roster_df = pd.read_csv('data/2025_roster_profiles_parsed.csv')

# Add roster number within each team (sequential order representing cost)
roster_df['roster_number'] = roster_df.groupby('team').cumcount() + 1

# Filter for players whose contracts expire in 2025 (making them free agents in 2026)
# Contract data is stored as strings, so we need to check for strings containing '2025'
# This includes '2025', 'June 2025', 'July 2025', etc.
free_agents_2026 = roster_df[
    roster_df['contract_thru'].notna() &
    roster_df['contract_thru'].astype(str).str.contains('2025', na=False)
].copy()

# Sort by team and name for easier reading
free_agents_2026 = free_agents_2026.sort_values(['team', 'name'])

print("\n" + "="*80)
print("FREE AGENTS IN 2026 (Contracts Expiring End of 2025)")
print("="*80)
print(f"\nTotal Players: {len(free_agents_2026)}")
print("\n" + "-"*80)

# Display by team
for team in free_agents_2026['team'].unique():
    team_players = free_agents_2026[free_agents_2026['team'] == team]
    print(f"\n{team} ({len(team_players)} players):")
    for idx, player in team_players.iterrows():
        designation = player['roster_designation']
        option = f" (Option: {player['option_years']})" if pd.notna(player['option_years']) else ""
        print(f"  - {player['name']} ({designation}){option}")

# Summary by designation type
print("\n" + "="*80)
print("SUMMARY BY DESIGNATION")
print("="*80)
designation_counts = free_agents_2026['roster_designation'].value_counts()
for designation, count in designation_counts.items():
    print(f"  {designation}: {count}")

# Save to CSV for further analysis
output_file = 'data/free_agents_2026.csv'
free_agents_2026.to_csv(output_file, index=False)
print(f"\n\nResults saved to: {output_file}")

# Show players with option years (teams can extend)
print("\n" + "="*80)
print("PLAYERS WITH TEAM OPTIONS")
print("="*80)
players_with_options = free_agents_2026[free_agents_2026['option_years'].notna()]
print(f"\nTotal: {len(players_with_options)} players")
for idx, player in players_with_options.iterrows():
    print(f"  - {player['name']} ({player['team']}) - Option through {player['option_years']}")
