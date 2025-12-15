"""
MLS Free Agent Contract Valuation App - Streamlit Interface

Interactive application to value 2026 MLS free agents and see their statistical peers.
"""

import streamlit as st
import pandas as pd
import numpy as np
from Player_Valuation import PlayerValuationSystem
import plotly.express as px
import plotly.graph_objects as go

# Helper function for consistent salary formatting
def format_salary(salary):
    """Format salary consistently - K for thousands, M for millions"""
    if salary is None:
        return "N/A"
    if salary >= 1_000_000:
        return f"${salary/1_000_000:.2f}M"
    else:
        return f"${salary/1000:.0f}K"

def safe_max(*values):
    """Safely find max value, filtering out None values and NaN"""
    filtered = []
    for v in values:
        if v is not None and not (isinstance(v, float) and pd.isna(v)):
            filtered.append(v)
    return max(filtered) if filtered else 0

def ordinal(n):
    """Convert number to ordinal string (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{int(n)}{suffix}"

def clean_stat_name(stat_name):
    """Convert abbreviated stat names to readable versions"""
    # Mapping of common FBref abbreviations to readable names
    stat_mapping = {
        # Aerial/Physical
        'Lost': 'Aerials Lost',
        'Won': 'Aerials Won',
        'Won%': 'Aerial Win %',

        # Possession/Dribbling
        'DIs': 'Dispossessed',
        'Mis': 'Miscontrols',
        'Succ': 'Successful Dribbles',
        'Succ%': 'Dribble Success %',
        'Att': 'Dribble Attempts',

        # Defensive
        'Tkl': 'Tackles',
        'TklW': 'Tackles Won',
        'Tkl%': 'Tackle Success %',
        'Def 3rd': 'Tackles Def 3rd',
        'Mid 3rd': 'Tackles Mid 3rd',
        'Att 3rd': 'Tackles Att 3rd',
        'Int': 'Interceptions',
        'Tkl+Int': 'Tackles + Interceptions',
        'Clr': 'Clearances',
        'Err': 'Errors',

        # Passing
        'Cmp': 'Passes Completed',
        'Cmp%': 'Pass Completion %',
        'Cmp%.1': 'Medium Pass %',
        'Att.1': 'Pass Attempts',
        'Prg': 'Progressive Passes',
        'KP': 'Key Passes',
        'PPA': 'Passes to Penalty Area',
        'CrsPA': 'Crosses to Penalty Area',

        # Shooting
        'Sh': 'Shots',
        'Sh/90': 'Shots per 90',
        'SoT': 'Shots on Target',
        'SoT%': 'Shot Accuracy %',
        'G/Sh': 'Goals per Shot',
        'G/SoT': 'Goals per Shot on Target',
        'Dist': 'Shot Distance',
        'FK': 'Free Kick Shots',

        # Creation
        'SCA': 'Shot Creating Actions',
        'SCA90': 'Shot Creating Actions per 90',
        'GCA': 'Goal Creating Actions',
        'GCA90': 'Goal Creating Actions per 90',

        # Carries
        'PrgC': 'Progressive Carries',
        'CPA': 'Carries to Penalty Area',
        'PrgDist': 'Progressive Carry Distance',

        # Expected Stats
        'xG': 'Expected Goals',
        'npxG': 'Non-Penalty xG',
        'npxG/Sh': 'npxG per Shot',
        'xAG': 'Expected Assisted Goals',
        'xA': 'Expected Assists',

        # Goalkeeper
        'GA': 'Goals Against',
        'SoTA': 'Shots on Target Against',
        'Save%': 'Save %',
        'PSxG': 'Post-Shot xG',
        'PSxG-GA': 'PSxG minus Goals Against',
        'PSxG-GA/90': 'PSxG-GA per 90',
        '#OPA': 'Defensive Actions Outside Penalty',
        '#OPA/90': 'Defensive Actions Outside Penalty per 90',
        'Avg.6': 'Average Distance of Def Actions',
        'Stp': 'Crosses Stopped',
        'Stp%': 'Cross Stop %',
        'Launch%': 'Launch %',
        'Launch%.1': 'Goal Kick Launch %',
        'Launch%.2': 'Def 3rd Launch %',
        'Avg': 'Average Pass Length',
        'Avg.1': 'Goal Kick Avg Length',
        'Avg.3': 'Def 3rd Avg Length',
        'Att (GK)': 'Pass Attempts',

        # General
        'Tot': 'Total Passes',
        'Blocks': 'Blocks',
        'Touches': 'Touches',
        'Carries': 'Carries',
        'Ball Recoveries': 'Ball Recoveries',
        'Recov': 'Ball Recoveries',

        # Additional common abbreviations
        'Ast': 'Assists',
        'CK': 'Corner Kicks',
        'Fls': 'Fouls Committed',
        'Fld': 'Fouls Drawn',
        'Off': 'Offsides',
        'Offsides': 'Offsides',
        'PKwon': 'Penalties Won',
        'PKcon': 'Penalties Conceded',
        'OG': 'Own Goals',
        'CrdY': 'Yellow Cards',
        'CrdR': 'Red Cards',
        '2CrdY': 'Second Yellow Cards',
        'Gls': 'Goals',
        'PKatt': 'Penalty Kicks Attempted',
        'PK': 'Penalty Kicks Made',
        'PKA': 'Penalty Kicks Allowed',
        '1/3': 'Passes into Final Third',
        'PrgP': 'Progressive Passes',
        'PrgR': 'Progressive Passes Received',
        'Live': 'Live-Ball Passes',
        'Dead': 'Dead-Ball Passes',
        'TB': 'Through Balls',
        'Sw': 'Switches',
        'Crs': 'Crosses',
        'Crosses': 'Crosses',
        'TI': 'Throw-Ins',
        'Press': 'Pressures',
        'Def Pen': 'Defensive Penalty Area Touches',
        'Def 3rd.1': 'Defensive 3rd Touches',
        'Mid 3rd.1': 'Middle 3rd Touches',
        'Att Pen': 'Attacking Penalty Area Touches',
        'Att 3rd.1': 'Attacking 3rd Touches',

        # Dribbling/Possession
        'Tkld': 'Times Tackled',
        'Tkld%': 'Tackled %',
        'Rec': 'Passes Received',
        'Dis': 'Distance Carried',
        'TO': 'Turnovers',
        'Thr': 'Passes Received Through Balls',

        # Defensive variants
        'Def': 'Defensive Actions',
        'TklW': 'Tackles Won',
        'Pass': 'Passes Allowed',
        'Opp': 'Opponent Actions'
    }

    # Return mapped name if exists, otherwise return original
    return stat_mapping.get(stat_name, stat_name)

def get_salary_axis_config(max_salary):
    """
    Determine appropriate axis scaling and label for salary charts.
    Returns (divisor, label) tuple.
    """
    # Handle None or 0 values
    if max_salary is None or max_salary == 0:
        return 1_000, "Salary ($K)"

    if max_salary >= 1_000_000:
        return 1_000_000, "Salary ($M)"
    else:
        return 1_000, "Salary ($K)"

# Page config
st.set_page_config(
    page_title="MLS Free Agent Valuator",
    layout="wide"
)

# Cache the system initialization
@st.cache_resource
def load_valuation_system():
    """Load and initialize the valuation system"""
    with st.spinner("Loading player data and training models..."):
        system = PlayerValuationSystem()
        # Load multi-season data with fallback logic
        system.load_and_merge_data(seasons=[2025, 2024, 2023])
        system.train_designation_classifiers(min_minutes=900)
        system.load_archetypes()
    return system

# Load free agents data
@st.cache_data
def load_free_agents():
    """Load the free agents dataset"""
    try:
        fa_df = pd.read_csv('data/free_agents_2026.csv')
        # Sort by team and name
        fa_df = fa_df.sort_values(['team', 'name'])
        return fa_df
    except FileNotFoundError:
        st.error("Free agents data not found. Please run find_free_agents_2026.py first.")
        return None

def get_peer_comparison_data(system, player_name, peer_names):
    """Get detailed stats for player and peers for radar charts"""

    # Get all players (selected + peers)
    all_players = [player_name] + peer_names

    # Filter dataframe
    df = system.df_master[system.df_master['Player'].isin(all_players)].copy()

    if len(df) == 0:
        return None

    # Check if player is a goalkeeper
    player_matches = df[df['Player'] == player_name]
    if len(player_matches) == 0:
        return None
    player_row = player_matches.iloc[0]
    is_gk = player_row['Pos'] == 'GK' if 'Pos' in df.columns else False

    # Define stat categories for radar charts
    if is_gk:
        # GK-specific stat categories
        stat_categories = {
            'Shot Stopping': {
                'stats': ['Post-Shot Expected Goals', 'PSxG-GAPost-Shot Expected Goals minus Goals AllowedPositive numbers suggest better luck or an above average ability to stop shotsPSxG is expected goals based on how likely the goalkeeper is to save the shotNote', 'PSxG-GA/90Post-Shot Expected Goals minus Goals Allowed per 90 minutesPositive numbers suggest better luck or an above average ability to stop shotsPSxG is expected goals based on how likely the goalkeeper is to save the shotNote', 'GA', 'Post-Shot Expected Goals per Shot on Target'],
                'labels': ['PSxG', 'PSxG-GA', 'PSxG-GA/90', 'Goals Against', 'PSxG per SoT']
            },
            'Distribution': {
                'stats': ['Cmp%', 'Prg', 'Launch%', 'Avg', 'Tot'],
                'labels': ['Pass Accuracy', 'Progressive Passes', 'Launch %', 'Avg Pass Length', 'Total Passes']
            },
            'Sweeping': {
                'stats': ['#OPA', '#OPA/90', 'Avg.6', 'Stp', 'Stp%'],
                'labels': ['Def Actions Outside Pen', 'Def Actions/90', 'Avg Distance', 'Crosses Stopped', 'Cross Stop %']
            },
            'Passing Under Pressure': {
                'stats': ['Att (GK)', 'Launch%.1', 'Avg.1', 'Launch%.2', 'Avg.3'],
                'labels': ['Pass Attempts', 'Goal Kick Launch %', 'GK Avg Length', 'Def 3rd Launch %', 'Def 3rd Avg Length']
            }
        }
    else:
        # Outfield player stat categories
        stat_categories = {
            'Shooting': {
                'stats': ['Sh/90', 'SoT%', 'G/Sh', 'npxG/Shot', 'xG'],
                'labels': ['Shots/90', 'Shot Accuracy', 'Goal Conversion', 'npxG/Shot', 'xG']
            },
            'Passing': {
                'stats': ['Cmp%', 'Prg', 'KP', 'xA', 'Cmp%.1'],  # Total, Progressive, Key Passes, xA, Medium passes
                'labels': ['Pass Accuracy', 'Progressive Passes', 'Key Passes', 'xA', 'Medium Pass %']
            },
            'Possession': {
                'stats': ['Touches', 'Succ%', 'Carries', 'PrgC', 'CPA'],
                'labels': ['Touches', 'Dribble Success', 'Carries', 'Progressive Carries', 'Carries to Penalty']
            },
            'Defensive': {
                'stats': ['Tkl+Int', 'Tkl%', 'Blocks', 'Int', 'Ball Recoveries'],
                'labels': ['Tackles+Int', 'Tackle Success', 'Blocks', 'Interceptions', 'Ball Recoveries']
            },
            'Creation': {
                'stats': ['SCA90', 'GCA90', 'xAG', 'PPA', 'CrsPA'],
                'labels': ['Shot Creating/90', 'Goal Creating/90', 'xAG', 'Passes to Penalty', 'Crosses to Penalty']
            }
        }

    return df, stat_categories

def get_position_comparison_data(system, player_name):
    """Get all players in the same position for league-wide radar charts"""

    # Get the player's position
    player_matches = system.df_master[system.df_master['Player'] == player_name]
    if len(player_matches) == 0:
        return None

    player_row = player_matches.iloc[0]
    is_gk = player_row['Pos'] == 'GK' if 'Pos' in player_row else False

    # Try to get granular position first, fallback to FBref position
    if 'granular_position' in player_row and pd.notna(player_row['granular_position']):
        position_key = player_row['granular_position']
        position_column = 'granular_position'
    elif 'position_group' in player_row and pd.notna(player_row['position_group']):
        position_key = player_row['position_group']
        position_column = 'position_group'
    else:
        # Fallback to Pos column
        position_key = player_row['Pos']
        position_column = 'Pos'

    # Filter to all players at this position with minimum minutes
    df = system.df_master[
        (system.df_master[position_column] == position_key) &
        (system.df_master['Minutes'] >= 270)
    ].copy()

    # Define stat categories (same as peer comparison)
    if is_gk:
        stat_categories = {
            'Shot Stopping': {
                'stats': ['Post-Shot Expected Goals', 'PSxG-GAPost-Shot Expected Goals minus Goals AllowedPositive numbers suggest better luck or an above average ability to stop shotsPSxG is expected goals based on how likely the goalkeeper is to save the shotNote', 'PSxG-GA/90Post-Shot Expected Goals minus Goals Allowed per 90 minutesPositive numbers suggest better luck or an above average ability to stop shotsPSxG is expected goals based on how likely the goalkeeper is to save the shotNote', 'GA', 'Post-Shot Expected Goals per Shot on Target'],
                'labels': ['PSxG', 'PSxG-GA', 'PSxG-GA/90', 'Goals Against', 'PSxG per SoT']
            },
            'Distribution': {
                'stats': ['Cmp%', 'Prg', 'Launch%', 'Avg', 'Tot'],
                'labels': ['Pass Accuracy', 'Progressive Passes', 'Launch %', 'Avg Pass Length', 'Total Passes']
            },
            'Sweeping': {
                'stats': ['#OPA', '#OPA/90', 'Avg.6', 'Stp', 'Stp%'],
                'labels': ['Def Actions Outside Pen', 'Def Actions/90', 'Avg Distance', 'Crosses Stopped', 'Cross Stop %']
            },
            'Passing Under Pressure': {
                'stats': ['Att (GK)', 'Launch%.1', 'Avg.1', 'Launch%.2', 'Avg.3'],
                'labels': ['Pass Attempts', 'Goal Kick Launch %', 'GK Avg Length', 'Def 3rd Launch %', 'Def 3rd Avg Length']
            }
        }
    else:
        stat_categories = {
            'Shooting': {
                'stats': ['Sh/90', 'SoT%', 'G/Sh', 'npxG/Shot', 'xG'],
                'labels': ['Shots/90', 'Shot Accuracy', 'Goal Conversion', 'npxG/Shot', 'xG']
            },
            'Passing': {
                'stats': ['Cmp%', 'Prg', 'KP', 'xA', 'Cmp%.1'],
                'labels': ['Pass Accuracy', 'Progressive Passes', 'Key Passes', 'xA', 'Medium Pass %']
            },
            'Possession': {
                'stats': ['Touches', 'Succ%', 'Carries', 'PrgC', 'CPA'],
                'labels': ['Touches', 'Dribble Success', 'Carries', 'Progressive Carries', 'Carries to Penalty']
            },
            'Defensive': {
                'stats': ['Tkl+Int', 'Tkl%', 'Blocks', 'Int', 'Ball Recoveries'],
                'labels': ['Tackles+Int', 'Tackle Success', 'Blocks', 'Interceptions', 'Ball Recoveries']
            },
            'Creation': {
                'stats': ['SCA90', 'GCA90', 'xAG', 'PPA', 'CrsPA'],
                'labels': ['Shot Creating/90', 'Goal Creating/90', 'xAG', 'Passes to Penalty', 'Crosses to Penalty']
            }
        }

    return df, stat_categories, position_key

def create_radar_chart(df, player_name, peer_names, category_name, stats, labels):
    """Create a radar chart comparing player to peers"""

    # Filter to relevant players
    player_df = df[df['Player'] == player_name]
    peers_df = df[df['Player'].isin(peer_names)]

    if len(player_df) == 0 or len(peers_df) == 0:
        return None

    # Fill NaN with 0 for stats
    for stat in stats:
        if stat not in df.columns:
            return None

    # Calculate percentile ranks relative to peers (0-100)
    percentile_data = []

    # Get player values
    player_row = player_df.iloc[0]
    player_values = []

    for stat in stats:
        # Combine player and peers for this stat
        all_values = np.array(list(peers_df[stat].fillna(0)) + [player_row[stat] if pd.notna(player_row[stat]) else 0])

        # Calculate percentile rank (0-100)
        player_val = player_row[stat] if pd.notna(player_row[stat]) else 0
        percentile = (np.sum(all_values <= player_val) / len(all_values)) * 100
        player_values.append(percentile)

    # Get average peer values (as percentile)
    peer_values = [50] * len(stats)  # Peers average at 50th percentile by definition

    # Create figure
    fig = go.Figure()

    # Add peer average (orange)
    fig.add_trace(go.Scatterpolar(
        r=peer_values + [peer_values[0]],  # Close the shape
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(255, 165, 0, 0.2)',
        line=dict(color='orange', width=2),
        name='Peer Average',
        hovertemplate='%{theta}: 50th percentile<extra></extra>'
    ))

    # Add player (red)
    fig.add_trace(go.Scatterpolar(
        r=player_values + [player_values[0]],  # Close the shape
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.1)',
        line=dict(color='red', width=3),
        name=player_name,
        hovertemplate='%{theta}: %{r:.0f}th percentile<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[25, 50, 75, 100],
                ticktext=['25th', '50th', '75th', '100th']
            )
        ),
        showlegend=True,
        title=f"{category_name} Performance vs Peers",
        height=400
    )

    return fig

def get_top_bottom_stats(system, player_name, n=3):
    """
    Get the top N and bottom N statistics for a player compared to all players at their FBref position.

    Returns:
        dict with 'top_stats', 'bottom_stats', 'position', 'total_players'
    """
    # Get player data
    player_matches = system.df_master[system.df_master['Player'] == player_name]
    if len(player_matches) == 0:
        return None

    player_row = player_matches.iloc[0]

    # Get FBref position
    fbref_position = player_row['Pos'] if 'Pos' in player_row else None
    if not fbref_position:
        return None

    # Filter to all players at this FBref position with minimum minutes
    position_df = system.df_master[
        (system.df_master['Pos'] == fbref_position) &
        (system.df_master['Minutes'] >= 270)
    ].copy()

    if len(position_df) < 5:
        return None

    # Get all numeric columns (stats)
    numeric_cols = position_df.select_dtypes(include=[np.number]).columns.tolist()

    # Exclude non-stat columns
    exclude_cols = ['Minutes', 'Season', 'data_season', 'base_salary', 'compensation',
                    'year_int', 'Age', 'Born', 'MP', 'Starts', 'Min', '90s']
    stat_cols = [col for col in numeric_cols if col not in exclude_cols]

    # Position-specific exclusions
    if fbref_position == 'GK':
        # Exclude outfield stats that don't apply to goalkeepers
        gk_exclude = ['Gls', 'Ast', 'G+A', 'G-PK', 'PK', 'PKatt', 'xG', 'npxG', 'xAG', 'npxG+xAG',
                      'Sh', 'SoT', 'SoT%', 'Sh/90', 'SoT/90', 'G/Sh', 'G/SoT', 'Dist',
                      'FK', 'npxG/Sh', 'G-xG', 'np:G-xG', 'PrgC', 'PrgP', 'PrgR',
                      'Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl.1', 'Att', 'Tkl%',
                      'Lost', 'Blocks', 'Sh.1', 'Pass', 'Int', 'Tkl+Int', 'Clr', 'Err',
                      'Touches', 'Def Pen', 'Att Pen', 'Live', 'Succ', 'Att.1', 'Succ%',
                      'Tkld', 'Tkld%', 'Carries', 'TotDist', 'PrgDist', 'CPA', 'Mis', 'Dis',
                      'Rec', 'SCA', 'SCA90', 'PassLive', 'PassDead', 'TO', 'Fld', 'Def',
                      'GCA', 'GCA90', 'PassLive.1', 'PassDead.1', 'TO.1', 'Sh.2', 'Fld.1', 'Def.1',
                      'CrdY', 'CrdR', '2CrdY', 'Fls', 'Off', 'PKwon', 'PKcon', 'OG', 'Recov',
                      'Won', 'Lost.1', 'Won%']
        stat_cols = [col for col in stat_cols if col not in gk_exclude]

    # Remove duplicate column names (keep first occurrence)
    # This handles cases where the same stat appears in multiple source files
    # Also exclude columns with numeric suffixes like 'Cmp%.12' which are pandas duplicates
    import re
    seen = set()
    unique_stat_cols = []
    for col in stat_cols:
        # Skip columns with .N suffix (pandas duplicate indicators)
        if re.search(r'\.\d+$', str(col)):
            continue
        if col not in seen:
            seen.add(col)
            unique_stat_cols.append(col)
    stat_cols = unique_stat_cols

    # Calculate percentile ranks for all stats
    stat_percentiles = []
    for stat in stat_cols:
        if stat not in position_df.columns:
            continue

        # Get player value
        player_val = player_row[stat] if pd.notna(player_row[stat]) else 0

        # Get all position values
        position_values = position_df[stat].fillna(0).values

        # Skip if all values are the same or zero
        if len(set(position_values)) <= 1:
            continue

        # Calculate percentile for sorting
        percentile = (np.sum(position_values <= player_val) / len(position_values)) * 100

        # Calculate cardinal rank (1 = best, higher = worse)
        cardinal_rank = np.sum(position_values > player_val) + 1

        stat_percentiles.append({
            'stat': stat,
            'player_value': player_val,
            'percentile': percentile,  # Keep for sorting
            'cardinal_rank': cardinal_rank,
            'position_median': np.median(position_values),
            'position_max': np.max(position_values)
        })

    # Sort by percentile
    stat_percentiles.sort(key=lambda x: x['percentile'], reverse=True)

    # Get top N and bottom N
    top_stats = stat_percentiles[:n]
    bottom_stats = stat_percentiles[-n:][::-1]  # Reverse to show worst first

    return {
        'top_stats': top_stats,
        'bottom_stats': bottom_stats,
        'position': fbref_position,
        'total_players': len(position_df)
    }

def create_position_radar_chart(df, player_name, category_name, stats, labels, position_label):
    """Create a radar chart comparing player to all players at their position"""

    # Filter to player
    player_df = df[df['Player'] == player_name]

    if len(player_df) == 0 or len(df) < 5:
        return None

    # Check if all stats exist
    for stat in stats:
        if stat not in df.columns:
            return None

    # Get player values
    player_row = player_df.iloc[0]
    player_values = []

    for stat in stats:
        # Get all position values for this stat
        all_position_values = df[stat].fillna(0).values

        # Calculate percentile rank (0-100) compared to all at position
        player_val = player_row[stat] if pd.notna(player_row[stat]) else 0
        percentile = (np.sum(all_position_values <= player_val) / len(all_position_values)) * 100
        player_values.append(percentile)

    # Position average at 50th percentile
    position_avg = [50] * len(stats)

    # Create figure
    fig = go.Figure()

    # Add position average (light blue)
    fig.add_trace(go.Scatterpolar(
        r=position_avg + [position_avg[0]],
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(100, 149, 237, 0.2)',
        line=dict(color='cornflowerblue', width=2),
        name=f'{position_label} Average',
        hovertemplate='%{theta}: 50th percentile<extra></extra>'
    ))

    # Add player (red)
    fig.add_trace(go.Scatterpolar(
        r=player_values + [player_values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.1)',
        line=dict(color='red', width=3),
        name=player_name,
        hovertemplate='%{theta}: %{r:.0f}th percentile<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[25, 50, 75, 100],
                ticktext=['25th', '50th', '75th', '100th']
            )
        ),
        showlegend=True,
        title=f"{category_name} vs All {position_label}s ({len(df)} players)",
        height=400
    )

    return fig

# Main app
def main():
    st.title("MLS Free Agent Contract Valuator")
    st.markdown("### 2026 Free Agent Market Analysis")

    # Load system and data
    system = load_valuation_system()
    fa_df = load_free_agents()

    if fa_df is None:
        st.stop()

    # Sidebar filters
    st.sidebar.header("Player Selection Filters")

    # Get all player data with position info from the system
    position_cols = ['Player', 'position_group']
    if 'granular_position' in system.df_master.columns:
        position_cols.append('granular_position')
    all_player_data = system.df_master[position_cols].drop_duplicates()

    # Merge with free agents to get position data
    fa_with_position = fa_df.merge(
        all_player_data,
        left_on='name',
        right_on='Player',
        how='left'
    )

    # Team filter
    all_teams = ["All Teams"] + sorted(fa_with_position['team'].unique().tolist())
    selected_team = st.sidebar.selectbox("Team", all_teams, key='team_filter')

    # Apply team filter
    temp_filtered = fa_with_position.copy()
    if selected_team != "All Teams":
        temp_filtered = temp_filtered[temp_filtered['team'] == selected_team]

    # Position filter (dynamic based on team) - with both FBref groups and FC25 granular positions
    st.sidebar.markdown("**Position Filters:**")

    # FBref Position Group filter
    available_position_groups = sorted(temp_filtered['position_group'].dropna().unique().tolist())
    all_position_groups = ["All"] + available_position_groups
    selected_position_group = st.sidebar.selectbox(
        "Position Group (FBref)",
        all_position_groups,
        key='position_group_filter',
        help="Broad position categories: GK, DF, MF, FW"
    )

    # Apply position group filter
    if selected_position_group != "All":
        temp_filtered = temp_filtered[temp_filtered['position_group'] == selected_position_group]

    # FC25 Granular Position filter (if available)
    if 'granular_position' in temp_filtered.columns:
        available_granular = sorted(temp_filtered['granular_position'].dropna().unique().tolist())
        if available_granular:
            all_granular = ["All"] + available_granular
            selected_granular = st.sidebar.selectbox(
                "Specific Position (FC25)",
                all_granular,
                key='granular_position_filter',
                help="Detailed positions: CB, ST, CDM, CAM, LW, RW, etc."
            )

            # Apply granular position filter
            if selected_granular != "All":
                temp_filtered = temp_filtered[temp_filtered['granular_position'] == selected_granular]

    # Player name filter (dynamic based on team and position)
    available_players = sorted(temp_filtered['name'].unique().tolist())
    all_players_option = ["All Players"] + available_players
    selected_player_filter = st.sidebar.selectbox(
        "Player Name",
        all_players_option,
        key='player_name_filter',
        help="Select a specific player or 'All Players' to browse"
    )

    # Apply player name filter
    if selected_player_filter != "All Players":
        temp_filtered = temp_filtered[temp_filtered['name'] == selected_player_filter]

    # Additional filters section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Additional Filters")

    # Designation filter
    all_designations = ["All Designations"] + sorted(fa_df['roster_designation'].dropna().unique().tolist())
    selected_designation = st.sidebar.selectbox("Contract Designation", all_designations)

    # Option year filter
    has_option_filter = st.sidebar.radio(
        "Contract Status",
        ["All Players", "With Team Option", "No Team Option"]
    )

    # Apply additional filters
    filtered_df = temp_filtered.copy()

    if selected_designation != "All Designations":
        filtered_df = filtered_df[filtered_df['roster_designation'] == selected_designation]

    if has_option_filter == "With Team Option":
        filtered_df = filtered_df[filtered_df['option_years'].notna()]
    elif has_option_filter == "No Team Option":
        filtered_df = filtered_df[filtered_df['option_years'].isna()]

    # Valuation adjustments section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Valuation Adjustments")

    # Toggle for age-based adjustment
    apply_age_adjustment = st.sidebar.checkbox(
        "Apply Age-Based Premium",
        value=True,
        help="Adjust salary based on position-specific age curves (peak ages vary by position)"
    )

    # Show additional premium options in expander
    with st.sidebar.expander("Additional Premiums"):
        championship_premium = st.checkbox(
            "Pedigree",
            value=False,
            help="Apply 5-15% premium for hardware winners (MLS Cup, Supporters' Shield, Golden Boot, MVP, etc.)"
        )

        if championship_premium:
            champ_pct = st.slider(
                "Pedigree Premium %",
                min_value=5,
                max_value=15,
                value=10,
                step=1
            )
        else:
            champ_pct = 0

        breakout_premium = st.checkbox(
            "Breakout Season Bonus",
            value=False,
            help="Apply 5-10% premium for career-best performance"
        )

        if breakout_premium:
            breakout_pct = st.slider(
                "Breakout Premium %",
                min_value=5,
                max_value=10,
                value=7,
                step=1
            )
        else:
            breakout_pct = 0

    # Info sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This tool analyzes **2026 MLS Free Agents** using:\n\n"
        "- K-Nearest Neighbors peer comparison\n"
        "- 2025 season performance data\n"
        "- Statistical clustering by archetype\n"
        "- Position-specific age curves\n"
        "- MLS salary cap optimization\n\n"
        f"**{len(fa_df)} total free agents** identified with contracts expiring in 2025"
    )

    # Academic citations
    with st.sidebar.expander("Academic Sources"):
        st.markdown("""
        **Age Curve Analysis:**
        - Franceschi et al. (2024). [Determinants of football players' valuation: A systematic review](https://onlinelibrary.wiley.com/doi/10.1111/joes.12552). *Journal of Economic Surveys*

        **Position-Specific Metrics:**
        - EA Sports FC 25 Player Database (2024)

        **MLS Salary Cap Rules:**
        - [MLS 2025 Salary Cap Structure](https://phillysoccerpage.net/2025/01/08/mls-salary-cap-details-updated-to-2025/)
        - [MLS Players Association Salary Data](https://mlsplayers.org/resources/salary-guide)

        **Performance Data:**
        - [FBref](https://fbref.com) - Advanced Statistics (powered by Opta)
        """)

    # Display summary stats
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Free Agents", len(fa_df))
    with col2:
        st.metric("Filtered Results", len(filtered_df))
    with col3:
        st.metric("With Team Options", len(fa_df[fa_df['option_years'].notna()]))
    with col4:
        st.metric("No Options", len(fa_df[fa_df['option_years'].isna()]))

    # Player selection
    # Check if a specific player was selected via the sidebar filter
    if selected_player_filter != "All Players":
        # A specific player was selected in the sidebar
        selected_player = selected_player_filter
        st.header(f"Valuation for {selected_player}")
        st.info(f"Player selected via sidebar filter. Change the filter to view other players.")
    else:
        # Show dropdown to select from filtered results
        st.header("Select Player to Value")

    # Create a formatted list of players
    player_options = []
    for idx, row in filtered_df.iterrows():
        option_text = f" (Option: {row['option_years']})" if pd.notna(row['option_years']) else ""

        # Use roster number if no designation
        if pd.notna(row['roster_designation']):
            designation = row['roster_designation']
        elif 'roster_number' in row and pd.notna(row['roster_number']):
            designation = f"Roster #{int(row['roster_number'])}"
        else:
            designation = "N/A"

        player_display = f"{row['name']} - {row['team']} ({designation}){option_text}"
        player_options.append((row['name'], player_display))

    if len(player_options) == 0:
        st.warning("No players match the selected filters. Please adjust your filters.")
        st.stop()

    # Dropdown with formatted display
    player_dict = dict(player_options)
    selected_display = st.selectbox(
        "Choose a free agent:",
        options=list(player_dict.values()),
        index=0
    )

    # Get actual player name
    selected_player = [name for name, display in player_dict.items() if display == selected_display][0]

    if not selected_player:
        st.warning("No player selected")
        return

    # Value the selected player
    st.markdown("---")

    with st.spinner(f"Analyzing {selected_player}..."):
        result = system.value_player(selected_player)

    if 'error' in result:
        st.error(f"Error: {result['error']}")

        # Check if player exists in data at all
        player_data = system.df_master[system.df_master['Player'] == selected_player]
        if len(player_data) > 0:
            player_minutes = player_data.iloc[0].get('Minutes', 0)
            st.info(f"⚠️ This player has only {player_minutes:.0f} minutes of playing time. A minimum of 270 minutes (~3 full matches) is required for reliable statistical analysis and salary valuation.")
        else:
            st.info("⚠️ This player was not found in the FBref statistical database for the 2023-2025 seasons. They may not have appeared in any MLS matches during this period, or had insufficient playing time to be tracked.")
        return

    # Check if player is under the minutes threshold
    player_minutes = result.get('minutes', 0)
    under_threshold = player_minutes < 900

    # Player Overview Header
    player_team = fa_df[fa_df['name'] == selected_player]['team'].iloc[0] if selected_player in fa_df['name'].values else "Unknown"

    st.header(f"{selected_player}")
    st.markdown(f"**{player_team}**")

    # Success message with warning if under threshold or using prior season data
    data_season = result.get('data_season', 2025)
    using_prior_season = data_season < 2025

    if under_threshold:
        st.warning(f"Limited Playing Time: {player_minutes:.0f} minutes ({player_minutes/90:.1f} matches) - Analysis may be less reliable")

    if using_prior_season:
        st.info(f"Using {data_season} season data - Player has insufficient data in 2025 season")

    # Player info metrics - with age highlighted
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        # Display granular position if available, with position_group as backup
        granular_pos = result.get('granular_position')
        if granular_pos and pd.notna(granular_pos):
            position_display = f"{granular_pos} ({result['position']})"
            alt_pos = result.get('alternative_positions')
            if alt_pos and pd.notna(alt_pos):
                position_help = f"Alternative positions: {alt_pos}"
            else:
                position_help = None
        else:
            position_display = result['position']
            position_help = "FBref group position"

        st.metric(
            "Position",
            position_display,
            delta=None,
            help=position_help
        )

    with col2:
        # Display age with peak indicator
        player_age = result.get('age', 'N/A')
        if player_age != 'N/A':
            age_factor = result.get('age_adjustment_factor', 1.0)

            # Determine age status based on factor
            # Young players now get 1.00-1.05x (potential premium)
            # Prime/Peak players get 1.05-1.20x
            # Post-peak get 0.95-1.05x
            # Declining get <0.95x
            if age_factor >= 1.15:
                age_delta = "Peak Years"
                age_delta_color = "normal"  # Green
            elif age_factor >= 1.05:
                age_delta = "Prime"
                age_delta_color = "normal"  # Green
            elif age_factor >= 1.00:
                # Young players with potential (1.00-1.05x)
                age_delta = "Developing"
                age_delta_color = "normal"  # Green (positive for young talent)
            elif age_factor >= 0.95:
                # Post-peak but still valuable
                age_delta = "Established"
                age_delta_color = "off"  # Gray
            else:
                # Declining value (<0.95x)
                age_delta = "Declining"
                age_delta_color = "inverse"  # Red
        else:
            age_delta = None
            age_delta_color = "off"

        st.metric(
            "Age",
            player_age,
            delta=age_delta,
            delta_color=age_delta_color,
            help=f"Age-based adjustment: {result.get('age_adjustment_factor', 1.0):.2f}x" if player_age != 'N/A' else None
        )

    with col3:
        if under_threshold:
            minutes_delta = "Low sample size"
            minutes_color = "inverse"  # Red warning
        else:
            minutes_delta = None
            minutes_color = "off"
        st.metric(
            "Minutes Played",
            f"{result['minutes']:.0f}",
            delta=minutes_delta,
            delta_color=minutes_color
        )

    with col4:
        # Current compensation
        current_salary = result.get('actual_salary')
        if current_salary and current_salary > 0:
            st.metric(
                "Current Salary",
                format_salary(current_salary),
                help="2025 base salary"
            )
        else:
            st.metric(
                "Current Salary",
                "N/A",
                help="No salary data available"
            )

    with col5:
        if using_prior_season:
            season_delta = "Prior season"
            season_color = "inverse"  # Red warning
        else:
            season_delta = "Current"
            season_color = "normal"  # Green good
        st.metric(
            "Data Season",
            f"{data_season}",
            delta=season_delta,
            delta_color=season_color
        )

    # Salary estimation
    if 'salary_estimate' in result and 'predicted_salary' in result['salary_estimate']:
        est = result['salary_estimate']

        st.markdown("---")
        st.header("Contract Recommendation")

    elif 'salary_estimate' in result and 'error' in result['salary_estimate']:
        # Handle case where salary estimation failed
        st.markdown("---")
        st.header("Valuation Analysis")

        error_msg = result['salary_estimate']['error']
        peers_found = result['salary_estimate'].get('peers_found', 0)

        st.warning(f"⚠️ {error_msg}")
        st.info(f"This player's predicted designation/position combination has limited comparable players in the database ({peers_found} found, minimum 5 required for statistical analysis).")

        # Still show predicted designation
        if 'predicted_designation' in result:
            st.subheader("Predicted Player Designation")
            st.metric("Designation Tier", result['predicted_designation'])

            if 'designation_confidence' in result:
                st.write("**Prediction Confidence:**")
                conf_df = pd.DataFrame([
                    {'Tier': tier, 'Probability': f"{prob:.1%}"}
                    for tier, prob in result['designation_confidence'].items()
                ]).sort_values('Probability', ascending=False)
                st.dataframe(conf_df, hide_index=True, use_container_width=True)

        st.markdown("---")
        st.info("💡 **Recommendation:** Consider comparing to similar players manually or adjusting position/designation filters to find comparable players.")
        return  # Exit early since we can't show salary recommendations

    else:
        st.error("Unable to generate salary estimation")
        return

    if 'salary_estimate' in result and 'predicted_salary' in result['salary_estimate']:
        est = result['salary_estimate']

        # Check if using fallback tier
        if est.get('used_fallback', False):
            original_tier = est.get('original_designation', 'N/A')
            fallback_tier = est.get('fallback_tier', 'N/A')
            st.info(f"ℹ️ **Note:** Using {fallback_tier} tier comparables due to limited {original_tier} peers at this position. Salary estimates are based on top {fallback_tier} players with similar statistical profiles.")

        # Calculate adjusted salary based on toggles
        base_salary = est['predicted_salary']
        final_salary = base_salary
        adjustments = []

        # Apply age adjustment if enabled
        if apply_age_adjustment and 'age_adjusted_salary' in result:
            age_factor = result.get('age_adjustment_factor', 1.0)
            age_pct = (age_factor - 1) * 100
            final_salary = base_salary * age_factor
            # Show discount vs premium properly
            if age_pct >= 0:
                adjustments.append(f"Age Premium: +{age_pct:.1f}% (Age {result.get('age', 'N/A')})")
            else:
                adjustments.append(f"Age Discount: -{abs(age_pct):.1f}% (Age {result.get('age', 'N/A')})")

        # Apply pedigree premium (to base, not final)
        if championship_premium:
            final_salary = final_salary + (base_salary * champ_pct/100)
            adjustments.append(f"Pedigree: +{champ_pct}%")

        # Apply breakout premium (to base, not final)
        if breakout_premium:
            final_salary = final_salary + (base_salary * breakout_pct/100)
            adjustments.append(f"Breakout Season: +{breakout_pct}%")

        # Calculate adjusted range
        base_range_low = est.get('salary_range_low')
        base_range_high = est.get('salary_range_high')

        if apply_age_adjustment and 'age_adjusted_range_low' in result:
            adj_low = result['age_adjusted_range_low']
            adj_high = result['age_adjusted_range_high']
        else:
            adj_low = base_range_low
            adj_high = base_range_high

        # Apply same premiums to range (only if values exist)
        # Each premium applies to the BASE range, not the adjusted range
        if adj_low is not None and adj_high is not None and base_range_low is not None and base_range_high is not None:
            if championship_premium:
                adj_low = adj_low + (base_range_low * champ_pct/100)
                adj_high = adj_high + (base_range_high * champ_pct/100)
            if breakout_premium:
                adj_low = adj_low + (base_range_low * breakout_pct/100)
                adj_high = adj_high + (base_range_high * breakout_pct/100)

        # Main salary section
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("Recommended Contract Value")

            # Show base if adjustments applied
            if adjustments:
                st.metric(
                    "Base Statistical Model",
                    format_salary(base_salary),
                    help="Peer-based model prediction before adjustments"
                )

                # Show adjustments
                with st.expander("Applied Adjustments"):
                    for adj in adjustments:
                        st.write(f"• {adj}")

                # Calculate delta properly (can be negative)
                salary_diff = final_salary - base_salary
                if salary_diff >= 0:
                    delta_display = f"+{format_salary(salary_diff)}"
                else:
                    delta_display = f"-{format_salary(abs(salary_diff))}"

                st.metric(
                    "**Final Recommended Salary**",
                    f"**{format_salary(final_salary)}**",
                    delta=delta_display,
                    help="Salary after applying selected adjustments (premiums or discounts)"
                )
            else:
                st.metric(
                    "Recommended Salary",
                    format_salary(final_salary),
                    help="Model-predicted fair market value based on peer comparison"
                )

            if adj_low is not None and adj_high is not None:
                st.markdown("##### Negotiation Range (25th-75th percentile)")
                range_col1, range_col2 = st.columns(2)
                with range_col1:
                    st.metric("Low End", format_salary(adj_low))
                with range_col2:
                    st.metric("High End", format_salary(adj_high))

        with col2:
            st.subheader("Player Profile")

            # Contract tier
            st.markdown("##### Contract Tier")
            st.info(f"**{result['predicted_designation']}**")

            # Player archetype
            st.markdown("##### Player Archetype")
            if result.get('is_outlier'):
                archetype_text = 'Elite at Position'
            else:
                archetype_text = 'Standard Positional Player'
            st.info(f"**{archetype_text}**")

            # Position-specific salary distribution
            st.markdown("##### Position Salary Distribution")

            # Get salary distribution for this position
            position_key = result.get('granular_position') if pd.notna(result.get('granular_position')) else result['position']

            # Filter players by position
            if 'granular_position' in system.df_master.columns and pd.notna(result.get('granular_position')):
                position_players = system.df_master[
                    (system.df_master['granular_position'] == position_key) &
                    (system.df_master['base_salary'].notna())
                ]
            else:
                position_players = system.df_master[
                    (system.df_master['position_group'] == position_key) &
                    (system.df_master['base_salary'].notna())
                ]

            if len(position_players) > 0:
                # Create histogram
                fig_dist = go.Figure()

                # Determine scaling based on max salary in position
                max_pos_salary = position_players['base_salary'].max()
                divisor, axis_label = get_salary_axis_config(safe_max(
                    max_pos_salary,
                    final_salary
                ))

                fig_dist.add_trace(go.Histogram(
                    x=position_players['base_salary'] / divisor,
                    nbinsx=20,
                    name='Position Salaries',
                    marker_color='lightblue',
                    opacity=0.7
                ))

                # Add player's recommended salary
                if final_salary:
                    fig_dist.add_vline(
                        x=final_salary / divisor,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Recommended",
                        annotation_position="top"
                    )

                # Add MLS thresholds
                # TAM threshold (silver)
                fig_dist.add_vline(
                    x=683_750 / divisor,  # Max budget charge
                    line_dash="dot",
                    line_color="silver",
                    annotation_text="TAM",
                    annotation_position="top"
                )

                # DP threshold (gold) - only if in scale
                dp_threshold = 1_740_000  # 2025 DP threshold
                if dp_threshold <= safe_max(max_pos_salary, final_salary if final_salary else 0):
                    fig_dist.add_vline(
                        x=dp_threshold / divisor,
                        line_dash="dot",
                        line_color="gold",
                        annotation_text="DP",
                        annotation_position="top"
                    )

                fig_dist.update_layout(
                    xaxis_title=axis_label,
                    yaxis_title="Number of Players",
                    height=250,
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False
                )

                st.plotly_chart(fig_dist, use_container_width=True)

                # Show percentile (only if final_salary exists)
                if final_salary is not None:
                    percentile = (position_players['base_salary'] <= final_salary).sum() / len(position_players) * 100
                    st.caption(f"Recommended salary is at {percentile:.0f}th percentile for {position_key} position")
            else:
                st.caption("Insufficient position data for distribution")

        # MLS Contract Structure section
        if 'contract_structure' in result:
            st.markdown("---")
            st.subheader("MLS Contract Structure")

            contract = result['contract_structure']

            # Create contract summary
            struct_col1, struct_col2 = st.columns(2)

            with struct_col1:
                st.metric(
                    "Designation",
                    contract['designation'],
                    help="Roster designation based on 2025 MLS rules"
                )

            with struct_col2:
                st.metric(
                    "Budget Charge",
                    format_salary(contract['budget_charge']),
                    help="Amount counting against salary cap"
                )

            # Show allocation money details
            if contract.get('allocation_money_needed', 0) > 0:
                st.info(
                    f"Requires {format_salary(contract['allocation_money_needed'])} "
                    f"{contract['allocation_type']} to buy down to max budget charge"
                )

            # Show TAM buydown option for DPs
            if 'tam_buydown_option' in contract:
                with st.expander("TAM Buydown Option"):
                    tam_opt = contract['tam_buydown_option']
                    st.write(f"**Cost:** {format_salary(tam_opt['tam_needed'])} TAM")
                    st.write(f"**Result:** {tam_opt['new_designation']} with {format_salary(tam_opt['new_budget_charge'])} charge")
                    st.write("This removes the DP tag while staying under the TAM threshold.")

            # Contract Tier Benchmarks
            st.markdown("##### Positional Contract Benchmarks")
            st.caption("Closest players at this position by contract tier - showing the performance level needed for TAM/DP deals")

            # Get position for filtering
            position_key = result.get('granular_position') if pd.notna(result.get('granular_position')) else result['position']

            # Filter to same position with salary data
            if 'granular_position' in system.df_master.columns and pd.notna(result.get('granular_position')):
                position_filter = system.df_master['granular_position'] == position_key
            else:
                position_filter = system.df_master['position_group'] == position_key

            position_with_salary = system.df_master[
                position_filter &
                (system.df_master['base_salary'].notna()) &
                (system.df_master['Minutes'] >= 270)
            ].copy()

            if len(position_with_salary) > 0:
                # Define salary thresholds
                TAM_THRESHOLD = 683_750
                DP_THRESHOLD = 1_740_000

                # Classify players by designation
                position_with_salary['designation_tier'] = position_with_salary['base_salary'].apply(
                    lambda x: 'DP' if x >= DP_THRESHOLD else ('TAM' if x >= TAM_THRESHOLD else 'Standard')
                )

                # Get closest TAM and DP player (by salary)
                tam_players = position_with_salary[position_with_salary['designation_tier'] == 'TAM']
                dp_players = position_with_salary[position_with_salary['designation_tier'] == 'DP']

                benchmark_data = []

                # Find closest TAM player (lowest TAM salary at position)
                if len(tam_players) > 0:
                    closest_tam = tam_players.nsmallest(1, 'base_salary').iloc[0]
                    benchmark_data.append({
                        'Tier': 'TAM',
                        'Player': closest_tam['Player'],
                        'Team': closest_tam.get('Squad', 'N/A'),
                        'Salary': format_salary(closest_tam['base_salary']),
                        'Minutes': f"{closest_tam['Minutes']:.0f}"
                    })

                # Find closest DP player (lowest DP salary at position)
                if len(dp_players) > 0:
                    closest_dp = dp_players.nsmallest(1, 'base_salary').iloc[0]
                    benchmark_data.append({
                        'Tier': 'DP',
                        'Player': closest_dp['Player'],
                        'Team': closest_dp.get('Squad', 'N/A'),
                        'Salary': format_salary(closest_dp['base_salary']),
                        'Minutes': f"{closest_dp['Minutes']:.0f}"
                    })

                if benchmark_data:
                    benchmark_df = pd.DataFrame(benchmark_data)
                    st.dataframe(
                        benchmark_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Tier": st.column_config.TextColumn("Tier", width="small", help="Contract designation"),
                            "Player": st.column_config.TextColumn("Player", width="medium"),
                            "Team": st.column_config.TextColumn("Team", width="medium"),
                            "Salary": st.column_config.TextColumn("Salary", width="medium"),
                            "Minutes": st.column_config.TextColumn("Minutes", width="small")
                        }
                    )
                else:
                    st.caption(f"No TAM or DP players found at {position_key} position")
            else:
                st.caption("Insufficient position data for benchmarks")

        # Current salary comparison
        if 'actual_salary' in result and result['actual_salary'] and final_salary is not None:
            st.markdown("---")
            st.subheader("Current Salary vs Recommendation")

            diff = final_salary - result['actual_salary']
            diff_pct = (diff / result['actual_salary']) * 100

            current_col1, current_col2 = st.columns(2)

            with current_col1:
                st.metric("Current Salary", format_salary(result['actual_salary']))

            with current_col2:
                if diff > 0:
                    st.metric(
                        "Market Adjustment",
                        f"+{format_salary(abs(diff))}",
                        f"{abs(diff_pct):.1f}% underpaid"
                    )
                else:
                    st.metric(
                        "Market Adjustment",
                        f"-{format_salary(abs(diff))}",
                        f"{abs(diff_pct):.1f}% overpaid"
                    )

        # Salary range visualization
        st.markdown("### Salary Range Analysis")

        try:
            fig = go.Figure()

            # Determine scaling based on max salary in the chart
            max_val = safe_max(
                est.get('peer_max'),
                final_salary,
                result.get('actual_salary')
            )
            divisor, axis_label = get_salary_axis_config(max_val)
        except Exception as e:
            st.error(f"Error creating salary range chart: {str(e)}")
            st.write(f"Debug - peer_max: {est.get('peer_max')}, final_salary: {final_salary}, actual: {result.get('actual_salary')}")
            divisor, axis_label = 1000, "Salary ($K)"
            fig = go.Figure()

        # Add peer range (only if values exist)
        if est.get('peer_min') is not None and est.get('peer_max') is not None:
            fig.add_trace(go.Scatter(
                x=[est['peer_min']/divisor, est['peer_max']/divisor],
                y=['Peer Range', 'Peer Range'],
                mode='lines',
                line=dict(color='lightgray', width=8),
                name='Peer Range',
                showlegend=True
            ))

        # Add IQR range (use adj_low/adj_high with adjustments applied, not base range)
        if adj_low is not None and adj_high is not None:
            fig.add_trace(go.Scatter(
                x=[adj_low/divisor, adj_high/divisor],
                y=['Negotiation Range', 'Negotiation Range'],
                mode='lines',
                line=dict(color='blue', width=12),
                name='25th-75th Percentile',
                showlegend=True
            ))

        # Add recommended salary (use final_salary with adjustments, not base predicted_salary)
        if final_salary is not None:
            fig.add_trace(go.Scatter(
                x=[final_salary/divisor],
                y=['Recommended'],
                mode='markers',
                marker=dict(color='green', size=15, symbol='diamond'),
                name='Recommended',
                showlegend=True
            ))

        # Add current salary if available
        if result.get('actual_salary'):
            fig.add_trace(go.Scatter(
                x=[result['actual_salary']/divisor],
                y=['Current'],
                mode='markers',
                marker=dict(color='red', size=15, symbol='star'),
                name='Current Salary',
                showlegend=True
            ))

        fig.update_layout(
            xaxis_title=axis_label,
            yaxis_title="",
            height=300,
            showlegend=True,
            hovermode='closest'
        )

        st.plotly_chart(fig, use_container_width=True)

        # K-NN Peers
        st.header("Statistical Peers")

        with st.expander("About Peer Comparison"):
            st.markdown(
                f"""
                **How peer comparison works:**
                - Uses K-Nearest Neighbors algorithm to find the **{est['n_peers']} most similar players**
                - Compares performance statistics within the same position and contract tier
                - Percentile rankings show performance relative to peer group (50th = average, 100th = best)
                - Salary recommendations based on peer salary distribution
                """
            )

        # Create peer comparison dataframe with better formatting
        peer_data = []
        for i, (name, salary) in enumerate(zip(est['peer_names'], est['peer_salaries']), 1):
            peer_data.append({
                'Rank': i,
                'Player': name,
                'Salary': format_salary(salary)
            })

        df_peers = pd.DataFrame(peer_data)

        # Display as a nice table
        st.dataframe(
            df_peers,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "Player": st.column_config.TextColumn("Player", width="large"),
                "Salary": st.column_config.TextColumn("Salary", width="medium")
            }
        )

        # Radar Charts - Statistical Comparison
        st.header("Performance Profile")

        # Get both peer and position comparison data
        peer_comparison = get_peer_comparison_data(system, selected_player, est['peer_names'][:5])
        position_comparison = get_position_comparison_data(system, selected_player)

        if peer_comparison and position_comparison:
            comparison_df, stat_categories = peer_comparison
            position_df, position_stat_categories, position_key = position_comparison

            st.info(f"**Comparing against 5 statistical peers and all {position_key} players** with ≥270 minutes ({len(position_df)} total players)")

            # Create tabs for each category
            category_tabs = st.tabs(list(stat_categories.keys()))

            for tab, (category_name, category_info) in zip(category_tabs, stat_categories.items()):
                with tab:
                    # Create two columns for side-by-side radar charts
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("##### vs Statistical Peers")
                        # Create peer radar chart
                        fig_peer = create_radar_chart(
                            comparison_df,
                            selected_player,
                            est['peer_names'][:5],
                            category_name,
                            category_info['stats'],
                            category_info['labels']
                        )

                        if fig_peer:
                            st.plotly_chart(fig_peer, use_container_width=True)
                        else:
                            st.info(f"Insufficient data for {category_name} peer comparison")

                    with col2:
                        st.markdown(f"##### vs All {position_key}s")
                        # Create position-wide radar chart
                        fig_position = create_position_radar_chart(
                            position_df,
                            selected_player,
                            category_name,
                            category_info['stats'],
                            category_info['labels'],
                            position_key
                        )

                        if fig_position:
                            st.plotly_chart(fig_position, use_container_width=True)
                        else:
                            st.info(f"Insufficient data for {category_name} position comparison")

                    # Add numeric stat values table for full position group
                    st.markdown(f"##### {category_name} - Position Group Statistics")

                    # Get player row
                    player_row = position_df[position_df['Player'] == selected_player]

                    if len(player_row) > 0:
                        player_row = player_row.iloc[0]

                        # Build table data using position group stats
                        table_data = []
                        for stat, label in zip(category_info['stats'], category_info['labels']):
                            if stat in position_df.columns:
                                # Get player value
                                player_val = player_row[stat] if pd.notna(player_row[stat]) else 0

                                # Calculate percentiles for full position group
                                position_values = position_df[stat].fillna(0)

                                # 25th percentile
                                percentile_25 = np.percentile(position_values, 25)

                                # 50th percentile (median)
                                percentile_50 = np.percentile(position_values, 50)

                                # 75th percentile
                                percentile_75 = np.percentile(position_values, 75)

                                # 100th percentile (max)
                                percentile_100 = np.max(position_values)

                                # Player cardinal rank (1st, 2nd, 3rd, etc.)
                                # Rank by descending order (higher stat value = better rank)
                                cardinal_rank = (position_values > player_val).sum() + 1

                                table_data.append({
                                    'Stat': label,
                                    'Player': f"{player_val:.2f}",
                                    'Rank': ordinal(cardinal_rank),
                                    '25th': f"{percentile_25:.2f}",
                                    '50th': f"{percentile_50:.2f}",
                                    '75th': f"{percentile_75:.2f}",
                                    'Max': f"{percentile_100:.2f}"
                                })

                        if table_data:
                            stats_table = pd.DataFrame(table_data)
                            st.dataframe(
                                stats_table,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Stat": st.column_config.TextColumn("Stat", width="medium"),
                                    "Player": st.column_config.TextColumn("Player", width="small"),
                                    "Rank": st.column_config.TextColumn("Rank", width="small"),
                                    "25th": st.column_config.TextColumn("25th %ile", width="small"),
                                    "50th": st.column_config.TextColumn("50th %ile", width="small"),
                                    "75th": st.column_config.TextColumn("75th %ile", width="small"),
                                    "Max": st.column_config.TextColumn("Max", width="small")
                                }
                            )
        else:
            st.warning("Could not load comparison data")

        # Top and Bottom Statistics
        st.header("Strengths & Weaknesses")

        top_bottom = get_top_bottom_stats(system, selected_player, n=3)

        if top_bottom:
            st.info(f"Comparing all statistics vs {top_bottom['total_players']} {top_bottom['position']} players (FBref position) with ≥270 minutes")

            # Create two columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Top 3 Statistics")

                # Create table for top stats
                top_data = []
                for stat_info in top_bottom['top_stats']:
                    top_data.append({
                        'Statistic': clean_stat_name(stat_info['stat']),
                        'Value': f"{stat_info['player_value']:.2f}",
                        'Rank': ordinal(stat_info['cardinal_rank']),
                        'Position Median': f"{stat_info['position_median']:.2f}",
                        'Position Max': f"{stat_info['position_max']:.2f}"
                    })

                if top_data:
                    top_df = pd.DataFrame(top_data)
                    st.dataframe(
                        top_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Statistic": st.column_config.TextColumn("Statistic", help=f"Compared to all {top_bottom['position']} players", width="medium"),
                            "Value": st.column_config.TextColumn("Player", width="small"),
                            "Rank": st.column_config.TextColumn("Rank", width="small"),
                            "Position Median": st.column_config.TextColumn("Median", width="small"),
                            "Position Max": st.column_config.TextColumn("Max", width="small")
                        }
                    )

            with col2:
                st.markdown("##### Bottom 3 Statistics")

                # Create table for bottom stats
                bottom_data = []
                for stat_info in top_bottom['bottom_stats']:
                    bottom_data.append({
                        'Statistic': clean_stat_name(stat_info['stat']),
                        'Value': f"{stat_info['player_value']:.2f}",
                        'Rank': ordinal(stat_info['cardinal_rank']),
                        'Position Median': f"{stat_info['position_median']:.2f}",
                        'Position Max': f"{stat_info['position_max']:.2f}"
                    })

                if bottom_data:
                    bottom_df = pd.DataFrame(bottom_data)
                    st.dataframe(
                        bottom_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Statistic": st.column_config.TextColumn("Statistic", help=f"Compared to all {top_bottom['position']} players", width="medium"),
                            "Value": st.column_config.TextColumn("Player", width="small"),
                            "Rank": st.column_config.TextColumn("Rank", width="small"),
                            "Position Median": st.column_config.TextColumn("Median", width="small"),
                            "Position Max": st.column_config.TextColumn("Max", width="small")
                        }
                    )
        else:
            # Check why it failed
            player_data = system.df_master[system.df_master['Player'] == selected_player]
            if len(player_data) > 0:
                player_minutes = player_data.iloc[0].get('Minutes', 0)
                if player_minutes < 270:
                    st.warning(f"⚠️ Insufficient playing time for statistical comparison. Player has {player_minutes:.0f} minutes (minimum 270 minutes required for reliable per-90 statistics).")
                else:
                    st.warning("Could not calculate top/bottom statistics - insufficient position data")
            else:
                st.warning("Player not found in statistical database")

        # Peer salary distribution - collapsible for advanced users
        with st.expander("View Peer Salary Distribution"):
            # Determine scaling based on max peer salary
            divisor, axis_label = get_salary_axis_config(safe_max(
                *est['peer_salaries'],
                final_salary,
                result.get('actual_salary')
            ))

            # Create dataframe with numeric salary values for histogram
            peer_salary_data = pd.DataFrame({
                axis_label: [s/divisor for s in est['peer_salaries']]
            })

            fig = px.histogram(
                peer_salary_data,
                x=axis_label,
                nbins=10,
                labels={axis_label: axis_label, 'count': 'Number of Players'}
            )

            # Add vertical line for recommended salary (use final_salary with adjustments)
            fig.add_vline(
                x=final_salary/divisor,
                line_dash="dash",
                line_color="green",
                annotation_text="Recommended",
                annotation_position="top"
            )

            # Add vertical line for current salary if available
            if result.get('actual_salary'):
                fig.add_vline(
                    x=result['actual_salary']/divisor,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Current",
                    annotation_position="top"
                )

            st.plotly_chart(fig, use_container_width=True)

        # Designation confidence chart
        if 'designation_confidence' in result:
            st.markdown("---")
            st.subheader("Contract Tier Confidence Breakdown")

            conf_data = pd.DataFrame([
                {'Tier': tier, 'Probability': prob}
                for tier, prob in sorted(
                    result['designation_confidence'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ])

            fig = px.bar(
                conf_data,
                x='Tier',
                y='Probability',
                title="Predicted Contract Tier Probabilities",
                labels={'Probability': 'Confidence', 'Tier': 'Contract Tier'},
                color='Probability',
                color_continuous_scale='Blues'
            )

            fig.update_layout(showlegend=False, yaxis_tickformat='.0%')

            st.plotly_chart(fig, use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption(
        "**MLS Free Agent Valuator** | Per 90 Minutes | "
        "Model: K-Nearest Neighbors + Random Forest Classification | "
        f"Analyzing {len(fa_df)} free agents with contracts expiring in 2025"
    )

if __name__ == "__main__":
    main()
