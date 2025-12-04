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
    pip install pandas lxml html5lib selenium webdriver-manager
"""

import pandas as pd
import time
from io import StringIO

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        
        # Clean the dataframe
        df = clean_player_stats(player_stats_df)
        
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
    print("6. Once you can see the player stats, press Enter here...")
    print()
    
    input("Press Enter when ready...")
    
    df = scrape_from_existing_browser(output_file="mls_player_stats.csv")
    
    if df is not None:
        print("\n" + "="*60)
        print("Sample of scraped data:")
        print("="*60)
        print(df.head(10).to_string())
        print(f"\nTotal players: {len(df)}")
        print(f"Columns: {list(df.columns)}")
    else:
        print("\nFailed to scrape data.")