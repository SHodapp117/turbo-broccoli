"""
Player Affinity Score System for MLS Cities

Combines demographic/cultural affinity with tax burden to calculate
how well international players from different countries might adapt
to each MLS city.

Based on peer-reviewed research:
- Cultural distance impacts adaptation (Hofstede dimensions)
- Demographic affinity correlates with social support networks
- Tax burden affects financial satisfaction
- Language proficiency affects performance (15% improvement with English)
"""

import math
from city_demographics import CITY_DEMOGRAPHICS
from detailed_demographics import DETAILED_CITY_DEMOGRAPHICS
from state_tax_data import STATE_TAX_INFO, get_effective_tax_rate

# Player origin countries commonly seen in MLS
PLAYER_ORIGINS = {
    'Mexico': {
        'primary_ethnicity': 'Hispanic',
        'detailed_group': 'Mexican',
        'language': 'Spanish',
        'english_proficiency': 0.3,  # 0-1 scale, average
    },
    'Argentina': {
        'primary_ethnicity': 'Hispanic',
        'detailed_group': 'Argentinean',
        'language': 'Spanish',
        'english_proficiency': 0.4,
    },
    'Colombia': {
        'primary_ethnicity': 'Hispanic',
        'detailed_group': 'Colombian',
        'language': 'Spanish',
        'english_proficiency': 0.35,
    },
    'Brazil': {
        'primary_ethnicity': 'Hispanic',
        'detailed_group': 'Other South American',
        'language': 'Portuguese',
        'english_proficiency': 0.4,
    },
    'Venezuela': {
        'primary_ethnicity': 'Hispanic',
        'detailed_group': 'Venezuelan',
        'language': 'Spanish',
        'english_proficiency': 0.35,
    },
    'Ecuador': {
        'primary_ethnicity': 'Hispanic',
        'detailed_group': 'Ecuadorian',
        'language': 'Spanish',
        'english_proficiency': 0.3,
    },
    'Uruguay': {
        'primary_ethnicity': 'Hispanic',
        'detailed_group': 'Uruguayan',
        'language': 'Spanish',
        'english_proficiency': 0.4,
    },
    'Jamaica': {
        'primary_ethnicity': 'Black',
        'detailed_group': 'Jamaican',
        'language': 'English',
        'english_proficiency': 1.0,  # Native English speakers
    },
    'Haiti': {
        'primary_ethnicity': 'Black',
        'detailed_group': 'Haitian',
        'language': 'French/Creole',
        'english_proficiency': 0.25,
    },
    'Nigeria': {
        'primary_ethnicity': 'Black',
        'detailed_group': 'Nigerian',
        'language': 'English',
        'english_proficiency': 0.9,  # English is official language
    },
    'Ghana': {
        'primary_ethnicity': 'Black',
        'detailed_group': 'Ghanaian',
        'language': 'English',
        'english_proficiency': 0.9,
    },
    'Senegal': {
        'primary_ethnicity': 'Black',
        'detailed_group': 'Other African',
        'language': 'French',
        'english_proficiency': 0.3,
    },
    'South Korea': {
        'primary_ethnicity': 'Asian',
        'detailed_group': 'Korean',
        'language': 'Korean',
        'english_proficiency': 0.5,
    },
    'Japan': {
        'primary_ethnicity': 'Asian',
        'detailed_group': 'Japanese',
        'language': 'Japanese',
        'english_proficiency': 0.45,
    },
    'China': {
        'primary_ethnicity': 'Asian',
        'detailed_group': 'Chinese',
        'language': 'Mandarin',
        'english_proficiency': 0.4,
    },
    'Vietnam': {
        'primary_ethnicity': 'Asian',
        'detailed_group': 'Vietnamese',
        'language': 'Vietnamese',
        'english_proficiency': 0.35,
    },
    'Philippines': {
        'primary_ethnicity': 'Asian',
        'detailed_group': 'Filipino',
        'language': 'Tagalog/English',
        'english_proficiency': 0.85,
    },
    'India': {
        'primary_ethnicity': 'Asian',
        'detailed_group': 'Asian Indian',
        'language': 'Hindi/English',
        'english_proficiency': 0.75,
    },
    'England': {
        'primary_ethnicity': 'White',
        'detailed_group': 'English',
        'language': 'English',
        'english_proficiency': 1.0,
    },
    'Ireland': {
        'primary_ethnicity': 'White',
        'detailed_group': 'Irish',
        'language': 'English',
        'english_proficiency': 1.0,
    },
    'Germany': {
        'primary_ethnicity': 'White',
        'detailed_group': 'German',
        'language': 'German',
        'english_proficiency': 0.65,
    },
    'Italy': {
        'primary_ethnicity': 'White',
        'detailed_group': 'Italian',
        'language': 'Italian',
        'english_proficiency': 0.5,
    },
    'France': {
        'primary_ethnicity': 'White',
        'detailed_group': 'French',
        'language': 'French',
        'english_proficiency': 0.55,
    },
    'Spain': {
        'primary_ethnicity': 'White',
        'detailed_group': 'Other European',
        'language': 'Spanish',
        'english_proficiency': 0.5,
    },
    'Portugal': {
        'primary_ethnicity': 'White',
        'detailed_group': 'Portuguese',
        'language': 'Portuguese',
        'english_proficiency': 0.5,
    },
    'Poland': {
        'primary_ethnicity': 'White',
        'detailed_group': 'Polish',
        'language': 'Polish',
        'english_proficiency': 0.6,
    },
    'Russia': {
        'primary_ethnicity': 'White',
        'detailed_group': 'Russian',
        'language': 'Russian',
        'english_proficiency': 0.45,
    },
}

def calculate_demographic_affinity(player_country, city):
    """
    Calculate demographic affinity score (0-100)

    Based on research showing social support networks correlate with adaptation success

    Args:
        player_country: Country of origin
        city: MLS city name

    Returns:
        Demographic affinity score (0-100, higher is better)
    """
    if player_country not in PLAYER_ORIGINS:
        return 50  # Neutral score for unknown countries

    if city not in CITY_DEMOGRAPHICS:
        return 50

    player_info = PLAYER_ORIGINS[player_country]
    city_demo = CITY_DEMOGRAPHICS[city]['demographics']

    # Base score from primary ethnicity percentage in city
    primary_ethnicity = player_info['primary_ethnicity']
    base_score = city_demo.get(primary_ethnicity, 0) * 2  # Scale to 0-100

    # Bonus for detailed demographic match (if available)
    detailed_bonus = 0
    if city in DETAILED_CITY_DEMOGRAPHICS:
        detailed_demo = DETAILED_CITY_DEMOGRAPHICS[city]
        player_group = player_info['detailed_group']

        # Check each detailed category
        for category in ['Asian_Detailed', 'Hispanic_Detailed', 'White_Detailed', 'Black_Detailed']:
            if category in detailed_demo and player_group in detailed_demo[category]:
                # Strong match - specific community present
                detailed_bonus = detailed_demo[category][player_group] * 3  # Higher weight
                break

    # Combine base and detailed scores
    affinity_score = min(100, base_score + detailed_bonus)

    return round(affinity_score, 2)

def calculate_language_adaptation_score(player_country):
    """
    Calculate language adaptation score based on English proficiency

    Research shows 15% performance improvement with advanced English proficiency

    Args:
        player_country: Country of origin

    Returns:
        Language score (0-100, higher is better)
    """
    if player_country not in PLAYER_ORIGINS:
        return 50

    english_proficiency = PLAYER_ORIGINS[player_country]['english_proficiency']

    # Convert to 0-100 scale
    # Native speakers (1.0) = 100
    # No English (0.0) = 30 (baseline - can still adapt but harder)
    score = 30 + (english_proficiency * 70)

    return round(score, 2)

def calculate_tax_burden_score(city, annual_salary=500000):
    """
    Calculate tax favorability score

    Lower tax burden = higher score

    Args:
        city: MLS city name
        annual_salary: Player's annual salary (default $500k - MLS median)

    Returns:
        Tax score (0-100, higher is better)
    """
    if city not in CITY_DEMOGRAPHICS:
        return 50

    state = CITY_DEMOGRAPHICS[city]['state']

    if state not in STATE_TAX_INFO:
        return 50

    # Calculate effective tax rate
    effective_rate = get_effective_tax_rate(state, annual_salary, 'single')

    # Convert to score (0% tax = 100, 13.3% tax = 0)
    # Linear scale based on MLS state range (0% to ~13%)
    max_rate = 13.3
    score = 100 - ((effective_rate / max_rate) * 100)
    score = max(0, min(100, score))  # Clamp to 0-100

    return round(score, 2)

def calculate_overall_affinity_score(player_country, city, annual_salary=500000, weights=None):
    """
    Calculate overall Player Affinity Score

    Combines demographic affinity, language adaptation, and tax burden

    Args:
        player_country: Country of origin
        city: MLS city name
        annual_salary: Player's annual salary
        weights: Dictionary with 'demographic', 'language', 'tax' weights (default: 0.5, 0.3, 0.2)

    Returns:
        Dictionary with overall score and component scores
    """
    if weights is None:
        weights = {
            'demographic': 0.5,  # Most important per research
            'language': 0.3,     # 15% performance impact per research
            'tax': 0.2          # Financial satisfaction factor
        }

    # Calculate component scores
    demo_score = calculate_demographic_affinity(player_country, city)
    lang_score = calculate_language_adaptation_score(player_country)
    tax_score = calculate_tax_burden_score(city, annual_salary)

    # Calculate weighted overall score
    overall_score = (
        (demo_score * weights['demographic']) +
        (lang_score * weights['language']) +
        (tax_score * weights['tax'])
    )

    # Determine adaptation likelihood category
    if overall_score >= 75:
        adaptation_category = 'Excellent'
        expected_timeline = '3-6 months'
    elif overall_score >= 60:
        adaptation_category = 'Good'
        expected_timeline = '6-9 months'
    elif overall_score >= 45:
        adaptation_category = 'Moderate'
        expected_timeline = '9-12 months'
    else:
        adaptation_category = 'Challenging'
        expected_timeline = '12+ months'

    return {
        'overall_score': round(overall_score, 2),
        'demographic_score': demo_score,
        'language_score': lang_score,
        'tax_score': tax_score,
        'adaptation_category': adaptation_category,
        'expected_timeline': expected_timeline,
        'components': {
            'demographic_weight': weights['demographic'],
            'language_weight': weights['language'],
            'tax_weight': weights['tax']
        }
    }

def rank_cities_for_player(player_country, annual_salary=500000):
    """
    Rank all MLS cities by affinity score for a player

    Args:
        player_country: Country of origin
        annual_salary: Player's annual salary

    Returns:
        List of tuples (city, score_dict) sorted by overall score
    """
    city_scores = []

    for city in CITY_DEMOGRAPHICS.keys():
        score_dict = calculate_overall_affinity_score(player_country, city, annual_salary)
        city_scores.append((city, score_dict))

    # Sort by overall score descending
    city_scores.sort(key=lambda x: x[1]['overall_score'], reverse=True)

    return city_scores

def compare_players_for_city(city, player_countries, annual_salary=500000):
    """
    Compare affinity scores for multiple players in one city

    Args:
        city: MLS city name
        player_countries: List of player countries
        annual_salary: Player's annual salary

    Returns:
        List of tuples (country, score_dict) sorted by overall score
    """
    player_scores = []

    for country in player_countries:
        score_dict = calculate_overall_affinity_score(country, city, annual_salary)
        player_scores.append((country, score_dict))

    # Sort by overall score descending
    player_scores.sort(key=lambda x: x[1]['overall_score'], reverse=True)

    return player_scores

def get_affinity_insights(player_country, city, annual_salary=500000):
    """
    Get detailed insights and recommendations

    Args:
        player_country: Country of origin
        city: MLS city name
        annual_salary: Player's annual salary

    Returns:
        Dictionary with insights and recommendations
    """
    scores = calculate_overall_affinity_score(player_country, city, annual_salary)

    insights = {
        'scores': scores,
        'strengths': [],
        'challenges': [],
        'recommendations': []
    }

    # Analyze strengths
    if scores['demographic_score'] >= 60:
        insights['strengths'].append(f"Strong cultural community support (score: {scores['demographic_score']})")
    if scores['language_score'] >= 70:
        insights['strengths'].append(f"Good English proficiency advantage (score: {scores['language_score']})")
    if scores['tax_score'] >= 70:
        insights['strengths'].append(f"Favorable tax environment (score: {scores['tax_score']})")

    # Analyze challenges
    if scores['demographic_score'] < 40:
        insights['challenges'].append(f"Limited cultural community (score: {scores['demographic_score']})")
        insights['recommendations'].append("Prioritize building cross-cultural relationships")
    if scores['language_score'] < 50:
        insights['challenges'].append(f"Language barrier may impact adaptation (score: {scores['language_score']})")
        insights['recommendations'].append("Invest in intensive English language training")
    if scores['tax_score'] < 50:
        insights['challenges'].append(f"Higher tax burden (score: {scores['tax_score']})")
        insights['recommendations'].append("Work with financial advisor on tax optimization")

    # General recommendations based on adaptation category
    if scores['adaptation_category'] == 'Challenging':
        insights['recommendations'].append("Consider extended pre-season integration period")
        insights['recommendations'].append("Assign cultural mentor from same background if possible")
    elif scores['adaptation_category'] == 'Moderate':
        insights['recommendations'].append("Establish support network early")
        insights['recommendations'].append("Regular check-ins during first 6 months")

    return insights

# Research-based scoring weights documentation
SCORING_METHODOLOGY = """
Player Affinity Score Methodology

Based on peer-reviewed research:

1. Demographic Affinity (50% weight):
   - Presence of ethnic/cultural community in city
   - Detailed ancestry match when available
   - Research basis: Social support networks correlate with adaptation success

2. Language Proficiency (30% weight):
   - English proficiency of player's origin country
   - Research basis: 15% performance improvement with advanced English

3. Tax Burden (20% weight):
   - State effective tax rate on player salary
   - Research basis: Financial satisfaction affects overall well-being

Score Interpretation:
- 75-100: Excellent adaptation likelihood (3-6 months)
- 60-74: Good adaptation likelihood (6-9 months)
- 45-59: Moderate adaptation likelihood (9-12 months)
- 0-44: Challenging adaptation (12+ months)

Sources:
- Cultural Distance: 34,430 transfers analyzed (Springer, 2023)
- Language Impact: Elite athlete study (15% performance correlation)
- Adaptation Timeline: Meta-analysis of international student-athletes
- SCAS reliability: α = 0.75-0.91 across studies
"""
