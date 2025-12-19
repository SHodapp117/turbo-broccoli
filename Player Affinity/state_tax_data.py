"""
MLS State Income Tax Data for 2025
Complete tax schedules for all states where MLS teams operate
"""

# MLS Teams by State (30 teams total including San Diego FC in 2025)
MLS_TEAMS = {
    'California': ['LA Galaxy', 'Los Angeles Football Club', 'San Jose Earthquakes', 'San Diego FC'],
    'Colorado': ['Colorado Rapids'],
    'Florida': ['Inter Miami CF', 'Orlando City SC'],
    'Georgia': ['Atlanta United'],
    'Illinois': ['Chicago Fire FC'],
    'Kansas': ['Sporting Kansas City'],
    'Massachusetts': ['New England Revolution'],
    'Minnesota': ['Minnesota United FC'],
    'New Jersey': ['New York Red Bulls'],
    'New York': ['New York City FC'],
    'Ohio': ['Columbus Crew SC', 'FC Cincinnati'],
    'Oregon': ['Portland Timbers'],
    'Pennsylvania': ['Philadelphia Union'],
    'Tennessee': ['Nashville SC'],
    'Texas': ['FC Dallas', 'Houston Dynamo'],
    'Utah': ['Real Salt Lake'],
    'Washington': ['Seattle Sounders FC']
}

# State Income Tax Rates and Brackets for 2025
STATE_TAX_INFO = {
    'California': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 10412, 'rate': 1.0},
            {'min': 10412, 'max': 24684, 'rate': 2.0},
            {'min': 24684, 'max': 38959, 'rate': 4.0},
            {'min': 38959, 'max': 54081, 'rate': 6.0},
            {'min': 54081, 'max': 68350, 'rate': 8.0},
            {'min': 68350, 'max': 349137, 'rate': 9.3},
            {'min': 349137, 'max': 418961, 'rate': 10.3},
            {'min': 418961, 'max': 698271, 'rate': 11.3},
            {'min': 698271, 'max': float('inf'), 'rate': 12.3}
        ],
        'top_rate': 13.3,  # 12.3% + 1% mental health surcharge on income over $1M
        'notes': '1% mental health services tax surcharge on income over $1 million brings effective top rate to 13.3%',
        'standard_deduction_single': 5540,
        'standard_deduction_joint': 11080
    },

    'Colorado': {
        'tax_type': 'Flat',
        'rate': 4.4,
        'top_rate': 4.4,
        'notes': 'Flat rate applies to all income levels',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Florida': {
        'tax_type': 'None',
        'rate': 0,
        'top_rate': 0,
        'notes': 'No state income tax. Revenue from sales tax (6%), property tax (0.74% effective), and other sources',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Georgia': {
        'tax_type': 'Flat',
        'rate': 5.19,
        'top_rate': 5.19,
        'notes': 'Flat 5.19% rate effective July 1, 2025 (retroactive to Jan 1). Will decrease to 4.99% by 2029',
        'standard_deduction_single': 12000,
        'standard_deduction_joint': 24000
    },

    'Illinois': {
        'tax_type': 'Flat',
        'rate': 4.95,
        'top_rate': 4.95,
        'notes': 'Flat rate applies to all income levels',
        'standard_deduction_single': None,
        'standard_deduction_joint': None,
        'personal_exemption': 2850
    },

    'Kansas': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 23000, 'rate': 5.20},  # Approximate threshold
            {'min': 23000, 'max': float('inf'), 'rate': 5.58}
        ],
        'top_rate': 5.58,
        'notes': 'Two brackets as of 2024 tax reform. Personal exemption: $18,320 (joint), $9,160 (single)',
        'standard_deduction_single': None,
        'standard_deduction_joint': None,
        'personal_exemption_single': 9160,
        'personal_exemption_joint': 18320
    },

    'Massachusetts': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 1000000, 'rate': 5.0},
            {'min': 1000000, 'max': float('inf'), 'rate': 9.0}
        ],
        'top_rate': 9.0,
        'notes': '5% base rate plus 4% surtax on income over $1 million',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Minnesota': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 30070, 'rate': 5.35},
            {'min': 30070, 'max': 98760, 'rate': 6.80},
            {'min': 98760, 'max': 183340, 'rate': 7.85},
            {'min': 183340, 'max': float('inf'), 'rate': 9.85}
        ],
        'top_rate': 9.85,
        'notes': 'Among the highest top rates in the country',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'New Jersey': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 20000, 'rate': 1.4},
            {'min': 20000, 'max': 35000, 'rate': 1.75},
            {'min': 35000, 'max': 40000, 'rate': 3.5},
            {'min': 40000, 'max': 75000, 'rate': 5.525},
            {'min': 75000, 'max': 500000, 'rate': 6.37},
            {'min': 500000, 'max': 1000000, 'rate': 8.97},
            {'min': 1000000, 'max': float('inf'), 'rate': 10.75}
        ],
        'top_rate': 10.75,
        'notes': 'Top rate of 10.75% on income over $1 million',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'New York': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 8500, 'rate': 4.0},
            {'min': 8500, 'max': 11700, 'rate': 4.5},
            {'min': 11700, 'max': 13900, 'rate': 5.25},
            {'min': 13900, 'max': 80650, 'rate': 5.5},
            {'min': 80650, 'max': 215400, 'rate': 6.0},
            {'min': 215400, 'max': 1077550, 'rate': 6.85},
            {'min': 1077550, 'max': 5000000, 'rate': 9.65},
            {'min': 5000000, 'max': 25000000, 'rate': 10.3},
            {'min': 25000000, 'max': float('inf'), 'rate': 10.9}
        ],
        'top_rate': 10.9,
        'notes': 'Top rate of 10.9% on income over $25 million. Has tax benefit recapture provision',
        'standard_deduction_single': 8000,
        'standard_deduction_joint': 16050
    },

    'Ohio': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 26050, 'rate': 0.0},
            {'min': 26050, 'max': 100000, 'rate': 2.75},  # Approximate
            {'min': 100000, 'max': float('inf'), 'rate': 3.5}
        ],
        'top_rate': 3.5,
        'notes': 'Three brackets. First $26,050 is tax-free for single filers',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Oregon': {
        'tax_type': 'Progressive',
        'brackets': [
            {'min': 0, 'max': 4400, 'rate': 4.75},
            {'min': 4400, 'max': 11050, 'rate': 6.75},
            {'min': 11050, 'max': 125000, 'rate': 8.75},
            {'min': 125000, 'max': float('inf'), 'rate': 9.90}
        ],
        'top_rate': 9.90,
        'notes': 'Four brackets ranging from 4.75% to 9.9%',
        'standard_deduction_single': 2835,
        'standard_deduction_joint': 5670,
        'tax_credit_per_exemption': 256
    },

    'Pennsylvania': {
        'tax_type': 'Flat',
        'rate': 3.07,
        'top_rate': 3.07,
        'notes': 'Flat rate of 3.07%. Retirement income is not taxed',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Tennessee': {
        'tax_type': 'None',
        'rate': 0,
        'top_rate': 0,
        'notes': 'No state income tax',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Texas': {
        'tax_type': 'None',
        'rate': 0,
        'top_rate': 0,
        'notes': 'No state income tax. Constitutional ban on personal income tax. Revenue from sales tax (6.25%) and property tax (1.36% effective)',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Utah': {
        'tax_type': 'Flat',
        'rate': 4.65,
        'top_rate': 4.65,
        'notes': 'Flat rate applies to all income levels',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    },

    'Washington': {
        'tax_type': 'None',
        'rate': 0,
        'top_rate': 0,
        'notes': 'No state income tax on wages. Has 7% capital gains tax on profits over $270K, plus additional 2.9% on gains over $1M (effective 2025)',
        'standard_deduction_single': None,
        'standard_deduction_joint': None
    }
}

def get_effective_tax_rate(state, income, filing_status='single'):
    """
    Calculate effective tax rate for a given state and income level

    Args:
        state: State name
        income: Annual income
        filing_status: 'single' or 'joint'

    Returns:
        Effective tax rate as percentage
    """
    if state not in STATE_TAX_INFO:
        return 0

    tax_info = STATE_TAX_INFO[state]

    # Handle states with no income tax
    if tax_info['tax_type'] == 'None':
        return 0

    # Handle flat tax states
    if tax_info['tax_type'] == 'Flat':
        return tax_info['rate']

    # Handle progressive tax states
    if tax_info['tax_type'] == 'Progressive':
        total_tax = 0
        brackets = tax_info['brackets']

        for i, bracket in enumerate(brackets):
            bracket_min = bracket['min']
            bracket_max = bracket['max']
            rate = bracket['rate']

            if income > bracket_min:
                taxable_in_bracket = min(income, bracket_max) - bracket_min
                total_tax += taxable_in_bracket * (rate / 100)

        return (total_tax / income * 100) if income > 0 else 0

    return 0

def get_tax_burden_comparison():
    """
    Get comparative analysis of tax burdens across MLS states

    Returns:
        Dictionary with analysis data
    """
    states_with_no_tax = [state for state, info in STATE_TAX_INFO.items()
                          if info['tax_type'] == 'None']

    states_with_flat_tax = [state for state, info in STATE_TAX_INFO.items()
                            if info['tax_type'] == 'Flat']

    states_with_progressive_tax = [state for state, info in STATE_TAX_INFO.items()
                                   if info['tax_type'] == 'Progressive']

    # Sort by top rate
    states_by_top_rate = sorted(STATE_TAX_INFO.items(),
                                key=lambda x: x[1]['top_rate'],
                                reverse=True)

    return {
        'no_tax_states': states_with_no_tax,
        'flat_tax_states': states_with_flat_tax,
        'progressive_tax_states': states_with_progressive_tax,
        'states_by_top_rate': states_by_top_rate,
        'total_states': len(STATE_TAX_INFO),
        'average_top_rate': sum(info['top_rate'] for info in STATE_TAX_INFO.values()) / len(STATE_TAX_INFO)
    }
