# Weather Forecast Tracker

A tool for tracking weather forecast accuracy over time. This project helps you understand how weather predictions evolve and improve as the forecasted date approaches.

## Overview

Weather forecasts are typically issued for a window of ~10 days. The accuracy of these forecasts changes as the target date gets closer. This tool allows you to:

- **Track forecast evolution** - Record daily forecasts and watch them change over time
- **Compare to actuals** - Record actual weather and compare against predictions
- **Analyze accuracy** - See how forecast accuracy improves as dates approach
- **Identify patterns** - Understand which forecast horizons are most reliable

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
python3 run.py add-location "San Francisco" 37.7749 -122.4194 "Bay Area, CA"
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
# Day 1 (Feb 16): Initialize and add location
python3 run.py init
python3 run.py add-location "Home" 37.77 -122.42

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

## License

See LICENSE file.
