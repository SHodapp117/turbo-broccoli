#!/bin/bash

# MLS Free Agent Valuator Launcher Script

echo "=================================="
echo "MLS Free Agent Contract Valuator"
echo "=================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Check if free agents data exists
if [ ! -f "data/free_agents_2026.csv" ]; then
    echo "Free agents data not found. Generating..."
    python find_free_agents_2026.py
    echo ""
fi

# Launch Streamlit app
echo "Launching Streamlit app..."
echo "The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the app"
echo ""

streamlit run app.py
