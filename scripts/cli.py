"""
Command-line interface for weather forecast tracking.
Usage:
    python scripts/cli.py <command> [options]

Commands:
    init                    Initialize the database
    add-location            Add a new location
    list-locations          List all locations
    add-forecast            Add a forecast run with daily forecasts
    list-forecasts          List forecast runs
    add-actual              Record actual weather for a date
    list-actual             List actual weather records
    accuracy                Analyze forecast accuracy for a date
"""
import sys
from datetime import date, datetime
from typing import Optional

from models.database import init_db, get_db
from services.weather_service import WeatherService
from analysis.accuracy import AccuracyAnalyzer


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


def cmd_init(args):
    """Initialize the database."""
    print_header("Initializing Database")
    init_db()
    print("✓ Database initialized successfully!")
    print("  Database file: weather_forecast.db")


def cmd_add_location(args):
    """Add a new location."""
    if len(args) < 1:
        print("Usage: python scripts/cli.py add-location <name> [latitude] [longitude] [description]")
        return

    name = args[0]
    latitude = float(args[1]) if len(args) > 1 else None
    longitude = float(args[2]) if len(args) > 2 else None
    description = args[3] if len(args) > 3 else None

    db = next(get_db())
    service = WeatherService(db)

    # Check if location already exists
    existing = service.get_location_by_name(name)
    if existing:
        print(f"⚠️  Location '{name}' already exists (ID: {existing.id})")
        return

    location = service.create_location(name, latitude, longitude, description)
    print(f"✓ Location created successfully!")
    print(f"  ID: {location.id}")
    print(f"  Name: {location.name}")
    if location.latitude:
        print(f"  Coordinates: {location.latitude}, {location.longitude}")


def cmd_list_locations(args):
    """List all locations."""
    print_header("Locations")
    db = next(get_db())
    service = WeatherService(db)

    locations = service.list_locations()
    if not locations:
        print("No locations found.")
        print("\nAdd a location with: python scripts/cli.py add-location <name> [lat] [lon] [description]")
        return

    print(f"{'ID':<6} {'Name':<25} {'Coordinates':<25}")
    print("-" * 60)
    for loc in locations:
        coords = f"{loc.latitude}, {loc.longitude}" if loc.latitude else "N/A"
        print(f"{loc.id:<6} {loc.name:<25} {coords:<25}")


def cmd_add_forecast(args):
    """Add a forecast run with daily forecasts."""
    if len(args) < 3:
        print("""
Usage: python3 run.py add-forecast <run_date> <location_id> <target_dates_and_data>

Example:
  Add a 3-day forecast:
  python3 run.py add-forecast 2026-02-16 1 2026-02-16:15,8:Sunny 2026-02-17:18,10:Cloudy 2026-02-18:12,5:Rainy

  Format for each day: <target_date>:<high>,<low>:<conditions>
  Optional: :<precip_chance>:<wind>:<humidity>

Tips:
  - Use underscores for multi-word conditions: Partly_Cloudy, Heavy_Rain
  - Or quote your arguments: "2026-02-17:18,10:Partly Cloudy"
""")
        return

    run_date = parse_date(args[0])
    location_id = int(args[1])
    forecast_data = args[2:]

    db = next(get_db())
    service = WeatherService(db)

    # Verify location exists
    location = service.get_location(location_id)
    if not location:
        print(f"⚠️  Location ID {location_id} not found.")
        return

    # Create forecast run
    forecast_run = service.create_forecast_run(run_date, location_id)
    print(f"✓ Created forecast run for {run_date} (ID: {forecast_run.id})")

    # Parse and add daily forecasts
    for data in forecast_data:
        parts = data.split(":")
        if len(parts) < 2:
            print(f"⚠️  Invalid forecast data: {data}")
            continue

        target_date = parse_date(parts[0])
        temps = parts[1].split(",")
        temp_high = float(temps[0]) if temps[0] else None
        temp_low = float(temps[1]) if len(temps) > 1 and temps[1] else None

        conditions = parts[2] if len(parts) > 2 else None
        # Convert underscores to spaces for display
        if conditions:
            conditions = conditions.replace("_", " ")
        
        precip_chance = int(parts[3]) if len(parts) > 3 and parts[3] else None
        wind_speed = float(parts[4]) if len(parts) > 4 and parts[4] else None
        humidity = int(parts[5]) if len(parts) > 5 and parts[5] else None

        forecast = service.add_forecast(
            forecast_run_id=forecast_run.id,
            target_date=target_date,
            temp_high=temp_high,
            temp_low=temp_low,
            conditions=conditions,
            precipitation_chance=precip_chance,
            wind_speed=wind_speed,
            humidity=humidity
        )
        print(f"  Added forecast for {target_date}: High {temp_high}°, Low {temp_low}° - {conditions}")


def cmd_list_forecasts(args):
    """List forecast runs."""
    print_header("Forecast Runs")
    db = next(get_db())
    service = WeatherService(db)

    location_id = int(args[0]) if args else None
    runs = service.list_forecast_runs(location_id)

    if not runs:
        print("No forecast runs found.")
        return

    print(f"{'ID':<6} {'Date':<12} {'Location':<20} {'Source':<15} {'Forecasts':<10}")
    print("-" * 65)
    for run in runs:
        location_name = run.location.name if run.location else "Unknown"
        forecast_count = len(run.daily_forecasts)
        print(f"{run.id:<6} {str(run.run_date):<12} {location_name:<20} {run.source:<15} {forecast_count:<10}")

    # Show detailed view for specific run if ID provided
    if args and len(args) > 0 and args[0].isdigit():
        run_id = int(args[0])
        run = service.get_forecast_run(run_id)
        if run:
            print(f"\n\nForecasts in run #{run_id}:")
            print(f"{'Target Date':<15} {'High':>8} {'Low':>8} {'Conditions':<20}")
            print("-" * 55)
            for fc in run.daily_forecasts:
                high_str = f"{fc.temp_high}°" if fc.temp_high else "N/A"
                low_str = f"{fc.temp_low}°" if fc.temp_low else "N/A"
                cond_str = fc.conditions or "N/A"
                print(f"{str(fc.target_date):<15} {high_str:>8} {low_str:>8} {cond_str:<20}")


def cmd_add_actual(args):
    """Record actual weather for a date."""
    if len(args) < 3:
        print("""
Usage: python scripts/cli.py add-actual <date> <location_id> <high>,<low> [conditions] [precip] [wind] [humidity]

Example:
  python scripts/cli.py add-actual 2026-02-16 1 15,8 Sunny 0 12.5 45
""")
        return

    date_val = parse_date(args[0])
    location_id = int(args[1])
    temps = args[2].split(",")
    temp_high = float(temps[0]) if temps[0] else None
    temp_low = float(temps[1]) if len(temps) > 1 and temps[1] else None

    conditions = args[3] if len(args) > 3 else None
    precipitation = float(args[4]) if len(args) > 4 and args[4] else None
    wind_speed = float(args[5]) if len(args) > 5 and args[5] else None
    humidity = int(args[6]) if len(args) > 6 and args[6] else None

    db = next(get_db())
    service = WeatherService(db)

    # Verify location exists
    location = service.get_location(location_id)
    if not location:
        print(f"⚠️  Location ID {location_id} not found.")
        return

    # Check if actual already exists
    existing = service.get_actual_weather(location_id, date_val)
    if existing:
        print(f"⚠️  Actual weather already recorded for {date_val} at location {location_id}")
        print("  Use update functionality (coming soon) or delete and re-add.")
        return

    actual = service.add_actual_weather(
        location_id=location_id,
        date=date_val,
        temp_high=temp_high,
        temp_low=temp_low,
        conditions=conditions,
        precipitation_amount=precipitation,
        wind_speed=wind_speed,
        humidity=humidity
    )
    print(f"✓ Actual weather recorded for {date_val}")
    print(f"  High: {temp_high}°  |  Low: {temp_low}°  |  Conditions: {conditions}")


def cmd_list_actual(args):
    """List actual weather records."""
    print_header("Actual Weather Records")
    db = next(get_db())
    service = WeatherService(db)

    location_id = int(args[0]) if args else None
    records = service.list_actual_weather(location_id)

    if not records:
        print("No actual weather records found.")
        return

    print(f"{'ID':<6} {'Date':<12} {'Location':<15} {'High':>8} {'Low':>8} {'Conditions':<20}")
    print("-" * 75)
    for rec in records:
        location_name = rec.location.name if rec.location else "Unknown"
        high_str = f"{rec.temp_high}°" if rec.temp_high else "N/A"
        low_str = f"{rec.temp_low}°" if rec.temp_low else "N/A"
        cond_str = rec.conditions or "N/A"
        print(f"{rec.id:<6} {str(rec.date):<12} {location_name:<15} {high_str:>8} {low_str:>8} {cond_str:<20}")


def cmd_accuracy(args):
    """Analyze forecast accuracy for a specific date."""
    if len(args) < 2:
        print("Usage: python scripts/cli.py accuracy <date> <location_id>")
        print("Example: python scripts/cli.py accuracy 2026-02-16 1")
        return

    target_date = parse_date(args[0])
    location_id = int(args[1])

    db = next(get_db())
    analyzer = AccuracyAnalyzer(db)
    analyzer.print_accuracy_report(location_id, target_date)


def main():
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "init": cmd_init,
        "add-location": cmd_add_location,
        "list-locations": cmd_list_locations,
        "add-forecast": cmd_add_forecast,
        "list-forecasts": cmd_list_forecasts,
        "add-actual": cmd_add_actual,
        "list-actual": cmd_list_actual,
        "accuracy": cmd_accuracy,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print("\nAvailable commands:")
        for cmd in commands.keys():
            print(f"  {cmd}")
        return

    commands[command](args)


if __name__ == "__main__":
    main()
