"""
FBref MLS Player Stats Scraper (Selenium Version)
Connects to an existing Chrome browser session that YOU control.

SETUP:
1. First, start Chrome with remote debugging enabled:
   
   Mac:
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
   
2. In that Chrome window:
   - Go to https://fbref.com/en/comps/22/stats/Major-League-Soccer-Stats
   - Pass any Cloudflare checks
   - Click the "Show" button to reveal the Player Standard Stats table
   - Make sure you can see the player stats table

3. Run this script:
   python MLS_Stats.py

REQUIREMENTS:
    pip install pandas lxml html5lib selenium webdriver-manager beautifulsoup4
"""

import pandas as pd
import time
from io import StringIO

import os
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Create data folder if it doesn't exist
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)


def extract_glossary_from_html(html: str) -> dict:
    """
    Extract column abbreviations and their full names from FBref HTML.
    FBref has a glossary section with format: "Abbrev -- Full Name Description"
    We want to map the abbreviation to the full name (the part right after --).
    """
    soup = BeautifulSoup(html, 'lxml')
    glossary = {}
    
    # Method 1: Look for glossary in the page text
    # The glossary format is: "Abbrev -- Full Name Description"
    page_text = soup.get_text()
    
    # Find all lines with " -- " pattern
    import re
    # Match pattern: word(s) -- Full Name (possibly more words)
    # We want the abbreviation and the first part after --
    pattern = r'([A-Za-z0-9+/]+)\s*--\s*([^\n]+)'
    matches = re.findall(pattern, page_text)
    
    for abbrev, full_description in matches:
        abbrev = abbrev.strip()
        full_description = full_description.strip()
        
        # The full name is typically the first few words before a longer description
        # Often it's repeated, like "Shot-Creating Actions Shot-Creating Actions The two..."
        # So we take the first meaningful phrase
        
        # Split by common description starters
        for splitter in [' The ', ' Minimum ', ' Given ', ' Position ', ' This is ', ' First,']:
            if splitter in full_description:
                full_description = full_description.split(splitter)[0]
                break
        
        # Clean up - remove duplicate phrases
        words = full_description.split()
        if len(words) >= 4:
            mid = len(words) // 2
            first_half = ' '.join(words[:mid])
            second_half = ' '.join(words[mid:2*mid])
            if first_half == second_half:
                full_description = first_half
        
        full_description = full_description.strip()
        
        if abbrev and full_description and len(abbrev) < 20:
            glossary[abbrev] = full_description
    
    # Method 2: Also check data-tip attributes on table headers as backup
    for th in soup.find_all('th'):
        abbrev = th.get_text(strip=True)
        full_name = None
        
        if th.get('data-tip'):
            full_name = th.get('data-tip')
        elif th.get('aria-label'):
            full_name = th.get('aria-label')
        else:
            for child in th.find_all(['span', 'a']):
                if child.get('data-tip'):
                    full_name = child.get('data-tip')
                    break
        
        if abbrev and full_name and abbrev != full_name and abbrev not in glossary:
            if '<' in full_name:
                full_name = BeautifulSoup(full_name, 'lxml').get_text(strip=True)
            glossary[abbrev] = full_name.strip()
    
    return glossary


def rename_columns_with_glossary(df, glossary: dict):
    """Rename DataFrame columns using the glossary mapping."""
    new_columns = []
    for col in df.columns:
        col_str = str(col)
        # Check if this column has a full name in the glossary
        if col_str in glossary:
            new_columns.append(glossary[col_str])
        else:
            new_columns.append(col_str)
    df.columns = new_columns
    return df


def scrape_from_existing_browser(output_file: str = "mls_player_stats.csv") -> pd.DataFrame:
    """
    Connect to an existing Chrome session and scrape the page.
    You must have Chrome open with --remote-debugging-port=9222
    """
    print("Connecting to existing Chrome session on port 9222...")
    
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"\nERROR: Could not connect to Chrome: {e}")
        print("\nMake sure you started Chrome with remote debugging:")
        print("  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug")
        return None
    
    try:
        print(f"Connected! Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Get the page HTML
        html = driver.page_source
        
        # Save for debugging
        with open("debug_page.html", "w", encoding='utf-8') as f:
            f.write(html)
        print("Saved debug_page.html")
        
        # Count tables
        table_count = html.lower().count("<table")
        print(f"Found {table_count} <table> tags in HTML")
        
        if table_count == 0:
            print("ERROR: No tables found. Make sure you clicked 'Show' to reveal the table.")
            return None
        
        # Parse tables (allow duplicate column names)
        try:
            tables = pd.read_html(StringIO(html), flavor='lxml')
            print(f"Parsed {len(tables)} tables")
        except ValueError:
            tables = pd.read_html(StringIO(html), flavor='html5lib')
            print(f"Parsed {len(tables)} tables with html5lib")
        
        # Re-parse the tables without modifying duplicate columns
        pd.set_option('mode.chained_assignment', None)
        
        # Find the Player Standard Stats table
        player_stats_df = None
        
        for i, table in enumerate(tables):
            # Flatten multi-level columns
            if isinstance(table.columns, pd.MultiIndex):
                table.columns = ['_'.join(str(c) for c in col).strip() 
                                for col in table.columns.values]
            
            cols_lower = [str(c).lower() for c in table.columns]
            has_player = any('player' in c for c in cols_lower)
            has_squad = any('squad' in c for c in cols_lower)
            
            print(f"  Table {i}: {table.shape}, player={has_player}, squad={has_squad}")
            
            if has_player and has_squad and len(table) > 50:
                player_stats_df = table
                print(f"\n✓ Found Player Standard Stats (index {i}) with {len(table)} rows")
                break
        
        if player_stats_df is None:
            print("\nCould not find Player Standard Stats table")
            print("Make sure you clicked the 'Show' button on the page!")
            return None
        
        # Extract glossary from HTML and rename columns
        print("Extracting column glossary from page...")
        glossary = extract_glossary_from_html(html)
        if glossary:
            print(f"  Found {len(glossary)} column definitions")
        
        # Clean the dataframe
        df = clean_player_stats(player_stats_df)
        
        # Rename columns with full names
        if glossary:
            df = rename_columns_with_glossary(df, glossary)
            print("  Renamed columns to full names")
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"\n✓ Saved {len(df)} player records to {output_file}")
        
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        raise
        
    finally:
        # Don't quit - leave the browser open since user opened it
        print("Done! (Browser left open)")


def clean_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and format the player stats DataFrame."""
    df = df.copy()
    
    # Flatten multi-level columns if still present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(str(c) for c in col).strip() 
                     for col in df.columns.values]
    
    # Find player column
    player_col = [c for c in df.columns if 'player' in str(c).lower()][0]
    
    # Remove header rows embedded in data
    df = df[df[player_col] != 'Player']
    df = df.reset_index(drop=True)
    
    # Clean column names - remove prefixes from multi-level headers
    clean_cols = []
    for col in df.columns:
        col_str = str(col)
        for prefix in ['Unnamed:', 'Playing Time_', 'Performance_', 'Expected_', 'Per 90 Minutes_', 'level_0_']:
            col_str = col_str.replace(prefix, '')
        col_str = col_str.strip('_').strip()
        clean_cols.append(col_str)
    df.columns = clean_cols
    
    return df


if __name__ == "__main__":
    print("="*60)
    print("FBref MLS Scraper - Manual Browser Mode")
    print("="*60)
    print()
    print("INSTRUCTIONS:")
    print("1. Close all Chrome windows")
    print("2. Start Chrome with debugging enabled:")
    print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug")
    print()
    print("3. In that Chrome window, go to:")
    print("   https://fbref.com/en/comps/22/stats/Major-League-Soccer-Stats")
    print()
    print("4. Pass any Cloudflare checks")
    print("5. Click 'Show' to reveal the Player Standard Stats table")
    print()
    print(f"All CSV files will be saved to: ./{DATA_FOLDER}/")
    print()
    
    while True:
        print("-"*60)
        input("Press Enter when ready to scrape (or Ctrl+C to quit)...")
        
        # Ask for output filename
        print()
        output_file = input("Output filename (default: mls_player_stats.csv): ").strip()
        if not output_file:
            output_file = "mls_player_stats.csv"
        if not output_file.endswith('.csv'):
            output_file += '.csv'
        
        # Save to data folder
        output_path = os.path.join(DATA_FOLDER, output_file)
        
        df = scrape_from_existing_browser(output_file=output_path)
        
        if df is not None:
            print("\n" + "="*60)
            print("Sample of scraped data:")
            print("="*60)
            print(df.head(10).to_string())
            print(f"\nTotal players: {len(df)}")
            print(f"Columns: {list(df.columns)}")
        else:
            print("\nFailed to scrape data.")
        
        print("\n\nReady for next scrape. Navigate to a new page and click 'Show'.") 