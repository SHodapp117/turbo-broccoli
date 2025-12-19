import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from state_tax_data import MLS_TEAMS, STATE_TAX_INFO, get_effective_tax_rate, get_tax_burden_comparison
from city_demographics import CITY_DEMOGRAPHICS, get_diversity_index, get_minority_percentage, get_cities_by_majority, get_most_diverse_cities, get_demographic_summary
from detailed_demographics import DETAILED_CITY_DEMOGRAPHICS, get_detailed_demographics, get_top_ancestries, compare_ancestry_across_cities, get_diversity_by_category
from player_affinity_score import (PLAYER_ORIGINS, calculate_overall_affinity_score, rank_cities_for_player,
                                   compare_players_for_city, get_affinity_insights, SCORING_METHODOLOGY)

# Page configuration
st.set_page_config(
    page_title="Player Affinity Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("⚽ Player Affinity Dashboard")
st.markdown("Analyze player performance metrics and team dynamics")

# Sidebar
with st.sidebar:
    st.header("Filters")
    st.markdown("Configure your dashboard filters here")

    # Example filters - customize based on your data
    season = st.selectbox("Season", ["2024", "2023", "2022"])
    team = st.multiselect("Teams", ["Team A", "Team B", "Team C", "Team D"])

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ MLS Map", "💰 State Tax Analysis", "🌎 City Demographics", "🎯 Player Affinity Score"])

with tab1:
    st.header("MLS Teams Map")
    st.markdown("Geographic distribution of all 30 MLS teams across the United States")

    # City coordinates for MLS teams with logo URLs
    CITY_COORDINATES = {
        'Los Angeles': {'lat': 34.0522, 'lon': -118.2437, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9725.png'},
        'Carson': {'lat': 33.8317, 'lon': -118.2820, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9724.png'},
        'San Jose': {'lat': 37.3382, 'lon': -121.8863, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9731.png'},
        'San Diego': {'lat': 32.7157, 'lon': -117.1611, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/27517.png'},
        'Denver': {'lat': 39.7392, 'lon': -104.9903, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9728.png'},
        'Miami': {'lat': 25.7617, 'lon': -80.1918, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/13796.png'},
        'Orlando': {'lat': 28.5383, 'lon': -81.3792, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9808.png'},
        'Atlanta': {'lat': 33.7490, 'lon': -84.3880, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9723.png'},
        'Chicago': {'lat': 41.8781, 'lon': -87.6298, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9726.png'},
        'Kansas City': {'lat': 39.0997, 'lon': -94.5786, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9732.png'},
        'Boston': {'lat': 42.3601, 'lon': -71.0589, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9729.png'},
        'St. Paul': {'lat': 44.9537, 'lon': -93.0900, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/11991.png'},
        'St. Louis': {'lat': 38.6270, 'lon': -90.1994, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/22012.png'},
        'Harrison': {'lat': 40.7396, 'lon': -74.1518, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9730.png'},
        'New York': {'lat': 40.7128, 'lon': -74.0060, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9880.png'},
        'Charlotte': {'lat': 35.2271, 'lon': -80.8431, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/14008.png'},
        'Columbus': {'lat': 39.9612, 'lon': -82.9988, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9727.png'},
        'Cincinnati': {'lat': 39.1031, 'lon': -84.5120, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/13192.png'},
        'Portland': {'lat': 45.5152, 'lon': -122.6784, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/11212.png'},
        'Philadelphia': {'lat': 39.9526, 'lon': -75.1652, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/10521.png'},
        'Nashville': {'lat': 36.1627, 'lon': -86.7816, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/13530.png'},
        'Austin': {'lat': 30.2672, 'lon': -97.7431, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/14007.png'},
        'Houston': {'lat': 29.7604, 'lon': -95.3698, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9722.png'},
        'Frisco': {'lat': 33.1507, 'lon': -96.8236, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9733.png'},
        'Salt Lake City': {'lat': 40.7608, 'lon': -111.8910, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/10014.png'},
        'Seattle': {'lat': 47.6062, 'lon': -122.3321, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9734.png'},
        'Washington': {'lat': 38.9072, 'lon': -77.0369, 'logo': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/9721.png'}
    }

    # Create map dataframe
    map_data = []
    for city, coords in CITY_COORDINATES.items():
        city_info = CITY_DEMOGRAPHICS[city]
        map_data.append({
            'City': city,
            'Team': city_info['team'],
            'lat': coords['lat'],
            'lon': coords['lon'],
            'logo': coords['logo'],
            'State': city_info['state'],
            'Population': city_info['population'],
            'Majority': city_info['majority']
        })

    map_df = pd.DataFrame(map_data)

    # Display team logos on US map using HTML/CSS overlay approach
    st.markdown("### Interactive MLS Teams Map")

    # Create HTML for team logo display on map
    html_logos = """
    <style>
    .map-container {
        position: relative;
        width: 100%;
        height: 700px;
        background: linear-gradient(to bottom, #87CEEB 0%, #E0F6FF 50%, #90EE90 100%);
        border-radius: 10px;
        overflow: hidden;
    }
    .team-logo {
        position: absolute;
        width: 40px;
        height: 40px;
        transform: translate(-50%, -50%);
        cursor: pointer;
        transition: all 0.3s ease;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
    }
    .team-logo:hover {
        width: 60px;
        height: 60px;
        z-index: 1000;
    }
    .team-info {
        position: absolute;
        background: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-size: 11px;
        display: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1001;
        white-space: nowrap;
    }
    .team-logo:hover + .team-info {
        display: block;
    }
    </style>
    <div class="map-container">
    """

    # Map coordinates to pixel positions (rough projection for continental US)
    # US bounds: lat 25-50, lon -125 to -65
    for idx, row in map_df.iterrows():
        # Convert lat/lon to percentage positions
        x_pct = ((row['lon'] + 125) / 60) * 100  # Normalize longitude
        y_pct = 100 - ((row['lat'] - 25) / 25) * 100  # Normalize latitude (inverted)

        html_logos += f"""
        <img src="{row['logo']}"
             class="team-logo"
             style="left: {x_pct}%; top: {y_pct}%;"
             alt="{row['Team']}"
             title="{row['Team']} - {row['City']}, {row['State']}">
        <div class="team-info" style="left: {x_pct}%; top: {y_pct + 5}%;">
            <strong>{row['Team']}</strong><br>
            {row['City']}, {row['State']}<br>
            Pop: {row['Population']:,}
        </div>
        """

    html_logos += "</div>"

    st.markdown(html_logos, unsafe_allow_html=True)

    st.markdown("*Hover over team logos to see details*")

    st.divider()

    # Summary statistics
    st.subheader("Geographic Distribution Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Teams", len(map_df))
    with col2:
        states_count = map_df['State'].nunique()
        st.metric("States Represented", states_count)
    with col3:
        # East vs West divide (Mississippi River ~-95° longitude)
        western_teams = len(map_df[map_df['lon'] < -95])
        st.metric("Western Teams", western_teams)
    with col4:
        eastern_teams = len(map_df[map_df['lon'] >= -95])
        st.metric("Eastern Teams", eastern_teams)

    st.divider()

    # Teams by state
    st.subheader("Teams by State")

    teams_by_state = map_df.groupby('State').agg({
        'Team': list,
        'City': 'count'
    }).reset_index()
    teams_by_state.columns = ['State', 'Teams', 'Count']
    teams_by_state = teams_by_state.sort_values('Count', ascending=False)

    # Format teams list for display
    teams_by_state['Teams'] = teams_by_state['Teams'].apply(lambda x: ', '.join(x))

    st.dataframe(
        teams_by_state,
        use_container_width=True,
        hide_index=True,
        column_config={
            'State': st.column_config.TextColumn('State', width='medium'),
            'Count': st.column_config.NumberColumn('# of Teams', width='small'),
            'Teams': st.column_config.TextColumn('Teams', width='large')
        }
    )

with tab2:
    st.header("State Income Tax Analysis for MLS Teams")
    st.markdown("Complete 2025 income tax schedules for all states where MLS teams operate")

    # Tax burden comparison
    tax_comparison = get_tax_burden_comparison()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total MLS States", tax_comparison['total_states'])
    with col2:
        st.metric("No Income Tax", len(tax_comparison['no_tax_states']))
    with col3:
        st.metric("Flat Tax States", len(tax_comparison['flat_tax_states']))
    with col4:
        st.metric("Avg Top Rate", f"{tax_comparison['average_top_rate']:.2f}%")

    st.divider()

    # Tax type breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tax System Distribution")
        tax_type_counts = {
            'No Income Tax': len(tax_comparison['no_tax_states']),
            'Flat Tax': len(tax_comparison['flat_tax_states']),
            'Progressive Tax': len(tax_comparison['progressive_tax_states'])
        }
        fig = px.pie(
            values=list(tax_type_counts.values()),
            names=list(tax_type_counts.keys()),
            title='MLS States by Tax System Type',
            color_discrete_sequence=['#00D9FF', '#FFB800', '#FF6B6B']
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Tax Rates by State")
        top_rates_df = pd.DataFrame([
            {'State': state, 'Top Rate': info['top_rate'], 'Type': info['tax_type']}
            for state, info in STATE_TAX_INFO.items()
        ]).sort_values('Top Rate', ascending=False).head(10)

        fig = px.bar(
            top_rates_df,
            x='State',
            y='Top Rate',
            color='Type',
            title='Top 10 Highest Tax Rates',
            labels={'Top Rate': 'Top Rate (%)'},
            color_discrete_map={'Progressive': '#FF6B6B', 'Flat': '#FFB800', 'None': '#00D9FF'}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # State-by-state breakdown
    st.subheader("State-by-State Tax Information")

    # State selector
    selected_state = st.selectbox(
        "Select State",
        sorted(STATE_TAX_INFO.keys()),
        index=0
    )

    if selected_state:
        state_info = STATE_TAX_INFO[selected_state]
        teams_in_state = MLS_TEAMS[selected_state]

        # State overview
        st.markdown(f"### {selected_state}")
        st.markdown(f"**MLS Teams:** {', '.join(teams_in_state)}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tax Type", state_info['tax_type'])
        with col2:
            if state_info['tax_type'] == 'Flat':
                st.metric("Tax Rate", f"{state_info['rate']}%")
            else:
                st.metric("Top Rate", f"{state_info['top_rate']}%")
        with col3:
            if state_info.get('standard_deduction_single'):
                st.metric("Std Deduction (Single)", f"${state_info['standard_deduction_single']:,}")
            else:
                st.metric("Std Deduction", "N/A")

        # Notes
        if state_info.get('notes'):
            st.info(f"📌 {state_info['notes']}")

        # Tax brackets (if progressive)
        if state_info['tax_type'] == 'Progressive':
            st.markdown("#### Tax Brackets (Single Filer)")
            brackets_df = pd.DataFrame(state_info['brackets'])
            brackets_df['Income Range'] = brackets_df.apply(
                lambda x: f"${x['min']:,.0f} - ${x['max']:,.0f}" if x['max'] != float('inf')
                else f"${x['min']:,.0f}+",
                axis=1
            )
            brackets_df['Tax Rate'] = brackets_df['rate'].apply(lambda x: f"{x}%")

            st.dataframe(
                brackets_df[['Income Range', 'Tax Rate']],
                use_container_width=True,
                hide_index=True
            )

            # Visualize bracket structure
            fig = go.Figure()
            for i, bracket in enumerate(state_info['brackets']):
                if bracket['max'] != float('inf'):
                    fig.add_trace(go.Bar(
                        x=[f"${bracket['min']:,.0f} - ${bracket['max']:,.0f}"],
                        y=[bracket['rate']],
                        name=f"{bracket['rate']}%",
                        text=f"{bracket['rate']}%",
                        textposition='auto',
                    ))

            fig.update_layout(
                title=f"{selected_state} Tax Bracket Rates",
                xaxis_title="Income Range",
                yaxis_title="Tax Rate (%)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Tax calculator
    st.subheader("Tax Impact Calculator")
    st.markdown("Calculate effective tax rates across different income levels")

    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:
        income_level = st.number_input(
            "Annual Income ($)",
            min_value=0,
            max_value=10000000,
            value=100000,
            step=10000,
            format="%d"
        )

    with calc_col2:
        filing_status = st.selectbox("Filing Status", ["Single", "Joint"])

    # Calculate effective rates for all states
    if income_level > 0:
        tax_rates = []
        for state in STATE_TAX_INFO.keys():
            eff_rate = get_effective_tax_rate(state, income_level, filing_status.lower())
            teams = ', '.join(MLS_TEAMS[state])
            tax_amount = income_level * (eff_rate / 100)

            tax_rates.append({
                'State': state,
                'MLS Teams': teams,
                'Effective Rate': f"{eff_rate:.2f}%",
                'Estimated Tax': f"${tax_amount:,.2f}",
                'Tax Amount': tax_amount,
                'Rate Value': eff_rate
            })

        tax_rates_df = pd.DataFrame(tax_rates).sort_values('Rate Value', ascending=False)

        st.markdown(f"#### Tax Comparison at ${income_level:,} Income")

        # Show comparison chart
        fig = px.bar(
            tax_rates_df,
            x='State',
            y='Rate Value',
            hover_data=['MLS Teams', 'Estimated Tax'],
            title=f'Effective Tax Rates at ${income_level:,} Income',
            labels={'Rate Value': 'Effective Tax Rate (%)'},
            color='Rate Value',
            color_continuous_scale='Reds'
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Show detailed table
        st.dataframe(
            tax_rates_df[['State', 'MLS Teams', 'Effective Rate', 'Estimated Tax']],
            use_container_width=True,
            hide_index=True
        )

        # Tax savings comparison
        st.markdown("#### Tax Burden Comparison")
        max_tax_state = tax_rates_df.iloc[0]
        min_tax_state = tax_rates_df.iloc[-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Highest Tax State", max_tax_state['State'], max_tax_state['Effective Rate'])
        with col2:
            st.metric("Lowest Tax State", min_tax_state['State'], min_tax_state['Effective Rate'])
        with col3:
            savings = max_tax_state['Tax Amount'] - min_tax_state['Tax Amount']
            st.metric("Max Potential Savings", f"${savings:,.2f}")

    st.divider()

    # All states summary table
    st.subheader("Complete State Tax Summary")

    summary_data = []
    for state, info in STATE_TAX_INFO.items():
        teams = ', '.join(MLS_TEAMS[state])
        summary_data.append({
            'State': state,
            'MLS Teams': teams,
            'Team Count': len(MLS_TEAMS[state]),
            'Tax Type': info['tax_type'],
            'Top Rate': f"{info['top_rate']}%",
            'Notes': info.get('notes', '')
        })

    summary_df = pd.DataFrame(summary_data).sort_values('State')
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.divider()

    # Salary Breakdown by Club
    st.subheader("💰 Player Salary Breakdown by MLS Club")
    st.markdown("See how a proposed base salary gets deducted by state and federal taxes for each MLS team")

    salary_col1, salary_col2 = st.columns(2)

    with salary_col1:
        proposed_salary = st.number_input(
            "Proposed Annual Base Salary ($)",
            min_value=100000,
            max_value=15000000,
            value=1000000,
            step=100000,
            format="%d",
            key="salary_breakdown"
        )

    with salary_col2:
        filing_status_breakdown = st.selectbox(
            "Filing Status",
            ["Single", "Joint"],
            key="filing_breakdown"
        )

    if proposed_salary > 0:
        # Federal tax rates for 2025 (approximation for single filer)
        def calculate_federal_tax(income, status='single'):
            """Calculate approximate federal income tax"""
            if status.lower() == 'single':
                brackets = [
                    (11600, 0.10),
                    (47150, 0.12),
                    (100525, 0.22),
                    (191950, 0.24),
                    (243725, 0.32),
                    (609350, 0.35),
                    (float('inf'), 0.37)
                ]
            else:  # joint
                brackets = [
                    (23200, 0.10),
                    (94300, 0.12),
                    (201050, 0.22),
                    (383900, 0.24),
                    (487450, 0.32),
                    (731200, 0.35),
                    (float('inf'), 0.37)
                ]

            tax = 0
            prev_limit = 0
            for limit, rate in brackets:
                if income > prev_limit:
                    taxable = min(income, limit) - prev_limit
                    tax += taxable * rate
                    prev_limit = limit
                else:
                    break
            return tax

        # Calculate for all MLS clubs
        club_salary_data = []

        for state, teams in MLS_TEAMS.items():
            state_effective_rate = get_effective_tax_rate(state, proposed_salary, filing_status_breakdown.lower())
            state_tax = proposed_salary * (state_effective_rate / 100)
            federal_tax = calculate_federal_tax(proposed_salary, filing_status_breakdown.lower())
            total_tax = state_tax + federal_tax
            take_home = proposed_salary - total_tax
            effective_combined_rate = (total_tax / proposed_salary * 100)

            for team in teams:
                club_salary_data.append({
                    'Team': team,
                    'State': state,
                    'Base Salary': proposed_salary,
                    'State Tax': state_tax,
                    'Federal Tax': federal_tax,
                    'Total Tax': total_tax,
                    'Take Home Pay': take_home,
                    'State Tax Rate': state_effective_rate,
                    'Effective Combined Rate': effective_combined_rate
                })

        club_salary_df = pd.DataFrame(club_salary_data).sort_values('Take Home Pay', ascending=False)

        st.markdown(f"#### Salary Breakdown: ${proposed_salary:,} Base Salary")

        # Summary metrics
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        best_club = club_salary_df.iloc[0]
        worst_club = club_salary_df.iloc[-1]
        max_savings = worst_club['Total Tax'] - best_club['Total Tax']

        with summary_col1:
            st.metric("Best Take-Home", best_club['Team'], f"${best_club['Take Home Pay']:,.0f}")
        with summary_col2:
            st.metric("Worst Take-Home", worst_club['Team'], f"${worst_club['Take Home Pay']:,.0f}")
        with summary_col3:
            st.metric("Maximum Difference", f"${max_savings:,.0f}",
                     f"{((max_savings/proposed_salary)*100):.1f}% of salary")
        with summary_col4:
            avg_take_home = club_salary_df['Take Home Pay'].mean()
            st.metric("Average Take-Home", f"${avg_take_home:,.0f}")

        # Visualization: Take-Home Pay by Club
        fig = px.bar(
            club_salary_df,
            x='Team',
            y='Take Home Pay',
            color='Effective Combined Rate',
            title=f'Take-Home Pay by MLS Club (${proposed_salary:,} Base Salary)',
            labels={'Take Home Pay': 'Take-Home Pay ($)', 'Effective Combined Rate': 'Tax Rate (%)'},
            color_continuous_scale='RdYlGn_r',
            hover_data={
                'State': True,
                'Total Tax': ':$,.0f',
                'Effective Combined Rate': ':.2f%'
            }
        )
        fig.update_layout(height=600, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        # Stacked bar chart showing tax breakdown
        st.markdown("#### Tax Breakdown by Club")

        # Create data for stacked chart
        stacked_data = []
        for _, row in club_salary_df.iterrows():
            stacked_data.append({
                'Team': row['Team'],
                'Category': 'Take Home',
                'Amount': row['Take Home Pay']
            })
            stacked_data.append({
                'Team': row['Team'],
                'Category': 'Federal Tax',
                'Amount': row['Federal Tax']
            })
            stacked_data.append({
                'Team': row['Team'],
                'Category': 'State Tax',
                'Amount': row['State Tax']
            })

        stacked_df = pd.DataFrame(stacked_data)

        fig = px.bar(
            stacked_df,
            x='Team',
            y='Amount',
            color='Category',
            title=f'Salary Breakdown: Take-Home vs Taxes',
            labels={'Amount': 'Amount ($)'},
            color_discrete_map={
                'Take Home': '#2ECC71',
                'Federal Tax': '#E74C3C',
                'State Tax': '#F39C12'
            }
        )
        fig.update_layout(
            barmode='stack',
            height=600,
            xaxis_tickangle=-45,
            yaxis_title='Amount ($)'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Detailed table
        st.markdown("#### Detailed Salary Breakdown")

        display_salary_df = club_salary_df.copy()
        display_salary_df['Base Salary'] = display_salary_df['Base Salary'].apply(lambda x: f"${x:,.0f}")
        display_salary_df['State Tax'] = display_salary_df.apply(
            lambda x: f"${x['State Tax']:,.0f} ({x['State Tax Rate']:.2f}%)", axis=1
        )
        display_salary_df['Federal Tax'] = display_salary_df['Federal Tax'].apply(lambda x: f"${x:,.0f}")
        display_salary_df['Total Tax'] = display_salary_df.apply(
            lambda x: f"${x['Total Tax']:,.0f} ({x['Effective Combined Rate']:.2f}%)", axis=1
        )
        display_salary_df['Take Home Pay'] = display_salary_df['Take Home Pay'].apply(lambda x: f"${x:,.0f}")

        st.dataframe(
            display_salary_df[['Team', 'State', 'Base Salary', 'State Tax', 'Federal Tax', 'Total Tax', 'Take Home Pay']],
            use_container_width=True,
            hide_index=True
        )

        # Download option
        csv_salary = club_salary_df.to_csv(index=False)
        st.download_button(
            label="Download Salary Breakdown (CSV)",
            data=csv_salary,
            file_name=f"mls_salary_breakdown_{proposed_salary}.csv",
            mime="text/csv"
        )

        # Key insights
        st.markdown("#### 💡 Key Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Best States for Players (Lowest Tax):**")
            no_tax_states = club_salary_df[club_salary_df['State Tax Rate'] == 0]['State'].unique()
            for state in no_tax_states:
                teams_in_state = club_salary_df[club_salary_df['State'] == state]['Team'].tolist()
                st.success(f"✅ **{state}**: {', '.join(teams_in_state)} - No state income tax")

        with col2:
            st.markdown("**Highest Tax Burden:**")
            top_5_tax = club_salary_df.nlargest(5, 'Total Tax')
            for _, row in top_5_tax.iterrows():
                st.warning(f"⚠️ **{row['Team']}** ({row['State']}): ${row['Total Tax']:,.0f} total tax ({row['Effective Combined Rate']:.2f}%)")

with tab5:
    st.header("City Demographics Analysis")
    st.markdown("2020 Census data for all MLS cities - race and ethnicity breakdown")

    # Get demographic summary
    demo_summary = get_demographic_summary()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total MLS Cities", demo_summary['total_cities'])
    with col2:
        avg_white = demo_summary['average_demographics']['White']
        st.metric("Avg White Population", f"{avg_white}%")
    with col3:
        avg_minority = 100 - avg_white
        st.metric("Avg Minority Population", f"{avg_minority:.1f}%")
    with col4:
        most_diverse = demo_summary['most_diverse'][0]
        st.metric("Most Diverse City", most_diverse[0])

    st.divider()

    # Majority breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Cities by Ethnic Majority")
        majority_data = demo_summary['majority_breakdown']
        fig = px.pie(
            values=list(majority_data.values()),
            names=list(majority_data.keys()),
            title='MLS Cities by Ethnic Majority (2020 Census)',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show cities by majority
        cities_by_maj = get_cities_by_majority()
        for majority, cities in cities_by_maj.items():
            with st.expander(f"{majority} Majority Cities ({len(cities)})"):
                for city in sorted(cities):
                    team = CITY_DEMOGRAPHICS[city]['team']
                    st.write(f"• {city} - {team}")

    with col2:
        st.subheader("Most Diverse MLS Cities")
        diverse_cities = get_most_diverse_cities(10)
        diversity_df = pd.DataFrame(diverse_cities, columns=['City', 'Diversity Index'])
        diversity_df['Team'] = diversity_df['City'].apply(lambda x: CITY_DEMOGRAPHICS[x]['team'])

        fig = px.bar(
            diversity_df,
            x='City',
            y='Diversity Index',
            title='Top 10 Most Diverse MLS Cities (Simpson\'s Diversity Index)',
            labels={'Diversity Index': 'Diversity Index (0-1)'},
            color='Diversity Index',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Average demographic breakdown
    st.subheader("Average Demographic Composition Across All MLS Cities")
    avg_demo = demo_summary['average_demographics']
    avg_demo_df = pd.DataFrame({
        'Ethnicity': list(avg_demo.keys()),
        'Percentage': list(avg_demo.values())
    }).sort_values('Percentage', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            avg_demo_df,
            x='Ethnicity',
            y='Percentage',
            title='Average Demographics Across MLS Cities',
            color='Ethnicity',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            avg_demo_df,
            values='Percentage',
            names='Ethnicity',
            title='Demographic Distribution',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # City-by-city breakdown
    st.subheader("City-by-City Demographic Breakdown")

    selected_city = st.selectbox(
        "Select City",
        sorted(CITY_DEMOGRAPHICS.keys()),
        index=0,
        key="city_selector"
    )

    if selected_city:
        city_data = CITY_DEMOGRAPHICS[selected_city]

        # City overview
        st.markdown(f"### {selected_city}, {city_data['state']}")
        st.markdown(f"**Team:** {city_data['team']}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Population", f"{city_data['population']:,}")
        with col2:
            st.metric("Ethnic Majority", city_data['majority'])
        with col3:
            diversity = get_diversity_index(selected_city)
            st.metric("Diversity Index", f"{diversity:.3f}")
        with col4:
            minority_pct = get_minority_percentage(selected_city)
            st.metric("Minority %", f"{minority_pct}%")

        # Demographic breakdown
        st.markdown("#### Demographic Breakdown")
        demo_data = city_data['demographics']
        demo_df = pd.DataFrame({
            'Ethnicity': list(demo_data.keys()),
            'Percentage': list(demo_data.values())
        }).sort_values('Percentage', ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                demo_df,
                x='Ethnicity',
                y='Percentage',
                title=f'{selected_city} Demographics',
                color='Ethnicity',
                text='Percentage',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                demo_df,
                values='Percentage',
                names='Ethnicity',
                title=f'{selected_city} Ethnic Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)

        # Show detailed percentages
        st.dataframe(
            demo_df.style.background_gradient(subset=['Percentage'], cmap='YlOrRd'),
            use_container_width=True,
            hide_index=True
        )

        # Detailed Ancestry Breakdown (if available)
        if selected_city in DETAILED_CITY_DEMOGRAPHICS:
            st.markdown("---")
            st.markdown("### Detailed Ancestry/Origin Breakdown")
            st.markdown(f"Granular demographic data for {selected_city} by specific ancestry and origin groups")

            detailed_data = get_detailed_demographics(selected_city)

            # Create tabs for each demographic category
            detail_tabs = st.tabs(["🌏 Asian Origins", "🌎 Hispanic/Latino Origins", "🌍 European Ancestry", "🌍 African/Caribbean Origins"])

            # Asian Origins Tab
            with detail_tabs[0]:
                if 'Asian_Detailed' in detailed_data:
                    asian_data = detailed_data['Asian_Detailed']
                    asian_df = pd.DataFrame({
                        'Origin': list(asian_data.keys()),
                        'Percentage': list(asian_data.values())
                    }).sort_values('Percentage', ascending=False)

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.bar(
                            asian_df,
                            x='Origin',
                            y='Percentage',
                            title=f'Asian Population by Origin - {selected_city}',
                            color='Percentage',
                            color_continuous_scale='Teal'
                        )
                        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.pie(
                            asian_df,
                            values='Percentage',
                            names='Origin',
                            title=f'Asian Origin Distribution',
                            color_discrete_sequence=px.colors.sequential.Teal
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        asian_df.style.background_gradient(subset=['Percentage'], cmap='Teal'),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Diversity index for Asian category
                    asian_diversity = get_diversity_by_category(selected_city, 'Asian_Detailed')
                    st.metric("Asian Population Diversity Index", f"{asian_diversity:.3f}")

                else:
                    st.info("Detailed Asian origin data not yet available for this city")

            # Hispanic/Latino Origins Tab
            with detail_tabs[1]:
                if 'Hispanic_Detailed' in detailed_data:
                    hispanic_data = detailed_data['Hispanic_Detailed']
                    hispanic_df = pd.DataFrame({
                        'Origin': list(hispanic_data.keys()),
                        'Percentage': list(hispanic_data.values())
                    }).sort_values('Percentage', ascending=False)

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.bar(
                            hispanic_df,
                            x='Origin',
                            y='Percentage',
                            title=f'Hispanic/Latino Population by Origin - {selected_city}',
                            color='Percentage',
                            color_continuous_scale='Reds'
                        )
                        fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=500)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # Show only top 8 in pie chart for readability
                        top_hispanic = hispanic_df.head(8).copy()
                        other_sum = hispanic_df.iloc[8:]['Percentage'].sum() if len(hispanic_df) > 8 else 0
                        if other_sum > 0:
                            top_hispanic = pd.concat([top_hispanic, pd.DataFrame({'Origin': ['Other'], 'Percentage': [other_sum]})])

                        fig = px.pie(
                            top_hispanic,
                            values='Percentage',
                            names='Origin',
                            title=f'Hispanic/Latino Origin Distribution (Top 8)',
                            color_discrete_sequence=px.colors.sequential.Reds
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        hispanic_df.style.background_gradient(subset=['Percentage'], cmap='Reds'),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Diversity index for Hispanic category
                    hispanic_diversity = get_diversity_by_category(selected_city, 'Hispanic_Detailed')
                    st.metric("Hispanic/Latino Population Diversity Index", f"{hispanic_diversity:.3f}")

                else:
                    st.info("Detailed Hispanic/Latino origin data not yet available for this city")

            # European Ancestry Tab
            with detail_tabs[2]:
                if 'White_Detailed' in detailed_data:
                    white_data = detailed_data['White_Detailed']
                    white_df = pd.DataFrame({
                        'Ancestry': list(white_data.keys()),
                        'Percentage': list(white_data.values())
                    }).sort_values('Percentage', ascending=False)

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.bar(
                            white_df,
                            x='Ancestry',
                            y='Percentage',
                            title=f'European Ancestry - {selected_city}',
                            color='Percentage',
                            color_continuous_scale='Blues'
                        )
                        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.pie(
                            white_df,
                            values='Percentage',
                            names='Ancestry',
                            title=f'European Ancestry Distribution',
                            color_discrete_sequence=px.colors.sequential.Blues
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        white_df.style.background_gradient(subset=['Percentage'], cmap='Blues'),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Diversity index for White category
                    white_diversity = get_diversity_by_category(selected_city, 'White_Detailed')
                    st.metric("European Ancestry Diversity Index", f"{white_diversity:.3f}")

                else:
                    st.info("Detailed European ancestry data not yet available for this city")

            # African/Caribbean Origins Tab
            with detail_tabs[3]:
                if 'Black_Detailed' in detailed_data:
                    black_data = detailed_data['Black_Detailed']
                    black_df = pd.DataFrame({
                        'Origin': list(black_data.keys()),
                        'Percentage': list(black_data.values())
                    }).sort_values('Percentage', ascending=False)

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.bar(
                            black_df,
                            x='Origin',
                            y='Percentage',
                            title=f'Black/African Population by Origin - {selected_city}',
                            color='Percentage',
                            color_continuous_scale='Greens'
                        )
                        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.pie(
                            black_df,
                            values='Percentage',
                            names='Origin',
                            title=f'Black/African Origin Distribution',
                            color_discrete_sequence=px.colors.sequential.Greens
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        black_df.style.background_gradient(subset=['Percentage'], cmap='Greens'),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Diversity index for Black category
                    black_diversity = get_diversity_by_category(selected_city, 'Black_Detailed')
                    st.metric("Black/African Population Diversity Index", f"{black_diversity:.3f}")

                else:
                    st.info("Detailed Black/African origin data not yet available for this city")

        else:
            st.info(f"💡 Detailed ancestry breakdown not yet available for {selected_city}. Data available for: Los Angeles, San Jose, San Diego, Miami, New York, Chicago, Houston, Atlanta, Philadelphia, and Seattle.")

    st.divider()

    # Comparison tool
    st.subheader("City Comparison Tool")
    st.markdown("Compare demographics between multiple MLS cities")

    compare_cities = st.multiselect(
        "Select cities to compare",
        sorted(CITY_DEMOGRAPHICS.keys()),
        default=sorted(list(CITY_DEMOGRAPHICS.keys()))[:3],
        key="city_compare"
    )

    if len(compare_cities) >= 2:
        # Build comparison dataframe
        comparison_data = []
        for city in compare_cities:
            city_info = CITY_DEMOGRAPHICS[city]
            for ethnicity, pct in city_info['demographics'].items():
                comparison_data.append({
                    'City': city,
                    'Team': city_info['team'],
                    'Ethnicity': ethnicity,
                    'Percentage': pct,
                    'Population': city_info['population']
                })

        comparison_df = pd.DataFrame(comparison_data)

        # Grouped bar chart
        fig = px.bar(
            comparison_df,
            x='City',
            y='Percentage',
            color='Ethnicity',
            barmode='group',
            title='Demographic Comparison',
            labels={'Percentage': 'Population (%)'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Create pivot table for detailed comparison
        pivot_df = comparison_df.pivot_table(
            index='City',
            columns='Ethnicity',
            values='Percentage',
            aggfunc='first'
        ).round(1)
        pivot_df['Majority'] = [CITY_DEMOGRAPHICS[city]['majority'] for city in pivot_df.index]
        pivot_df['Population'] = [f"{CITY_DEMOGRAPHICS[city]['population']:,}" for city in pivot_df.index]
        pivot_df['Diversity'] = [get_diversity_index(city) for city in pivot_df.index]

        st.markdown("#### Detailed Comparison Table")
        st.dataframe(
            pivot_df.style.background_gradient(
                subset=['White', 'Black', 'Asian', 'Hispanic', 'Multiracial'],
                cmap='RdYlGn_r'
            ),
            use_container_width=True
        )

    st.divider()

    # Complete summary table
    st.subheader("Complete Demographics Summary - All MLS Cities")

    all_cities_data = []
    for city, data in CITY_DEMOGRAPHICS.items():
        city_row = {
            'City': city,
            'State': data['state'],
            'Team': data['team'],
            'Population': data['population'],
            'Majority': data['majority'],
            'Diversity': get_diversity_index(city),
            **{k: v for k, v in data['demographics'].items()}
        }
        all_cities_data.append(city_row)

    all_cities_df = pd.DataFrame(all_cities_data).sort_values('City')

    # Format for display
    display_df = all_cities_df.copy()
    display_df['Population'] = display_df['Population'].apply(lambda x: f"{x:,}")

    st.dataframe(
        display_df.style.background_gradient(
            subset=['White', 'Black', 'Asian', 'Hispanic', 'Multiracial'],
            cmap='RdYlGn_r'
        ),
        use_container_width=True,
        hide_index=True
    )

    # Download option
    csv = all_cities_df.to_csv(index=False)
    st.download_button(
        label="Download Complete Demographics Data (CSV)",
        data=csv,
        file_name="mls_city_demographics_2020.csv",
        mime="text/csv"
    )

with tab6:
    st.header("🎯 Player Affinity Score System")
    st.markdown("""
    **Research-Based Player Adaptation Prediction**

    This scoring system combines demographic affinity, language proficiency, and tax burden to predict
    how well international players will adapt to each MLS city.

    Based on peer-reviewed research analyzing 34,430+ international transfers and multiple adaptation studies.
    """)

    # Methodology expander
    with st.expander("📚 Scoring Methodology & Research Basis"):
        st.markdown(SCORING_METHODOLOGY)

    st.divider()

    # Two main modes: Player-to-Cities and City-to-Players
    mode = st.radio(
        "Analysis Mode",
        ["Find Best Cities for a Player", "Compare Players for a City"],
        horizontal=True
    )

    st.divider()

    if mode == "Find Best Cities for a Player":
        st.subheader("Find Best MLS Cities for International Player")

        col1, col2 = st.columns(2)

        with col1:
            player_country = st.selectbox(
                "Player's Country of Origin",
                sorted(PLAYER_ORIGINS.keys()),
                index=sorted(PLAYER_ORIGINS.keys()).index('Mexico')
            )

        with col2:
            annual_salary = st.number_input(
                "Annual Salary ($)",
                min_value=100000,
                max_value=10000000,
                value=500000,
                step=50000,
                help="Used to calculate tax burden component of affinity score"
            )

        # Show player profile
        if player_country:
            player_info = PLAYER_ORIGINS[player_country]
            st.markdown(f"### Player Profile: {player_country}")

            profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)
            with profile_col1:
                st.metric("Primary Ethnicity", player_info['primary_ethnicity'])
            with profile_col2:
                st.metric("Specific Origin", player_info['detailed_group'])
            with profile_col3:
                st.metric("Native Language", player_info['language'])
            with profile_col4:
                english_pct = int(player_info['english_proficiency'] * 100)
                st.metric("English Proficiency", f"{english_pct}%")

        st.divider()

        # Calculate and rank all cities
        city_rankings = rank_cities_for_player(player_country, annual_salary)

        # Show top 10 cities
        st.subheader(f"Top 10 MLS Cities for Players from {player_country}")

        top_10_data = []
        for i, (city, scores) in enumerate(city_rankings[:10], 1):
            city_info = CITY_DEMOGRAPHICS[city]
            top_10_data.append({
                'Rank': i,
                'City': city,
                'Team': city_info['team'],
                'Overall Score': scores['overall_score'],
                'Demographic': scores['demographic_score'],
                'Language': scores['language_score'],
                'Tax': scores['tax_score'],
                'Adaptation': scores['adaptation_category'],
                'Timeline': scores['expected_timeline']
            })

        top_10_df = pd.DataFrame(top_10_data)

        # Visualization
        fig = px.bar(
            top_10_df,
            x='City',
            y='Overall Score',
            color='Overall Score',
            title=f'Top 10 Cities by Affinity Score - {player_country} Players',
            labels={'Overall Score': 'Affinity Score (0-100)'},
            color_continuous_scale='Viridis',
            hover_data=['Team', 'Adaptation', 'Timeline']
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Detailed table
        st.dataframe(
            top_10_df.style.background_gradient(subset=['Overall Score', 'Demographic', 'Language', 'Tax'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Component breakdown for selected city
        st.subheader("Detailed City Analysis")
        selected_ranked_city = st.selectbox(
            "Select City for Detailed Analysis",
            [city for city, _ in city_rankings],
            index=0
        )

        if selected_ranked_city:
            insights = get_affinity_insights(player_country, selected_ranked_city, annual_salary)
            scores = insights['scores']

            # Score breakdown
            st.markdown(f"### {selected_ranked_city} - Affinity Analysis")

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                score_color = "🟢" if scores['overall_score'] >= 60 else "🟡" if scores['overall_score'] >= 45 else "🔴"
                st.metric("Overall Score", f"{scores['overall_score']}/100 {score_color}")
            with metric_col2:
                st.metric("Adaptation Category", scores['adaptation_category'])
            with metric_col3:
                st.metric("Expected Timeline", scores['expected_timeline'])
            with metric_col4:
                city_info = CITY_DEMOGRAPHICS[selected_ranked_city]
                st.metric("Population", f"{city_info['population']:,}")

            # Component scores visualization
            component_df = pd.DataFrame({
                'Component': ['Demographic\nAffinity\n(50%)', 'Language\nProficiency\n(30%)', 'Tax\nBurden\n(20%)'],
                'Score': [scores['demographic_score'], scores['language_score'], scores['tax_score']],
                'Weight': [50, 30, 20]
            })

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    component_df,
                    x='Component',
                    y='Score',
                    title='Component Scores Breakdown',
                    color='Score',
                    color_continuous_scale='RdYlGn',
                    text='Score'
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig.update_layout(showlegend=False, yaxis_range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.pie(
                    component_df,
                    values='Weight',
                    names='Component',
                    title='Component Weights in Overall Score'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Strengths and challenges
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### ✅ Strengths")
                if insights['strengths']:
                    for strength in insights['strengths']:
                        st.success(strength)
                else:
                    st.info("No significant strengths identified")

            with col2:
                st.markdown("#### ⚠️ Challenges")
                if insights['challenges']:
                    for challenge in insights['challenges']:
                        st.warning(challenge)
                else:
                    st.success("No major challenges identified")

            # Recommendations
            if insights['recommendations']:
                st.markdown("#### 💡 Recommendations")
                for rec in insights['recommendations']:
                    st.info(f"• {rec}")

    else:  # Compare Players for a City mode
        st.subheader("Compare International Players for MLS City")

        col1, col2 = st.columns(2)

        with col1:
            city_for_comparison = st.selectbox(
                "Select MLS City",
                sorted(CITY_DEMOGRAPHICS.keys()),
                index=0
            )

        with col2:
            annual_salary_compare = st.number_input(
                "Annual Salary ($)",
                min_value=100000,
                max_value=10000000,
                value=500000,
                step=50000,
                key="salary_compare"
            )

        # Select multiple player countries
        selected_countries = st.multiselect(
            "Select Player Countries to Compare",
            sorted(PLAYER_ORIGINS.keys()),
            default=['Mexico', 'Argentina', 'Colombia', 'England', 'South Korea']
        )

        if selected_countries and city_for_comparison:
            st.divider()

            # Calculate scores for all selected players
            player_comparisons = compare_players_for_city(city_for_comparison, selected_countries, annual_salary_compare)

            # Create comparison dataframe
            comparison_data = []
            for country, scores in player_comparisons:
                player_info = PLAYER_ORIGINS[country]
                comparison_data.append({
                    'Country': country,
                    'Overall Score': scores['overall_score'],
                    'Demographic': scores['demographic_score'],
                    'Language': scores['language_score'],
                    'Tax': scores['tax_score'],
                    'Adaptation': scores['adaptation_category'],
                    'Timeline': scores['expected_timeline'],
                    'Primary Ethnicity': player_info['primary_ethnicity'],
                    'English Proficiency': f"{int(player_info['english_proficiency']*100)}%"
                })

            comparison_df = pd.DataFrame(comparison_data)

            st.markdown(f"### Player Comparison for {city_for_comparison}")

            # Grouped bar chart
            melted_df = comparison_df.melt(
                id_vars=['Country'],
                value_vars=['Demographic', 'Language', 'Tax'],
                var_name='Component',
                value_name='Score'
            )

            fig = px.bar(
                melted_df,
                x='Country',
                y='Score',
                color='Component',
                barmode='group',
                title=f'Component Score Comparison - {city_for_comparison}',
                labels={'Score': 'Score (0-100)'},
                color_discrete_map={'Demographic': '#FF6B6B', 'Language': '#4ECDC4', 'Tax': '#45B7D1'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Overall scores comparison
            fig = px.bar(
                comparison_df,
                x='Country',
                y='Overall Score',
                color='Overall Score',
                title=f'Overall Affinity Scores - {city_for_comparison}',
                labels={'Overall Score': 'Affinity Score (0-100)'},
                color_continuous_scale='Viridis',
                hover_data=['Adaptation', 'Timeline']
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Detailed comparison table
            st.markdown("#### Detailed Comparison")
            st.dataframe(
                comparison_df.style.background_gradient(
                    subset=['Overall Score', 'Demographic', 'Language', 'Tax'],
                    cmap='RdYlGn'
                ),
                use_container_width=True,
                hide_index=True
            )

            # City demographic context
            st.divider()
            st.markdown(f"#### {city_for_comparison} Demographic Context")

            city_demo_info = CITY_DEMOGRAPHICS[city_for_comparison]
            demo_context_col1, demo_context_col2, demo_context_col3, demo_context_col4 = st.columns(4)

            with demo_context_col1:
                st.metric("Ethnic Majority", city_demo_info['majority'])
            with demo_context_col2:
                st.metric("Diversity Index", f"{get_diversity_index(city_for_comparison):.3f}")
            with demo_context_col3:
                st.metric("Hispanic %", f"{city_demo_info['demographics']['Hispanic']:.1f}%")
            with demo_context_col4:
                state_tax = STATE_TAX_INFO[city_demo_info['state']]['top_rate']
                st.metric("State Top Tax Rate", f"{state_tax}%")

# Footer
st.divider()
st.markdown("---")
st.markdown("Player Affinity Dashboard | Built with Streamlit")
