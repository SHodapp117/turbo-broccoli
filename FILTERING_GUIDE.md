# Player Selection & Filtering Guide

## 🎯 New Dynamic Filter System

The app now features a hierarchical, dynamic filtering system that makes it easy to find and analyze specific players.

## 📊 Filter Hierarchy

### Primary Filters (Always Visible)

#### 1. **Team Filter**
- **Default**: "All Teams"
- **Options**: All 30 MLS teams
- **Effect**: Filters all subsequent dropdowns
- **Example**: Select "SEATTLE SOUNDERS FC" to see only Sounders players

#### 2. **Position Filter** (Dynamic)
- **Default**: "All Positions"
- **Options**: Updates based on Team selection
- **Available Positions**: FW, MF, DF, GK
- **Example**:
  - If Team = "All Teams", shows all positions
  - If Team = "SEATTLE SOUNDERS FC", shows only positions with Sounders free agents

#### 3. **Player Name Filter** (Dynamic)
- **Default**: "All Players"
- **Options**: Updates based on Team AND Position selections
- **Behavior**:
  - If Team + Position are "All", shows all 433 free agents
  - If Team selected, shows only that team's players
  - If Team + Position selected, shows only matching players
- **Direct Selection**: Choose a specific player to jump directly to their valuation

### Additional Filters

#### 4. **Contract Designation**
- TAM Player
- Designated Player
- Homegrown Player
- U22 Initiative
- Generation adidas
- All Designations

#### 5. **Contract Status**
- All Players
- With Team Option (346 players)
- No Team Option (87 true free agents)

## 🔄 How Dynamic Filtering Works

### Example 1: Finding a Specific Player
1. **Team**: Select "INTER MIAMI CF"
2. **Position**: Select "FW"
3. **Player Name**: Select "Lionel Messi"
4. ✅ Valuation loads immediately

### Example 2: Browsing by Position
1. **Team**: "All Teams"
2. **Position**: "GK"
3. **Player Name**: "All Players"
4. Main dropdown shows all goalkeeper free agents
5. Select from formatted list

### Example 3: Team Analysis
1. **Team**: "ATLANTA UNITED"
2. **Position**: "All Positions"
3. **Player Name**: "All Players"
4. See all 16 Atlanta United free agents in dropdown

### Example 4: Using Additional Filters
1. **Team**: "All Teams"
2. **Position**: "MF"
3. **Player Name**: "All Players"
4. **Contract Status**: "No Team Option"
5. See midfielders who are true free agents (no team options)

## 📋 Filter Combinations

### Common Use Cases

**Find Undervalued Players**
- Team: "All Teams"
- Position: "All Positions"
- Player Name: "All Players"
- Designation: "TAM Player"
- Status: "No Team Option"
→ Browse TAM midfielders without team options

**Evaluate Team Options**
- Team: [Your Team]
- Position: "All Positions"
- Player Name: "All Players"
- Status: "With Team Option"
→ See which players your team can extend

**Position-Specific Scouting**
- Team: "All Teams"
- Position: "DF"
- Player Name: "All Players"
- Designation: "All Designations"
→ Browse all defender free agents

**Direct Player Lookup**
- Team: [Player's Team] (or "All Teams")
- Position: [Player's Position] (or "All Positions")
- Player Name: [Specific Player]
→ Instant valuation

## 🎮 Two Ways to Select Players

### Method 1: Sidebar Direct Selection
Use the **Player Name** dropdown in the sidebar to directly select a player. When selected:
- Valuation loads immediately
- Header shows "Valuation for [Player Name]"
- Info message: "Player selected via sidebar filter"
- To change: Update any sidebar filter

### Method 2: Main Dropdown
Keep **Player Name** as "All Players" to use the main selection dropdown:
- Shows formatted list with team, designation, and options
- Dropdown updates based on all active filters
- Example format: "Paul Rothrock - SEATTLE SOUNDERS FC (nan)"

## 🔍 Filter Reset

To see all players again:
1. Set Team: "All Teams"
2. Set Position: "All Positions"
3. Set Player Name: "All Players"
4. Set Designation: "All Designations"
5. Set Status: "All Players"

## 💡 Tips

✅ **Start Broad, Then Narrow**: Begin with "All" selections, then add filters
✅ **Use Position for Quick Search**: Position filter is very effective
✅ **Direct Selection is Fastest**: If you know the player, use sidebar Player Name
✅ **Check Metrics Dashboard**: Shows how many players match current filters
✅ **Additional Filters are Optional**: Primary filters (Team/Position/Name) work standalone

## 📊 Filter Metrics

The dashboard shows real-time counts:
- **Total Free Agents**: Always 433
- **Filtered Results**: Updates based on all active filters
- **With Team Options**: 346 players
- **No Options**: 87 players

## 🎯 Power User Shortcuts

**All True Free Agents**
- Team: "All Teams"
- Position: "All Positions"
- Player Name: "All Players"
- Status: "No Team Option"

**Team's Midfielders**
- Team: [Your Team]
- Position: "MF"
- Player Name: "All Players"

**All DPs Available**
- Team: "All Teams"
- Position: "All Positions"
- Player Name: "All Players"
- Designation: "Designated Player"
- Status: "No Team Option"
