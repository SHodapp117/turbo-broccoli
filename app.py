"""
MLS Player Valuation App - Streamlit Interface

Interactive application to value MLS players and see their statistical peers.
"""

import streamlit as st
import pandas as pd
import numpy as np
from Player_Valuation import PlayerValuationSystem
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="MLS Player Valuation",
    page_icon="⚽",
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

# Cache player list
@st.cache_data
def get_player_list(_system):
    """Get list of players with sufficient data"""
    df = _system.df_master

    # Filter to players with enough minutes
    df_filtered = df[df['Minutes'] >= 270].copy()

    # Get unique players
    players = sorted(df_filtered['Player'].unique())

    return players, df_filtered

# Main app
def main():
    st.title("⚽ MLS Player Valuation System")
    st.markdown("### Statistical Contract Analysis Tool")

    # Load system
    system = load_valuation_system()
    players, df_players = get_player_list(system)

    # Sidebar
    st.sidebar.header("Player Selection")

    # Filter options
    position_filter = st.sidebar.multiselect(
        "Filter by Position",
        options=['All', 'FW', 'MF', 'DF', 'GK'],
        default=['All']
    )

    # Apply position filter
    if 'All' not in position_filter and position_filter:
        filtered_players = df_players[df_players['position_group'].isin(position_filter)]['Player'].unique()
        available_players = sorted(set(players) & set(filtered_players))
    else:
        available_players = players

    # Player selection
    selected_player = st.sidebar.selectbox(
        "Select Player",
        options=available_players,
        index=0 if available_players else None
    )

    # Info sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This tool uses K-Nearest Neighbors to find statistically similar players "
        "and estimate contract values based on peer comparisons.\n\n"
        "**Data includes:**\n"
        "- 2025 MLS season stats\n"
        "- 685 players with 270+ minutes\n"
        "- Performance-based clustering"
    )

    if not selected_player:
        st.warning("No players available with current filters")
        return

    # Value the selected player
    with st.spinner(f"Analyzing {selected_player}..."):
        result = system.value_player(selected_player)

    if 'error' in result:
        st.error(f"Error: {result['error']}")
        return

    # Display results
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Position",
            result['position'],
            delta=None
        )

    with col2:
        st.metric(
            "Minutes Played",
            f"{result['minutes']:.0f}",
            delta=None
        )

    with col3:
        if 'predicted_designation' in result:
            st.metric(
                "Contract Tier",
                result['predicted_designation'],
                delta=f"{max(result.get('designation_confidence', {}).values())*100:.0f}% confidence" if 'designation_confidence' in result else None
            )
        else:
            st.metric("Contract Tier", result.get('actual_designation', 'Unknown'))

    # Salary estimation
    if 'salary_estimate' in result and 'predicted_salary' in result['salary_estimate']:
        est = result['salary_estimate']

        st.markdown("---")
        st.header("💰 Contract Valuation")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Recommended Salary",
                f"${est['predicted_salary']/1000:.0f}K",
                delta=None
            )

        with col2:
            st.metric(
                "25th Percentile",
                f"${est['salary_range_low']/1000:.0f}K",
                delta="Low end"
            )

        with col3:
            st.metric(
                "75th Percentile",
                f"${est['salary_range_high']/1000:.0f}K",
                delta="High end"
            )

        with col4:
            if result.get('actual_salary'):
                diff = est['predicted_salary'] - result['actual_salary']
                st.metric(
                    "Current Salary",
                    f"${result['actual_salary']/1000:.0f}K",
                    delta=f"{diff/1000:+.0f}K ({abs(diff)/result['actual_salary']*100:.1f}%)"
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
        st.markdown("---")
        st.header("👥 Statistical Peers (K-Nearest Neighbors)")

        st.markdown(
            f"These are the **{est['n_peers']} most similar players** based on "
            f"performance statistics in the same position and contract tier."
        )

        # Create peer comparison dataframe
        peer_data = {
            'Rank': list(range(1, len(est['peer_names']) + 1)),
            'Player': est['peer_names'],
            'Salary ($K)': [s/1000 for s in est['peer_salaries']],
        }

        df_peers = pd.DataFrame(peer_data)

        # Highlight the selected player
        def highlight_selected(row):
            if row['Player'] == selected_player:
                return ['background-color: #ffeb3b'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df_peers.style.apply(highlight_selected, axis=1).format({
                'Salary ($K)': '{:.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )

        # Peer salary distribution
        st.markdown("### Peer Salary Distribution")

        fig = px.histogram(
            df_peers,
            x='Salary ($K)',
            nbins=10,
            title=f"Salary Distribution of {selected_player}'s Statistical Peers",
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

        # Archetype info
        if 'archetype' in result:
            st.markdown("---")
            st.header("🎯 Player Archetype")

            if result.get('is_outlier'):
                st.success("**Elite/Specialist Player** (Statistical Outlier)")
                st.markdown(
                    "This player has a unique statistical profile that stands out "
                    "from typical players in their position."
                )
            else:
                st.info(f"**Archetype {result['archetype']}**")
                st.markdown(
                    f"This player fits the typical performance profile for "
                    f"{result['position']} players in MLS."
                )

        # Designation confidence
        if 'designation_confidence' in result:
            st.markdown("---")
            st.header("📊 Contract Tier Probabilities")

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
                title="Predicted Contract Tier Confidence",
                labels={'Probability': 'Confidence', 'Tier': 'Contract Tier'},
                color='Probability',
                color_continuous_scale='Blues'
            )

            fig.update_layout(showlegend=False, yaxis_tickformat='.0%')

            st.plotly_chart(fig, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "MLS Player Valuation System | Data: 2025 Season | "
        "Model: K-Nearest Neighbors + Random Forest Classification"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
