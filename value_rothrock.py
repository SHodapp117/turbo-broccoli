"""
Quick script to value Paul Rothrock
"""

from Player_Valuation import PlayerValuationSystem

# Initialize
system = PlayerValuationSystem()

# Load data
system.load_and_merge_data(season=2025)

# Train designation classifiers
system.train_designation_classifiers(min_minutes=900)

# Load archetypes
system.load_archetypes()

# Value Paul Rothrock
print("\n" + "="*60)
print("PAUL ROTHROCK CONTRACT VALUATION")
print("="*60)

result = system.value_player('Paul Rothrock')

# Print detailed summary
if 'error' not in result:
    print("\n" + "="*60)
    print("CONTRACT RECOMMENDATION")
    print("="*60)

    if 'salary_estimate' in result and 'predicted_salary' in result['salary_estimate']:
        est = result['salary_estimate']

        print(f"\nRECOMMENDED CONTRACT VALUE:")
        print(f"  Base Salary: ${est['predicted_salary']/1000:.0f}K")
        print(f"\nNEGOTIATION RANGE (25th-75th percentile):")
        print(f"  Low End:  ${est['salary_range_low']/1000:.0f}K")
        print(f"  High End: ${est['salary_range_high']/1000:.0f}K")
        print(f"\nPEER MARKET RANGE:")
        print(f"  Minimum: ${est['peer_min']/1000:.0f}K")
        print(f"  Maximum: ${est['peer_max']/1000:.0f}K")

        print(f"\nCONTRACT TIER: {result['predicted_designation']}")

        if 'designation_confidence' in result:
            print(f"\nTIER PROBABILITIES:")
            for tier, prob in sorted(result['designation_confidence'].items(),
                                    key=lambda x: x[1], reverse=True):
                print(f"  {tier}: {prob:.1%}")

        archetype_text = 'Elite/Specialist (Outlier)' if result.get('is_outlier') else f'Archetype {result.get("archetype", "Unknown")}'
        print(f"\nPLAYER ARCHETYPE: {archetype_text}")

        if 'actual_salary' in result and result['actual_salary']:
            print(f"\nCURRENT SALARY: ${result['actual_salary']/1000:.0f}K")
            diff = est['predicted_salary'] - result['actual_salary']
            if diff > 0:
                print(f"MARKET ADJUSTMENT: +${abs(diff)/1000:.0f}K ({abs(diff)/result['actual_salary']*100:.1f}% raise recommended)")
            else:
                print(f"MARKET ADJUSTMENT: -${abs(diff)/1000:.0f}K ({abs(diff)/result['actual_salary']*100:.1f}% overpaid)")

        print(f"\nSIMILAR PLAYERS (Statistical Peers):")
        for i, (name, salary) in enumerate(zip(est['peer_names'], est['peer_salaries']), 1):
            print(f"  {i}. {name}: ${salary/1000:.0f}K")
else:
    print(f"\nError: {result.get('error', 'Unknown error')}")
