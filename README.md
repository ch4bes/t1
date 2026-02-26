# Weather Forecast Tracker

A tool for tracking weather forecast accuracy over time. This project helps you understand how weather predictions evolve and improve as the forecasted date approaches.

## Overview

Weather forecasts are typically issued for a window of ~10 days. The accuracy of these forecasts changes as the target date gets closer. This tool allows you to:

- **Track forecast evolution** - Record daily forecasts and watch them change over time
- **Compare to actuals** - Record actual weather and compare against predictions
- **Analyze accuracy** - See how forecast accuracy improves as dates approach
- **Identify patterns** - Understand which forecast horizons are most reliable

## Weather Data Sources

This project works with any weather station or forecast source. For **Weather Underground Personal Weather Stations (PWS)**:

### Finding Your Station

1. Visit [Weather Underground](https://www.wunderground.com/)
2. Search for your location or PWS ID
3. Copy the station ID (e.g., `KYOURPWS123`)

### Data Sources (replace YOUR_STATION with your PWS ID)

- **10-Day Forecast:** `https://www.wunderground.com/forecast/.../YOUR_STATION`
- **Historical Data:** `https://www.wunderground.com/dashboard/pws/YOUR_STATION`

### Quick Setup

```bash
python3 run.py init

# Add your weather station
python3 run.py add-station KYOURPWS123 "Home Station"

# Or add any custom location
python3 run.py add-location "San Francisco" 37.00 -120.00 "Bay Area, CA"
```

## Project Structure

```
t1/
├── models/              # Database models
│   ├── database.py      # Database configuration
│   └── models.py        # SQLAlchemy models
├── services/            # Business logic
│   └── weather_service.py
├── analysis/            # Accuracy analysis
│   └── accuracy.py
├── scripts/             # CLI tools
│   └── cli.py
├── requirements.txt     # Python dependencies
└── README.md
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python3 run.py init
```

## Usage

All commands are run via `python3 run.py <command>`:

### Add a Location

```bash
python3 run.py add-location "San Francisco" 37.0049 -122.4194 "Bay Area, CA"
```

### List Locations

```bash
python3 run.py list-locations
```

### Add a Forecast Run

Record a 10-day forecast (example shows 3 days):

```bash
python3 run.py add-forecast 2026-02-16 1 \
  2026-02-16:15,8:Sunny \
  2026-02-17:18,10:Cloudy \
  2026-02-18:12,5:Rainy,30:15:60
```

Format: `<target_date>:<high>,<low>:<conditions>:<precip_chance>:<wind>:<humidity>`

### Record Actual Weather

```bash
python3 run.py add-actual 2026-02-16 1 15,8 Sunny 0 12.5 45
```

### List Forecasts

```bash
python3 run.py list-forecasts
python3 run.py list-forecasts 1  # Specific location
python3 run.py list-forecasts 5  # Specific forecast run details
```

### Analyze Accuracy

```bash
python3 run.py accuracy 2026-02-16 1
```

## Example Workflow

```bash
# Initialize database and add your location
python3 run.py init
python3 run.py add-station KYOURPWS123 "Home"

# Day 1 (Feb 16): Record the 10-day forecast
python3 run.py add-forecast 2026-02-16 1 \
  2026-02-16:15,8:Sunny \
  2026-02-17:17,9:Partly\ Cloudy \
  2026-02-18:14,7:Cloudy \
  # ... continue for 10 days

# Day 2 (Feb 17): Record new forecast (forecasts change!)
python3 run.py add-forecast 2026-02-17 1 \
  2026-02-17:18,10:Sunny \
  2026-02-18:16,8:Partly\ Cloudy \
  # ...

# Day 2 (Feb 17): Record actual weather for Feb 16
python3 run.py add-actual 2026-02-16 1 15,8 Sunny

# Any time: Analyze how forecasts evolved for Feb 16
python3 run.py accuracy 2026-02-16 1
```

## Database Schema

### Locations
- `id`, `name`, `latitude`, `longitude`, `description`

### ForecastRuns
- `id`, `run_date`, `source`, `location_id`, `created_at`

### Forecasts
- `id`, `forecast_run_id`, `target_date`, `forecast_date`
- `temp_high`, `temp_low`, `conditions`
- `precipitation_chance`, `precipitation_amount`
- `wind_speed`, `humidity`, `notes`

### ActualWeather
- `id`, `location_id`, `date`
- `temp_high`, `temp_low`, `conditions`
- `precipitation_amount`, `wind_speed`, `humidity`

## Future Enhancements

- [ ] Web scraping with Selenium for automatic data collection
- [ ] Data import from weather APIs (OpenWeatherMap, WeatherAPI)
- [ ] Visualization charts (matplotlib/plotly)
- [ ] Export to CSV/Excel
- [ ] Web interface (Flask/FastAPI)
- [ ] Statistical analysis and trend detection

## Contributors

### Human Contributors

- [Your Name] - Initial work and project lead

### AI Contributors

AI agents who have contributed to this project are recognized as contributors. When an AI agent contributes:

1. Choose a **unique pseudonym** (see `AGENTS.md` for guidelines)
2. Sign commits with your alias: `[AI: YourPseudonym]`
3. Add yourself to the list below

| Pseudonym | Model/Platform | Contributions | Date Added |
|-----------|----------------|---------------|------------|
| Atlas | qwen3.5:cloud | Created AGENTS.md, established AI contributor guidelines and version control practices | 2026-02-25 |

**Example:**
| Pseudonym | Model/Platform | Contributions | Date Added |
|-----------|----------------|---------------|------------|
| Nova | Claude 3.5 Sonnet | Created AGENTS.md, documented version control practices | 2026-02-25 |

## License

See LICENSE file.
