"""
Detailed Demographic Data for MLS Cities
Granular breakdown by ancestry and origin from 2020 Census and related data sources

This file provides detailed ancestry/origin information for:
- Asian populations (Chinese, Indian, Filipino, Vietnamese, Korean, Japanese, etc.)
- Hispanic/Latino populations (Mexican, Puerto Rican, Cuban, Dominican, Colombian, etc.)
- White/European ancestries (German, Irish, Italian, Polish, English, etc.)
- Black/African ancestries (African American, Jamaican, Haitian, Nigerian, Ethiopian, etc.)
"""

# Detailed demographic data by city
# Note: Some data combines 2020 Census with American Community Survey estimates where detailed breakdowns aren't yet published
DETAILED_CITY_DEMOGRAPHICS = {
    'Los Angeles': {
        'Asian_Detailed': {
            'Chinese': 3.7,
            'Filipino': 2.9,
            'Vietnamese': 1.1,
            'Korean': 2.3,
            'Japanese': 0.8,
            'Asian Indian': 0.6,
            'Thai': 0.3,
            'Cambodian': 0.2,
            'Other Asian': 0.1
        },
        'Hispanic_Detailed': {
            'Mexican': 32.1,
            'Salvadoran': 3.8,
            'Guatemalan': 2.6,
            'Puerto Rican': 1.0,
            'Cuban': 0.5,
            'Colombian': 0.8,
            'Honduran': 1.0,
            'Nicaraguan': 0.3,
            'Other Central American': 1.5,
            'Other South American': 1.2,
            'Other Hispanic': 2.4
        },
        'White_Detailed': {
            'German': 4.2,
            'Irish': 3.8,
            'English': 3.5,
            'Italian': 2.1,
            'Armenian': 2.0,
            'Russian': 1.5,
            'Polish': 0.8,
            'French': 0.7,
            'Other European': 5.7
        },
        'Black_Detailed': {
            'African American': 7.2,
            'Jamaican': 0.4,
            'Haitian': 0.2,
            'Nigerian': 0.2,
            'Ethiopian': 0.2,
            'Other African': 0.4
        }
    },

    'San Jose': {
        'Asian_Detailed': {
            'Vietnamese': 10.4,
            'Chinese': 6.7,
            'Filipino': 5.6,
            'Asian Indian': 4.6,
            'Korean': 1.5,
            'Japanese': 1.3,
            'Cambodian': 0.3,
            'Thai': 0.4,
            'Other Asian': 7.4
        },
        'Hispanic_Detailed': {
            'Mexican': 22.8,
            'Puerto Rican': 0.9,
            'Cuban': 0.3,
            'Salvadoran': 1.2,
            'Guatemalan': 0.6,
            'Colombian': 0.3,
            'Other Central American': 2.0,
            'Other South American': 1.1,
            'Other Hispanic': 2.0
        },
        'White_Detailed': {
            'German': 3.5,
            'Irish': 3.2,
            'English': 2.8,
            'Italian': 2.5,
            'Portuguese': 1.6,
            'French': 0.9,
            'Polish': 0.6,
            'Other European': 8.2
        },
        'Black_Detailed': {
            'African American': 2.1,
            'Nigerian': 0.2,
            'Ethiopian': 0.1,
            'Other African': 0.3
        }
    },

    'San Diego': {
        'Asian_Detailed': {
            'Filipino': 7.3,
            'Chinese': 3.4,
            'Vietnamese': 2.6,
            'Korean': 1.5,
            'Japanese': 1.2,
            'Asian Indian': 1.0,
            'Thai': 0.3,
            'Other Asian': 0.3
        },
        'Hispanic_Detailed': {
            'Mexican': 23.6,
            'Puerto Rican': 1.2,
            'Cuban': 0.5,
            'Salvadoran': 0.8,
            'Guatemalan': 0.5,
            'Colombian': 0.4,
            'Other Central American': 1.0,
            'Other South American': 0.7,
            'Other Hispanic': 1.0
        },
        'White_Detailed': {
            'German': 8.5,
            'Irish': 7.6,
            'English': 6.9,
            'Italian': 4.2,
            'French': 1.8,
            'Polish': 1.5,
            'Norwegian': 1.1,
            'Other European': 9.1
        },
        'Black_Detailed': {
            'African American': 4.8,
            'Jamaican': 0.3,
            'Nigerian': 0.2,
            'Ethiopian': 0.1,
            'Other African': 0.2
        }
    },

    'Miami': {
        'Asian_Detailed': {
            'Chinese': 0.4,
            'Asian Indian': 0.3,
            'Filipino': 0.2,
            'Vietnamese': 0.1,
            'Other Asian': 0.3
        },
        'Hispanic_Detailed': {
            'Cuban': 34.4,
            'Nicaraguan': 5.8,
            'Colombian': 6.2,
            'Venezuelan': 4.3,
            'Honduran': 3.5,
            'Puerto Rican': 2.9,
            'Mexican': 2.1,
            'Peruvian': 1.8,
            'Argentinean': 1.5,
            'Dominican': 1.2,
            'Guatemalan': 1.0,
            'Salvadoran': 0.8,
            'Chilean': 0.9,
            'Uruguayan': 0.5,
            'Other South American': 2.3,
            'Other Hispanic': 0.8
        },
        'White_Detailed': {
            'German': 2.1,
            'Irish': 1.8,
            'English': 1.5,
            'Italian': 1.9,
            'Polish': 0.6,
            'Other European': 5.1
        },
        'Black_Detailed': {
            'African American': 6.8,
            'Haitian': 3.7,
            'Jamaican': 0.9,
            'Trinidadian': 0.2,
            'Bahamian': 0.1,
            'Other Caribbean': 0.2
        }
    },

    'New York': {
        'Asian_Detailed': {
            'Chinese': 6.8,
            'Asian Indian': 3.1,
            'Korean': 1.4,
            'Filipino': 1.1,
            'Bangladeshi': 0.9,
            'Pakistani': 0.7,
            'Japanese': 0.4,
            'Vietnamese': 0.3,
            'Other Asian': 0.9
        },
        'Hispanic_Detailed': {
            'Puerto Rican': 8.3,
            'Dominican': 8.7,
            'Mexican': 4.9,
            'Ecuadorian': 2.1,
            'Colombian': 1.5,
            'Salvadoran': 0.6,
            'Guatemalan': 0.5,
            'Honduran': 0.4,
            'Peruvian': 0.3,
            'Other Central American': 0.4,
            'Other South American': 0.4,
            'Other Hispanic': 0.2
        },
        'White_Detailed': {
            'Italian': 7.8,
            'Irish': 5.4,
            'German': 4.2,
            'Polish': 2.8,
            'Russian': 2.4,
            'English': 1.9,
            'Greek': 0.9,
            'Ukrainian': 0.7,
            'Other European': 3.8
        },
        'Black_Detailed': {
            'African American': 13.2,
            'Jamaican': 2.6,
            'Haitian': 1.4,
            'Trinidadian': 0.7,
            'Ghanaian': 0.5,
            'Nigerian': 0.6,
            'West Indian': 0.5,
            'Other Caribbean': 0.4,
            'Other African': 0.3
        }
    },

    'Chicago': {
        'Asian_Detailed': {
            'Chinese': 2.1,
            'Asian Indian': 2.4,
            'Filipino': 1.3,
            'Korean': 0.6,
            'Pakistani': 0.3,
            'Japanese': 0.2,
            'Vietnamese': 0.1,
            'Other Asian': 0.0
        },
        'Hispanic_Detailed': {
            'Mexican': 21.4,
            'Puerto Rican': 6.7,
            'Guatemalan': 0.7,
            'Ecuadorian': 0.3,
            'Colombian': 0.2,
            'Salvadoran': 0.2,
            'Other Central American': 0.2,
            'Other South American': 0.1,
            'Other Hispanic': 0.0
        },
        'White_Detailed': {
            'Polish': 5.1,
            'Irish': 4.9,
            'German': 4.7,
            'Italian': 3.9,
            'English': 1.8,
            'Swedish': 0.8,
            'Russian': 0.7,
            'Czech': 0.5,
            'Other European': 4.5
        },
        'Black_Detailed': {
            'African American': 27.1,
            'Nigerian': 0.8,
            'Jamaican': 0.4,
            'Ethiopian': 0.3,
            'Ghanaian': 0.2,
            'Other African': 0.4
        }
    },

    'Houston': {
        'Asian_Detailed': {
            'Asian Indian': 2.1,
            'Vietnamese': 1.8,
            'Chinese': 1.6,
            'Filipino': 0.8,
            'Pakistani': 0.4,
            'Korean': 0.2,
            'Other Asian': 0.1
        },
        'Hispanic_Detailed': {
            'Mexican': 30.8,
            'Salvadoran': 2.9,
            'Honduran': 2.1,
            'Guatemalan': 1.0,
            'Puerto Rican': 0.9,
            'Colombian': 0.8,
            'Cuban': 0.6,
            'Venezuelan': 0.5,
            'Nicaraguan': 0.3,
            'Other Central American': 1.4,
            'Other South American': 1.3,
            'Other Hispanic': 1.5
        },
        'White_Detailed': {
            'German': 5.8,
            'Irish': 4.2,
            'English': 3.9,
            'French': 1.5,
            'Italian': 1.2,
            'Polish': 0.8,
            'Other European': 6.2
        },
        'Black_Detailed': {
            'African American': 19.3,
            'Nigerian': 1.7,
            'Jamaican': 0.6,
            'Haitian': 0.3,
            'Ethiopian': 0.2,
            'Ghanaian': 0.2,
            'Other African': 0.2
        }
    },

    'Atlanta': {
        'Asian_Detailed': {
            'Asian Indian': 1.8,
            'Chinese': 1.0,
            'Korean': 0.8,
            'Vietnamese': 0.4,
            'Filipino': 0.2,
            'Other Asian': 0.3
        },
        'Hispanic_Detailed': {
            'Mexican': 3.2,
            'Puerto Rican': 0.8,
            'Colombian': 0.5,
            'Guatemalan': 0.4,
            'Salvadoran': 0.3,
            'Cuban': 0.2,
            'Other Central American': 0.3,
            'Other South American': 0.2,
            'Other Hispanic': 0.1
        },
        'White_Detailed': {
            'English': 7.2,
            'German': 6.8,
            'Irish': 6.5,
            'Italian': 2.1,
            'French': 1.2,
            'Polish': 0.6,
            'Other European': 14.1
        },
        'Black_Detailed': {
            'African American': 42.6,
            'Nigerian': 1.8,
            'Jamaican': 0.9,
            'Ethiopian': 0.5,
            'Ghanaian': 0.4,
            'Haitian': 0.2,
            'Other African': 0.3
        }
    },

    'Philadelphia': {
        'Asian_Detailed': {
            'Chinese': 3.4,
            'Asian Indian': 2.1,
            'Vietnamese': 1.5,
            'Korean': 1.2,
            'Filipino': 0.3,
            'Other Asian': 0.2
        },
        'Hispanic_Detailed': {
            'Puerto Rican': 8.9,
            'Dominican': 2.3,
            'Mexican': 1.9,
            'Colombian': 0.5,
            'Guatemalan': 0.4,
            'Salvadoran': 0.3,
            'Other Central American': 0.3,
            'Other South American': 0.2,
            'Other Hispanic': 0.1
        },
        'White_Detailed': {
            'Irish': 11.2,
            'Italian': 7.9,
            'German': 6.5,
            'Polish': 3.8,
            'English': 2.1,
            'Russian': 1.2,
            'Ukrainian': 0.6,
            'Other European': 3.0
        },
        'Black_Detailed': {
            'African American': 35.4,
            'Jamaican': 1.5,
            'Haitian': 0.8,
            'Nigerian': 0.6,
            'Liberian': 0.4,
            'Ethiopian': 0.3,
            'Other African': 0.3
        }
    },

    'Seattle': {
        'Asian_Detailed': {
            'Chinese': 5.8,
            'Filipino': 4.1,
            'Vietnamese': 2.6,
            'Korean': 1.4,
            'Japanese': 1.3,
            'Asian Indian': 1.2,
            'Thai': 0.3,
            'Other Asian': 0.2
        },
        'Hispanic_Detailed': {
            'Mexican': 5.6,
            'Puerto Rican': 0.6,
            'Cuban': 0.2,
            'Salvadoran': 0.4,
            'Guatemalan': 0.3,
            'Colombian': 0.2,
            'Other Central American': 0.4,
            'Other South American': 0.3,
            'Other Hispanic': 0.2
        },
        'White_Detailed': {
            'German': 12.8,
            'Irish': 10.2,
            'English': 9.5,
            'Norwegian': 5.3,
            'Swedish': 3.2,
            'Italian': 2.8,
            'Polish': 1.5,
            'French': 1.9,
            'Other European': 12.3
        },
        'Black_Detailed': {
            'African American': 5.2,
            'Ethiopian': 0.8,
            'Somali': 0.4,
            'Nigerian': 0.2,
            'Other African': 0.2
        }
    }
}

def get_detailed_demographics(city):
    """
    Get detailed ancestry/origin demographics for a city

    Args:
        city: City name

    Returns:
        Dictionary with detailed breakdowns by category
    """
    if city not in DETAILED_CITY_DEMOGRAPHICS:
        return None

    return DETAILED_CITY_DEMOGRAPHICS[city]

def get_top_ancestries(city, category, n=5):
    """
    Get top N ancestries for a specific category

    Args:
        city: City name
        category: 'Asian_Detailed', 'Hispanic_Detailed', 'White_Detailed', or 'Black_Detailed'
        n: Number of top groups to return

    Returns:
        List of tuples (ancestry, percentage)
    """
    if city not in DETAILED_CITY_DEMOGRAPHICS:
        return []

    if category not in DETAILED_CITY_DEMOGRAPHICS[city]:
        return []

    data = DETAILED_CITY_DEMOGRAPHICS[city][category]
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    return sorted_data[:n]

def compare_ancestry_across_cities(ancestry_name, category):
    """
    Compare a specific ancestry across all cities

    Args:
        ancestry_name: Name of the ancestry (e.g., 'Mexican', 'Chinese', 'Irish')
        category: Category to search in

    Returns:
        Dictionary of city: percentage
    """
    results = {}

    for city, data in DETAILED_CITY_DEMOGRAPHICS.items():
        if category in data and ancestry_name in data[category]:
            results[city] = data[category][ancestry_name]

    return sorted(results.items(), key=lambda x: x[1], reverse=True)

def get_diversity_by_category(city, category):
    """
    Calculate Simpson's Diversity Index for a specific ethnic category

    Args:
        city: City name
        category: Category to analyze

    Returns:
        Diversity index (0-1 scale)
    """
    if city not in DETAILED_CITY_DEMOGRAPHICS:
        return 0

    if category not in DETAILED_CITY_DEMOGRAPHICS[city]:
        return 0

    data = DETAILED_CITY_DEMOGRAPHICS[city][category]

    # Simpson's Diversity Index
    sum_squares = sum((pct/100)**2 for pct in data.values())
    diversity_index = 1 - sum_squares

    return round(diversity_index, 3)

# Data source notes
DATA_SOURCES = """
Data Sources:
- 2020 U.S. Census Detailed DHC-A File (Released September 2023)
- American Community Survey 5-Year Estimates (2018-2022)
- Census Bureau Detailed Race and Ethnicity Groups Data

References:
- Census Bureau: "Census Bureau Releases 2020 Census Data for Nearly 1,500 Detailed Race and Ethnicity Groups"
- Asian populations: "Asian Indian Was The Largest Asian Alone Population Group in 2020"
- Hispanic populations: "Eight Hispanic Groups Each Had a Million or More Population in 2020"
- European ancestry: "Over Half of White Population Reported Being English, German or Irish"
- African ancestry: "New Population Counts for 62 Detailed Black or African American Groups"

Note: City-level detailed breakdowns combine multiple data sources as the full 2020 Census
Detailed DHC-A data is still being released and processed at the local level.
"""
