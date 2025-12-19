"""
MLS City Demographics Data from 2020 Census
Race and ethnicity breakdown for all cities with MLS teams
"""

# Complete MLS City Demographics (2020 Census Data)
# Categories: White, Black, Asian, Hispanic, Native/Other, Multiracial
CITY_DEMOGRAPHICS = {
    # California
    'Los Angeles': {
        'state': 'California',
        'team': 'Los Angeles FC',
        'demographics': {
            'White': 28.3,
            'Black': 8.6,
            'Asian': 11.8,
            'Hispanic': 47.2,
            'Native/Other': 0.5,
            'Multiracial': 3.6
        },
        'majority': 'Hispanic',
        'population': 3898747
    },
    'Carson': {  # LA Galaxy
        'state': 'California',
        'team': 'LA Galaxy',
        'demographics': {
            'White': 28.3,  # Using LA area demographics
            'Black': 8.6,
            'Asian': 11.8,
            'Hispanic': 47.2,
            'Native/Other': 0.5,
            'Multiracial': 3.6
        },
        'majority': 'Hispanic',
        'population': 3898747
    },
    'San Jose': {
        'state': 'California',
        'team': 'San Jose Earthquakes',
        'demographics': {
            'White': 23.3,
            'Black': 2.7,
            'Asian': 38.2,
            'Hispanic': 31.2,
            'Native/Other': 1.0,
            'Multiracial': 3.6
        },
        'majority': 'Asian',
        'population': 1013240
    },
    'San Diego': {
        'state': 'California',
        'team': 'San Diego FC',
        'demographics': {
            'White': 40.7,
            'Black': 5.6,
            'Asian': 17.6,
            'Hispanic': 29.7,
            'Native/Other': 1.2,
            'Multiracial': 5.3
        },
        'majority': 'White',
        'population': 1386932
    },

    # Colorado
    'Denver': {
        'state': 'Colorado',
        'team': 'Colorado Rapids',
        'demographics': {
            'White': 54.3,
            'Black': 8.5,
            'Asian': 3.8,
            'Hispanic': 27.9,
            'Native/Other': 1.2,
            'Multiracial': 4.2
        },
        'majority': 'White',
        'population': 715522
    },

    # Florida
    'Miami': {
        'state': 'Florida',
        'team': 'Inter Miami CF',
        'demographics': {
            'White': 14.0,
            'Black': 11.9,
            'Asian': 1.3,
            'Hispanic': 70.2,
            'Native/Other': 0.6,
            'Multiracial': 2.0
        },
        'majority': 'Hispanic',
        'population': 442241
    },
    'Orlando': {
        'state': 'Florida',
        'team': 'Orlando City SC',
        'demographics': {
            'White': 33.5,
            'Black': 22.8,
            'Asian': 4.2,
            'Hispanic': 32.9,
            'Native/Other': 1.5,
            'Multiracial': 5.1
        },
        'majority': 'White',
        'population': 307573
    },

    # Georgia
    'Atlanta': {
        'state': 'Georgia',
        'team': 'Atlanta United',
        'demographics': {
            'White': 38.5,
            'Black': 46.7,
            'Asian': 4.5,
            'Hispanic': 6.0,
            'Native/Other': 0.7,
            'Multiracial': 3.6
        },
        'majority': 'Black',
        'population': 498715
    },

    # Illinois
    'Chicago': {
        'state': 'Illinois',
        'team': 'Chicago Fire FC',
        'demographics': {
            'White': 35.9,
            'Black': 29.2,
            'Asian': 7.0,
            'Hispanic': 29.8,
            'Native/Other': 0.1,
            'Multiracial': 10.8
        },
        'majority': 'White',
        'population': 2746388
    },

    # Kansas
    'Kansas City': {
        'state': 'Kansas',
        'team': 'Sporting Kansas City',
        'demographics': {
            'White': 52.8,
            'Black': 25.8,
            'Asian': 3.1,
            'Hispanic': 12.0,
            'Native/Other': 1.1,
            'Multiracial': 5.2
        },
        'majority': 'White',
        'population': 508090
    },

    # Massachusetts
    'Boston': {  # New England Revolution
        'state': 'Massachusetts',
        'team': 'New England Revolution',
        'demographics': {
            'White': 44.6,
            'Black': 19.7,
            'Asian': 10.2,
            'Hispanic': 19.5,
            'Native/Other': 0.6,
            'Multiracial': 5.4
        },
        'majority': 'White',
        'population': 675647
    },

    # Minnesota
    'St. Paul': {  # Minnesota United FC
        'state': 'Minnesota',
        'team': 'Minnesota United FC',
        'demographics': {
            'White': 48.8,
            'Black': 16.5,
            'Asian': 19.2,
            'Hispanic': 9.7,
            'Native/Other': 1.2,
            'Multiracial': 4.7
        },
        'majority': 'White',
        'population': 311527
    },

    # Missouri
    'St. Louis': {
        'state': 'Missouri',
        'team': 'St. Louis City SC',
        'demographics': {
            'White': 42.9,
            'Black': 42.8,
            'Asian': 4.0,
            'Hispanic': 5.1,
            'Native/Other': 0.8,
            'Multiracial': 4.4
        },
        'majority': 'White',
        'population': 301578
    },

    # New Jersey
    'Harrison': {  # New York Red Bulls
        'state': 'New Jersey',
        'team': 'New York Red Bulls',
        'demographics': {
            'White': 36.0,
            'Black': 14.0,
            'Asian': 12.0,
            'Hispanic': 35.0,
            'Native/Other': 0.5,
            'Multiracial': 2.5
        },
        'majority': 'White',
        'population': 19450
    },

    # New York
    'New York': {
        'state': 'New York',
        'team': 'New York City FC',
        'demographics': {
            'White': 30.9,
            'Black': 20.2,
            'Asian': 15.6,
            'Hispanic': 28.3,
            'Native/Other': 0.2,
            'Multiracial': 4.8
        },
        'majority': 'White',
        'population': 8804190
    },

    # North Carolina
    'Charlotte': {
        'state': 'North Carolina',
        'team': 'Charlotte FC',
        'demographics': {
            'White': 39.7,
            'Black': 32.5,
            'Asian': 7.0,
            'Hispanic': 16.3,
            'Native/Other': 0.3,
            'Multiracial': 4.2
        },
        'majority': 'White',
        'population': 874579
    },

    # Ohio
    'Columbus': {
        'state': 'Ohio',
        'team': 'Columbus Crew SC',
        'demographics': {
            'White': 52.0,
            'Black': 28.3,
            'Asian': 6.2,
            'Hispanic': 7.7,
            'Native/Other': 0.8,
            'Multiracial': 5.0
        },
        'majority': 'White',
        'population': 905748
    },
    'Cincinnati': {
        'state': 'Ohio',
        'team': 'FC Cincinnati',
        'demographics': {
            'White': 46.9,
            'Black': 40.3,
            'Asian': 2.5,
            'Hispanic': 5.1,
            'Native/Other': 0.7,
            'Multiracial': 4.4
        },
        'majority': 'White',
        'population': 309317
    },

    # Oregon
    'Portland': {
        'state': 'Oregon',
        'team': 'Portland Timbers',
        'demographics': {
            'White': 66.4,
            'Black': 5.7,
            'Asian': 8.0,
            'Hispanic': 11.1,
            'Native/Other': 1.9,
            'Multiracial': 7.0
        },
        'majority': 'White',
        'population': 652503
    },

    # Pennsylvania
    'Philadelphia': {
        'state': 'Pennsylvania',
        'team': 'Philadelphia Union',
        'demographics': {
            'White': 36.3,
            'Black': 39.3,
            'Asian': 8.7,
            'Hispanic': 14.9,
            'Native/Other': 0.4,
            'Multiracial': 6.9
        },
        'majority': 'Black',
        'population': 1603797
    },

    # Tennessee
    'Nashville': {
        'state': 'Tennessee',
        'team': 'Nashville SC',
        'demographics': {
            'White': 53.3,
            'Black': 24.3,
            'Asian': 3.9,
            'Hispanic': 14.0,
            'Native/Other': 0.7,
            'Multiracial': 3.8
        },
        'majority': 'White',
        'population': 689447
    },

    # Texas
    'Austin': {
        'state': 'Texas',
        'team': 'Austin FC',
        'demographics': {
            'White': 47.1,
            'Black': 6.9,
            'Asian': 8.9,
            'Hispanic': 32.5,
            'Native/Other': 0.8,
            'Multiracial': 3.9
        },
        'majority': 'White',
        'population': 961855
    },
    'Houston': {
        'state': 'Texas',
        'team': 'Houston Dynamo',
        'demographics': {
            'White': 23.6,
            'Black': 22.5,
            'Asian': 7.0,
            'Hispanic': 44.1,
            'Native/Other': 0.8,
            'Multiracial': 2.0
        },
        'majority': 'Hispanic',
        'population': 2304580
    },
    'Frisco': {  # FC Dallas
        'state': 'Texas',
        'team': 'FC Dallas',
        'demographics': {
            'White': 28.2,
            'Black': 23.4,
            'Asian': 6.5,
            'Hispanic': 41.9,
            'Native/Other': 0.9,
            'Multiracial': 2.1
        },
        'majority': 'Hispanic',
        'population': 1304379
    },

    # Utah
    'Salt Lake City': {
        'state': 'Utah',
        'team': 'Real Salt Lake',
        'demographics': {
            'White': 63.4,
            'Black': 2.7,
            'Asian': 5.4,
            'Hispanic': 20.8,
            'Native/Other': 3.4,
            'Multiracial': 4.2
        },
        'majority': 'White',
        'population': 199723
    },

    # Washington
    'Seattle': {
        'state': 'Washington',
        'team': 'Seattle Sounders FC',
        'demographics': {
            'White': 59.5,
            'Black': 6.8,
            'Asian': 16.9,
            'Hispanic': 8.2,
            'Native/Other': 1.3,
            'Multiracial': 7.3
        },
        'majority': 'White',
        'population': 737015
    },

    # Washington D.C.
    'Washington': {
        'state': 'District of Columbia',
        'team': 'D.C. United',
        'demographics': {
            'White': 38.0,
            'Black': 41.4,
            'Asian': 4.8,
            'Hispanic': 11.3,
            'Native/Other': 0.6,
            'Multiracial': 3.9
        },
        'majority': 'Black',
        'population': 689545
    }
}

def get_diversity_index(city):
    """
    Calculate diversity index for a city using Simpson's Diversity Index
    Higher value = more diverse

    Args:
        city: City name

    Returns:
        Diversity index (0-1 scale, higher is more diverse)
    """
    if city not in CITY_DEMOGRAPHICS:
        return 0

    demographics = CITY_DEMOGRAPHICS[city]['demographics']

    # Simpson's Diversity Index: 1 - sum(proportion^2)
    sum_squares = sum((pct/100)**2 for pct in demographics.values())
    diversity_index = 1 - sum_squares

    return round(diversity_index, 3)

def get_minority_percentage(city):
    """
    Calculate total minority percentage (100 - White percentage)

    Args:
        city: City name

    Returns:
        Minority percentage
    """
    if city not in CITY_DEMOGRAPHICS:
        return 0

    white_pct = CITY_DEMOGRAPHICS[city]['demographics']['White']
    return round(100 - white_pct, 2)

def get_cities_by_majority():
    """
    Group cities by their ethnic majority

    Returns:
        Dictionary grouped by majority ethnicity
    """
    grouped = {}
    for city, data in CITY_DEMOGRAPHICS.items():
        majority = data['majority']
        if majority not in grouped:
            grouped[majority] = []
        grouped[majority].append(city)

    return grouped

def get_most_diverse_cities(n=10):
    """
    Get the n most diverse MLS cities

    Args:
        n: Number of cities to return

    Returns:
        List of tuples (city, diversity_index)
    """
    diversity_scores = [
        (city, get_diversity_index(city))
        for city in CITY_DEMOGRAPHICS.keys()
    ]

    return sorted(diversity_scores, key=lambda x: x[1], reverse=True)[:n]

def get_demographic_summary():
    """
    Get summary statistics across all MLS cities

    Returns:
        Dictionary with summary stats
    """
    all_cities = list(CITY_DEMOGRAPHICS.keys())

    # Calculate averages across all cities
    avg_demographics = {
        'White': 0,
        'Black': 0,
        'Asian': 0,
        'Hispanic': 0,
        'Native/Other': 0,
        'Multiracial': 0
    }

    for city_data in CITY_DEMOGRAPHICS.values():
        for ethnicity, pct in city_data['demographics'].items():
            avg_demographics[ethnicity] += pct

    # Average by number of cities
    n_cities = len(CITY_DEMOGRAPHICS)
    for ethnicity in avg_demographics:
        avg_demographics[ethnicity] = round(avg_demographics[ethnicity] / n_cities, 2)

    # Get majority breakdown
    majority_counts = {}
    for city_data in CITY_DEMOGRAPHICS.values():
        majority = city_data['majority']
        majority_counts[majority] = majority_counts.get(majority, 0) + 1

    return {
        'total_cities': n_cities,
        'average_demographics': avg_demographics,
        'majority_breakdown': majority_counts,
        'most_diverse': get_most_diverse_cities(5)
    }
