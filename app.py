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
        system.load_and_merge_data(season=2025)
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
    player_row = df[df['Player'] == player_name].iloc[0]
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
        all_values = list(peers_df[stat].fillna(0)) + [player_row[stat] if pd.notna(player_row[stat]) else 0]

        # Calculate percentile rank (0-100)
        player_val = player_row[stat] if pd.notna(player_row[stat]) else 0
        percentile = (sum(all_values <= player_val) / len(all_values)) * 100
        player_values.append(percentile)

    # Get average peer values (as percentile)
    peer_values = [50] * len(stats)  # Peers average at 50th percentile by definition

    # Create figure
    fig = go.Figure()

    # Add peer average (grey)
    fig.add_trace(go.Scatterpolar(
        r=peer_values + [peer_values[0]],  # Close the shape
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(128, 128, 128, 0.2)',
        line=dict(color='grey', width=2),
        name='Peer Average',
        hovertemplate='%{theta}: 50th percentile<extra></extra>'
    ))

    # Add player (black)
    fig.add_trace(go.Scatterpolar(
        r=player_values + [player_values[0]],  # Close the shape
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(0, 0, 0, 0.1)',
        line=dict(color='black', width=3),
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
    all_player_data = system.df_master[['Player', 'position_group']].drop_duplicates()

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

    # Position filter (dynamic based on team)
    available_positions = sorted(temp_filtered['position_group'].dropna().unique().tolist())
    all_positions = ["All Positions"] + available_positions
    selected_position = st.sidebar.selectbox("Position", all_positions, key='position_filter')

    # Apply position filter
    if selected_position != "All Positions":
        temp_filtered = temp_filtered[temp_filtered['position_group'] == selected_position]

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

    # Info sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This tool analyzes **2026 MLS Free Agents** using:\n\n"
        "✓ K-Nearest Neighbors peer comparison\n"
        "✓ 2025 season performance data\n"
        "✓ Statistical clustering by archetype\n\n"
        f"**{len(fa_df)} total free agents** identified with contracts expiring in 2025"
    )

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
        st.info("This player may not have enough playing time or statistical data for analysis.")
        return

    # Check if player is under the minutes threshold
    player_minutes = result.get('minutes', 0)
    under_threshold = player_minutes < 900

    # Player Overview Header
    player_team = fa_df[fa_df['name'] == selected_player]['team'].iloc[0] if selected_player in fa_df['name'].values else "Unknown"

    st.header(f"{selected_player}")
    st.markdown(f"**{player_team}**")

    # Success message with warning if under threshold
    if under_threshold:
        st.warning(f"Limited Playing Time: {player_minutes:.0f} minutes ({player_minutes/90:.1f} matches) - Analysis may be less reliable")

    # Player info metrics - simplified (removed duplicate tier)
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Position",
            result['position'],
            delta=None
        )

    with col2:
        minutes_delta = "⚠️ Low sample size" if under_threshold else None
        st.metric(
            "Minutes Played",
            f"{result['minutes']:.0f}",
            delta=minutes_delta
        )

    # Salary estimation
    if 'salary_estimate' in result and 'predicted_salary' in result['salary_estimate']:
        est = result['salary_estimate']

        st.markdown("---")
        st.header("Contract Recommendation")

        # Main salary section
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("Recommended Contract Value")
            st.metric(
                "Base Salary",
                f"${est['predicted_salary']/1000:.0f}K",
                help="Model-predicted fair market value based on peer comparison"
            )

            st.markdown("##### Negotiation Range (25th-75th percentile)")
            range_col1, range_col2 = st.columns(2)
            with range_col1:
                st.metric("Low End", f"${est['salary_range_low']/1000:.0f}K")
            with range_col2:
                st.metric("High End", f"${est['salary_range_high']/1000:.0f}K")

        with col2:
            st.subheader("Player Profile")

            # Contract tier
            st.markdown("##### Contract Tier")
            st.info(f"**{result['predicted_designation']}**")

            # Player archetype
            st.markdown("##### Player Archetype")
            archetype_text = 'Elite/Specialist (Outlier)' if result.get('is_outlier') else f'Archetype {result.get("archetype", "Unknown")}'
            st.info(f"**{archetype_text}**")

            # Tier probabilities
            if 'designation_confidence' in result:
                st.markdown("##### Tier Probabilities")
                sorted_tiers = sorted(
                    result['designation_confidence'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                for tier, prob in sorted_tiers:
                    st.progress(prob, text=f"{tier}: {prob:.1%}")

        # Current salary comparison
        if 'actual_salary' in result and result['actual_salary']:
            st.markdown("---")
            st.subheader("Current Salary vs Recommendation")

            diff = est['predicted_salary'] - result['actual_salary']
            diff_pct = (diff / result['actual_salary']) * 100

            current_col1, current_col2 = st.columns(2)

            with current_col1:
                st.metric("Current Salary", f"${result['actual_salary']/1000:.0f}K")

            with current_col2:
                if diff > 0:
                    st.metric(
                        "Market Adjustment",
                        f"+${abs(diff)/1000:.0f}K",
                        f"{abs(diff_pct):.1f}% underpaid"
                    )
                else:
                    st.metric(
                        "Market Adjustment",
                        f"-${abs(diff)/1000:.0f}K",
                        f"{abs(diff_pct):.1f}% overpaid"
                    )

        # Salary range visualization
        st.markdown("### Salary Range Analysis")

        fig = go.Figure()

        # Add peer range
        fig.add_trace(go.Scatter(
            x=[est['peer_min']/1000, est['peer_max']/1000],
            y=['Peer Range', 'Peer Range'],
            mode='lines',
            line=dict(color='lightgray', width=8),
            name='Peer Range',
            showlegend=True
        ))

        # Add IQR range
        fig.add_trace(go.Scatter(
            x=[est['salary_range_low']/1000, est['salary_range_high']/1000],
            y=['Negotiation Range', 'Negotiation Range'],
            mode='lines',
            line=dict(color='blue', width=12),
            name='25th-75th Percentile',
            showlegend=True
        ))

        # Add recommended salary
        fig.add_trace(go.Scatter(
            x=[est['predicted_salary']/1000],
            y=['Recommended'],
            mode='markers',
            marker=dict(color='green', size=15, symbol='diamond'),
            name='Recommended',
            showlegend=True
        ))

        # Add current salary if available
        if result.get('actual_salary'):
            fig.add_trace(go.Scatter(
                x=[result['actual_salary']/1000],
                y=['Current'],
                mode='markers',
                marker=dict(color='red', size=15, symbol='star'),
                name='Current Salary',
                showlegend=True
            ))

        fig.update_layout(
            xaxis_title="Salary ($K)",
            yaxis_title="",
            height=300,
            showlegend=True,
            hovermode='closest'
        )

        st.plotly_chart(fig, use_container_width=True)

        # K-NN Peers
        st.header("Statistical Peers")

        with st.expander("ℹ️ About Peer Comparison"):
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
                'Salary': f"${salary/1000:.0f}K"
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

        # Get peer comparison data
        peer_comparison = get_peer_comparison_data(system, selected_player, est['peer_names'][:5])

        if peer_comparison:
            comparison_df, stat_categories = peer_comparison

            # Create tabs for each category
            category_tabs = st.tabs(list(stat_categories.keys()))

            for tab, (category_name, category_info) in zip(category_tabs, stat_categories.items()):
                with tab:
                    # Create radar chart
                    fig = create_radar_chart(
                        comparison_df,
                        selected_player,
                        est['peer_names'][:5],
                        category_name,
                        category_info['stats'],
                        category_info['labels']
                    )

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"Insufficient data for {category_name} comparison")
        else:
            st.warning("Could not load peer comparison data")

        # Peer salary distribution - collapsible for advanced users
        with st.expander("📊 View Peer Salary Distribution"):
            # Create dataframe with numeric salary values for histogram
            peer_salary_data = pd.DataFrame({
                'Salary ($K)': [s/1000 for s in est['peer_salaries']]
            })

            fig = px.histogram(
                peer_salary_data,
                x='Salary ($K)',
                nbins=10,
                labels={'Salary ($K)': 'Salary ($K)', 'count': 'Number of Players'}
            )

            # Add vertical line for recommended salary
            fig.add_vline(
                x=est['predicted_salary']/1000,
                line_dash="dash",
                line_color="green",
                annotation_text="Recommended",
                annotation_position="top"
            )

            # Add vertical line for current salary if available
            if result.get('actual_salary'):
                fig.add_vline(
                    x=result['actual_salary']/1000,
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
        "**MLS Free Agent Valuator** | Data: 2025 Season | "
        "Model: K-Nearest Neighbors + Random Forest Classification | "
        f"Analyzing {len(fa_df)} free agents with contracts expiring in 2025"
    )

if __name__ == "__main__":
    main()
