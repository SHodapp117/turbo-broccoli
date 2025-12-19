# Player Affinity Dashboard

A Streamlit-based data dashboard for analyzing player performance metrics and team dynamics.

## Features

- Interactive data visualizations with Plotly
- Multi-tab interface for different analytics views
- Customizable filters and player selection
- Performance metrics and comparisons
- Responsive layout with modern UI

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Navigate to the project directory:
```bash
cd "Player Affinity"
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

Start the Streamlit app with:
```bash
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

## Project Structure

```
Player Affinity/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Customization

The current app uses sample data for demonstration. To use your own data:

1. Replace the `sample_data` DataFrame in [app.py](app.py) with your actual data source
2. Update filters and metrics to match your data schema
3. Customize visualizations based on your specific analytics needs

## Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

## Next Steps

- Add data loading from CSV/Excel files
- Implement database connectivity
- Create additional analytics views
- Add export functionality for reports
- Implement user authentication if needed
