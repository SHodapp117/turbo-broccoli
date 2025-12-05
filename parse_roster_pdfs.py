"""
MLS Club Roster Profile PDF Parser

Extracts structured data from MLS Club Roster Profile PDFs into CSV format.
Parses player information including names, designations, contracts, and status.
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path


def parse_roster_pdf(pdf_path):
    """
    Parse an MLS Club Roster Profile PDF and extract all team and player data.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of player dictionaries
    """
    all_players = []
    current_team = None
    current_roster_model = None
    current_gam = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Skip cover/info pages
            if page_num <= 3:
                continue

            text = page.extract_text()
            if not text:
                continue

            # Extract team name from header
            team_match = re.search(r'^([A-Z\s&\.FC]+)\s*\|\s*ROSTER PROFILE', text, re.MULTILINE)
            if team_match:
                current_team = team_match.group(1).strip()
                print(f"  Found team: {current_team}")

            # Extract roster model
            model_match = re.search(r'Roster Construction Model:\s*(.+)', text)
            if model_match:
                current_roster_model = model_match.group(1).strip()

            # Extract GAM
            gam_match = re.search(r'2025 GAM AVAILABLE\s*\$?([\d,]+)', text)
            if gam_match:
                current_gam = gam_match.group(1).replace(',', '')

            if not current_team:
                continue

            # Extract tables
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Check if this is a roster table - header might be in row 0 or 1
                headers = None
                start_row = 0

                # Try first row as headers
                if table[0]:
                    test_headers = [str(h).upper() if h else '' for h in table[0]]
                    if 'ROSTER DESIGNATION' in ' '.join(test_headers):
                        headers = test_headers
                        start_row = 1

                # Try second row as headers
                if not headers and len(table) > 1:
                    test_headers = [str(h).upper() if h else '' for h in table[1]]
                    if 'ROSTER DESIGNATION' in ' '.join(test_headers):
                        headers = test_headers
                        start_row = 2

                # Skip if not a roster table
                if not headers or 'NAME' not in ' '.join(headers):
                    continue

                # Find column indices
                name_idx = None
                designation_idx = None
                status_idx = None
                contract_idx = None
                option_idx = None

                for i, h in enumerate(headers):
                    if 'NAME' in h and name_idx is None:
                        name_idx = i
                    elif 'DESIGNATION' in h:
                        designation_idx = i
                    elif 'STATUS' in h:
                        status_idx = i
                    elif 'CONTRACT' in h and 'THRU' in h:
                        contract_idx = i
                    elif 'OPTION' in h:
                        option_idx = i

                if name_idx is None:
                    continue

                # Parse each row (starting after headers)
                for row in table[start_row:]:
                    if not row or len(row) <= name_idx:
                        continue

                    player_name = row[name_idx]

                    # Skip empty rows, headers, and section markers
                    if not player_name or not str(player_name).strip():
                        continue

                    player_name = str(player_name).strip()

                    # Skip non-player rows
                    skip_terms = ['NAME', 'SENIOR ROSTER', 'SUPPLEMENTAL ROSTER',
                                  'SUPPLEMENTAL SPOT', 'OFF-ROSTER', 'DESIGNATED PLAYERS',
                                  'U22 INITIATIVE', 'UNAVAILABLE PLAYERS', 'NO.']
                    if any(term in player_name.upper() for term in skip_terms):
                        continue

                    # Extract designation
                    designation = ''
                    if designation_idx is not None and len(row) > designation_idx:
                        designation = str(row[designation_idx]).strip() if row[designation_idx] else ''

                    # Extract status
                    status = ''
                    if status_idx is not None and len(row) > status_idx:
                        status = str(row[status_idx]).strip() if row[status_idx] else ''

                    # Extract contract year
                    contract = ''
                    if contract_idx is not None and len(row) > contract_idx:
                        contract = str(row[contract_idx]).strip() if row[contract_idx] else ''

                    # Extract option years
                    options = ''
                    if option_idx is not None and len(row) > option_idx:
                        options = str(row[option_idx]).strip() if row[option_idx] else ''

                    # Determine category
                    category = 'Standard'
                    if 'Designated Player' in designation or 'Young Designated' in designation:
                        category = 'Designated Player'
                    elif 'U22 Initiative' in designation:
                        category = 'U22 Initiative'
                    elif 'TAM Player' in designation:
                        category = 'TAM Player'
                    elif 'Homegrown' in designation:
                        category = 'Homegrown'
                    elif 'Generation adidas' in designation:
                        category = 'Generation Adidas'

                    # Create player record
                    player = {
                        'team': current_team,
                        'name': player_name,
                        'roster_designation': designation,
                        'current_status': status,
                        'contract_thru': contract,
                        'option_years': options,
                        'category': category,
                        'roster_model': current_roster_model or '',
                        'team_gam_2025': current_gam or ''
                    }

                    all_players.append(player)

    return all_players


def main():
    """Main execution function"""

    # Define paths
    data_dir = Path('/Users/mojo/special projects /MLS Project/turbo-broccoli/data')

    # Find all roster profile PDFs
    pdf_files = list(data_dir.glob('*Roster Profile*.pdf'))

    if not pdf_files:
        print("No Club Roster Profile PDFs found in the data directory.")
        return

    print(f"Found {len(pdf_files)} roster profile PDF(s)\n")

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")

        # Parse the PDF
        players = parse_roster_pdf(pdf_file)

        print(f"Total players extracted: {len(players)}\n")

        if not players:
            print("WARNING: No players extracted! Check PDF format.\n")
            continue

        # Convert to DataFrame
        df = pd.DataFrame(players)

        # Generate output filename
        season = '2025' if '2025' in pdf_file.name else '2024'
        output_file = data_dir / f'{season}_roster_profiles_parsed.csv'

        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"✓ Saved to: {output_file}")

        # Print summary statistics
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        print(f"Total teams: {df['team'].nunique()}")
        print(f"Total players: {len(df)}")

        print(f"\nPlayers by category:")
        category_counts = df['category'].value_counts()
        for cat, count in category_counts.items():
            print(f"  {cat}: {count}")

        print(f"\nPlayers by status:")
        status_counts = df['current_status'].value_counts()
        for status, count in list(status_counts.items())[:10]:  # Top 10
            if status:
                print(f"  {status}: {count}")

        print(f"\nTop 10 teams by roster size:")
        team_counts = df['team'].value_counts().head(10)
        for team, count in team_counts.items():
            print(f"  {team}: {count}")

        # Show sample
        print("\n" + "="*60)
        print("SAMPLE DATA (first 10 rows)")
        print("="*60)
        print(df[['team', 'name', 'category', 'contract_thru']].head(10).to_string(index=False))

        print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
