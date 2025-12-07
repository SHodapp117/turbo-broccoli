# EA Sports FC 25 Position Data - Setup Guide

This guide walks you through downloading granular position data from Kaggle's EA Sports FC 25 dataset.

## Step 1: Install Kaggle CLI

```bash
pip install kaggle
```

## Step 2: Get Kaggle API Credentials

1. **Create a Kaggle account** (if you don't have one)
   - Go to: https://www.kaggle.com
   - Sign up for free

2. **Generate API token**
   - Go to: https://www.kaggle.com/settings/account
   - Scroll to "API" section
   - Click **"Create New Token"**
   - This downloads `kaggle.json` to your Downloads folder

3. **Install credentials**
   ```bash
   # Create kaggle directory
   mkdir -p ~/.kaggle

   # Move the downloaded file
   mv ~/Downloads/kaggle.json ~/.kaggle/

   # Set permissions (important for security)
   chmod 600 ~/.kaggle/kaggle.json
   ```

## Step 3: Run the Download Script

```bash
# Make script executable
chmod +x scripts/download_fc25_positions.py

# Run the script
python scripts/download_fc25_positions.py
```

## What This Does

The script will:

1. ✅ Download the EA Sports FC 25 dataset from Kaggle
2. ✅ Extract the player CSV files
3. ✅ Filter for MLS players only
4. ✅ Save position data to `data/fc25_mls_positions.csv`
5. ✅ Show position distribution statistics

## Expected Output

You'll get a CSV file with columns like:

- `Name` - Player name
- `Position` - Primary position (GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST, CF)
- `Alternative positions` - Other positions they can play
- `Team` - Club name
- `League` - Should be "MLS"
- `Age` - Player age

## Position Codes You'll See

| Code | Position |
|------|----------|
| GK   | Goalkeeper |
| CB   | Center Back |
| LB   | Left Back |
| RB   | Right Back |
| LWB  | Left Wing Back |
| RWB  | Right Wing Back |
| CDM  | Center Defensive Midfield |
| CM   | Center Midfield |
| CAM  | Center Attacking Midfield |
| LM   | Left Midfield |
| RM   | Right Midfield |
| LW   | Left Winger |
| RW   | Right Winger |
| ST   | Striker |
| CF   | Center Forward |

## Troubleshooting

### "No module named 'kaggle'"
```bash
pip install kaggle
```

### "Unauthorized"
- Make sure `kaggle.json` is in `~/.kaggle/`
- Check permissions: `ls -la ~/.kaggle/kaggle.json` (should show `-rw-------`)

### "Dataset not found"
- The dataset might have been renamed or removed
- Check: https://www.kaggle.com/datasets/nyagami/ea-sports-fc-25-database-ratings-and-stats

### No MLS players found
- The script will save all players
- You can manually filter by League = "MLS" in Excel/Python

## Next Steps

After running this script, proceed to:

1. **Name Mapping** - Match FC 25 names to your FBref player names
2. **Data Integration** - Merge position data into your existing datasets
3. **Update Code** - Modify `Player_Valuation.py` to use granular positions
