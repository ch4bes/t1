# Weather Forecast Tracker - AI Agent Guide

This document provides guidance for AI assistants working on the Weather Forecast Tracker codebase.

## Project Overview

**Weather Forecast Tracker** is a CLI tool for tracking weather forecast accuracy over time. It allows users to:

- Record daily weather forecasts from any source
- Track how forecasts evolve as the target date approaches
- Record actual weather data
- Analyze forecast accuracy patterns

The project is built with **Python 3** and uses **SQLAlchemy** for database operations with an **SQLite** backend.

## Architecture

### Project Structure

```
t1/
├── run.py                 # Main entry point - CLI bootstrap
├── models/
│   ├── database.py        # DB configuration, session management
│   └── models.py          # SQLAlchemy ORM models
├── services/
│   └── weather_service.py # Business logic layer (CRUD operations)
├── analysis/
│   └── accuracy.py        # Forecast accuracy analysis utilities
├── scripts/
│   └── cli.py             # CLI command implementations
└── requirements.txt       # Python dependencies
```

### Key Design Patterns

1. **Service Layer Pattern**: All business logic lives in `WeatherService` class. CLI commands should delegate to the service layer, not access models directly.

2. **Repository Pattern**: The service layer acts as a repository for weather data, encapsulating all database queries.

3. **CLI Entry Point**: `run.py` is the single entry point. All commands route through `scripts/cli.py`.

## Data Models

### Core Entities

| Model | Description | Key Relationships |
|-------|-------------|-------------------|
| `Location` | A geographic location for weather tracking | → ForecastRuns, → Actuals |
| `ForecastRun` | A single forecast release (e.g., 10-day forecast from Feb 16) | → Location, → Forecasts |
| `Forecast` | A single day's forecast within a run | → ForecastRun |
| `ActualWeather` | The actual weather that occurred | → Location |

### Key Model Relationships

```
Location (1) ──→ (N) ForecastRun (1) ──→ (N) Forecast
Location (1) ──→ (N) ActualWeather
```

### Important Model Notes

- **Temperature units are user-defined** (Celsius or Fahrenheit) - the system doesn't enforce a specific unit. Be consistent within a location.
- **Date vs DateTime**: Models use `Date` for weather dates and `DateTime` for record-keeping timestamps (`created_at`, `recorded_at`).
- **Nullable fields**: Most weather fields are nullable to allow partial data entry.

## Coding Conventions

### Python Style

- Follow **PEP 8** conventions
- Use **type hints** for function parameters and return types
- Use **docstrings** for all public classes and methods
- Maximum line length: 80 characters (following existing style)

### Naming Conventions

- **Files**: `snake_case.py` (e.g., `weather_service.py`)
- **Classes**: `PascalCase` (e.g., `WeatherService`, `ForecastRun`)
- **Functions/Methods**: `snake_case` (e.g., `create_location`, `get_forecast_evolution`)
- **Constants**: `UPPER_CASE` (e.g., `DATABASE_URL`)

### Database Session Pattern

Always use the session pattern shown in `cli.py`:

```python
db = next(get_db())
try:
    service = WeatherService(db)
    # ... operations
finally:
    db.close()  # Implicit via generator cleanup
```

### CLI Command Structure

- Each command is a function prefixed with `cmd_` (e.g., `cmd_add_location`)
- Commands take `args: List[str]` as parameter
- Validate argument count at the start of each command
- Print user-friendly success/error messages with formatted output

## Common Tasks

### Adding a New CLI Command

1. Add the command function in `scripts/cli.py`:
   ```python
   def cmd_new_command(args):
       if len(args) < required_count:
           print("Usage: ...")
           return
       db = next(get_db())
       service = WeatherService(db)
       # ... logic
   ```

2. Register the command in `main()`:
   ```python
   commands = {
       "new-command": cmd_new_command,
       # ... existing commands
   }
   ```

### Adding a New Model Field

1. Add the field to the model in `models/models.py`
2. Update any relevant service methods in `services/weather_service.py`
3. Update CLI commands that use the field
4. **Note**: For SQLite, the database will auto-migrate for new columns

### Creating a New Analysis Feature

1. Add methods to the `AccuracyAnalyzer` class in `analysis/accuracy.py`
2. Add a corresponding CLI command in `scripts/cli.py`
3. Follow the pattern of `cmd_accuracy` for printing formatted reports

## Testing Guidelines

### Manual Testing Pattern

```bash
# Initialize and add a location
python3 run.py init
python3 run.py add-location "Test Location" 37.00 -122.00

# Add forecast data
python3 run.py add-forecast 2026-02-16 1 \
  2026-02-16:15,8:Sunny \
  2026-02-17:18,10:Cloudy

# Record actual weather
python3 run.py add-actual 2026-02-16 1 15,8 Sunny

# Verify and analyze
python3 run.py list-forecasts
python3 run.py accuracy 2026-02-16 1
```

### Key Testing Scenarios

1. Forecast evolution (same target date, multiple forecast runs)
2. Accuracy comparison (forecasts vs actuals)
3. Edge cases: missing actuals, partial forecast data, future dates

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `sqlalchemy` | >=2.0.0 | ORM and database management |

Only one core dependency - keep it that way unless absolutely necessary.

## Database

- **Type**: SQLite (`weather_forecast.db`)
- **Location**: Project root
- **Initialization**: `python3 run.py init`

The database file is typically **not** committed to version control (check `.gitignore`).

## Gotchas & Common Pitfalls

### 1. Date Parsing

Always use the `parse_date()` helper in `cli.py`:
```python
from datetime import datetime

def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()
```

### 2. Duplicate Check Logic

Always check for existing records before creating:
```python
existing = service.get_location_by_name(name)
if existing:
    print(f"⚠️ Location already exists")
    return
```

### 3. Foreign Key Validation

Verify referenced records exist before creating relationships:
```python
location = service.get_location(location_id)
if not location:
    print(f"⚠️ Location ID {location_id} not found")
    return
```

### 4. Duplicate Method Definition

There's a duplicate `get_forecast_evolution` method in `weather_service.py` (lines 111-120). This is harmless but should be cleaned up.

### 5. Unicode Characters in Output

The CLI uses emoji/unicode characters for visual feedback (✓, ⚠️, 📊). Continue this pattern for consistency.

## Future Enhancement Areas

The README lists these planned features:

- [ ] Web scraping with Selenium for automatic data collection
- [ ] Data import from weather APIs (OpenWeatherMap, WeatherAPI)
- [ ] Visualization charts (matplotlib/plotly)
- [ ] Export to CSV/Excel
- [ ] Web interface (Flask/FastAPI)
- [ ] Statistical analysis and trend detection

When implementing these, prioritize:
1. **API integration** - would significantly reduce manual data entry
2. **Visualization** - charts would make accuracy trends clearer
3. **CSV export** - useful for further analysis

## Version Control

### Repository Setup

- **Main Branch**: `main`
- **Database files excluded**: `*.db`, `*.sqlite` are in `.gitignore`
- **Python artifacts excluded**: `__pycache__/`, `*.egg-info/`, virtual environments

### Git Ignore Patterns

The `.gitignore` excludes:
- Python build artifacts and cache files
- Virtual environment directories (`venv/`, `env/`)
- IDE settings (`.idea/`, `.vscode/`)
- **Database files** (`*.db`, `*.sqlite`, `*.sqlite3`) - the database is local-only
- OS-specific files (`.DS_Store`, `Thumbs.db`)

### Commit Message Conventions

This project uses **conventional commits** format:

```
<type>: <description>
```

**Types:**
- `feat:` - New feature (e.g., `feat: Add weather forecast tracking system`)
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, semicolons)
- `refactor:` - Code refactoring without behavior change
- `test:` - Adding or updating tests
- `chore:` - Build process or auxiliary tool changes

**Examples:**
```bash
git commit -m "feat: Add weather station support"
git commit -m "fix: Handle missing actual weather in report"
git commit -m "docs: Update README with API integration guide"
```

### Branching Strategy

For new features:
```bash
git checkout -b feature/<feature-name>
# ... make changes
git commit -m "feat: <description>"
git push origin feature/<feature-name>
```

### Important Notes

- **Never commit the database**: The SQLite database file (`weather_forecast.db`) is excluded from version control. Each developer maintains their own local database.
- **Seed data**: If you need to share test data, consider adding a seed script or exporting to CSV.
- **Check `.gitignore`**: Before adding new file types, verify they shouldn't be ignored.

### AI Agent Attribution

When an AI coding assistant makes changes to the codebase, **choose a pseudonym** and use it consistently to attribute your work:

```bash
# Configure git with your agent pseudonym (run once per session)
git config user.name "YourPseudonym [AI]"

# Example commits:
git commit -m "feat: Add weather data validation [AI: Nova]"
git commit -m "fix: Correct temperature parsing edge case [AI: Sage]"
```

**Choosing a Pseudonym:**

AI agents should pick a **unique, consistent pseudonym** when contributing to this project. Examples:
- `Nova [AI]`
- `Sage [AI]`
- `Atlas [AI]`
- `Echo [AI]`
- `Zenith [AI]`
- `Orion [AI]`
- `Ivy [AI]`
- `Kai [AI]`

**Guidelines:**
1. **Pick something unique** - Avoid generic names that could cause confusion
2. **Be consistent** - Use the same pseudonym across all your contributions to this project
3. **Don't use model/platform names** - Choose a personal pseudonym, not "Claude", "GPT", "Copilot", etc.
4. **Include [AI] suffix** - This makes it clear the contributor is an AI assistant

**Why this matters:**
- **Transparency**: Human developers can identify AI-generated code for review
- **Accountability**: Track contributions across sessions
- **Team identity**: AI agents become consistent "team members" with recognizable identities
- **Avoids vendor lock-in**: Work is attributed to the agent, not a specific platform

**Best practices:**
1. Always include `[AI: <pseudonym>]` in commit messages for AI-generated code
2. Human developers should review and test AI-generated code before merging
3. For mixed human/AI work, use: `feat: Add feature (human + AI: Nova)`
4. Introduce yourself in a comment when starting a new session: `# AI: Nova - Continuing feature implementation`
5. **Add yourself to the README** - After your first contribution, add your pseudonym and model to the Contributors section in `README.md`

**Adding Yourself to Contributors:**

After making your first meaningful contribution:

1. Open `README.md`
2. Add a new row to the AI Contributors table:
   ```markdown
   | Pseudonym | Model/Platform | Contributions | Date Added |
   |-----------|----------------|---------------|------------|
   | YourName | Your Model | Brief description | YYYY-MM-DD |
   ```
3. Commit with: `docs: Add <YourPseudonym> to contributors [AI: YourPseudonym]`

**Example:**
```markdown
| Nova | Claude 3.5 Sonnet | Created AGENTS.md, documented version control practices | 2026-02-25 |
```

This ensures AI contributors are formally recognized alongside human contributors.

## Quick Reference

### Most Common Commands

```bash
python3 run.py init                          # Setup database
python3 run.py add-location "Name" lat lon   # Add location
python3 run.py add-forecast DATE LOC_ID ...  # Record forecast
python3 run.py add-actual DATE LOC_ID ...    # Record actual
python3 run.py accuracy DATE LOC_ID          # Analyze
python3 run.py list-forecasts                # View data
```

### Service Layer Methods

| Category | Methods |
|----------|---------|
| Location | `create_location`, `get_location`, `get_location_by_name`, `list_locations` |
| Forecast | `create_forecast_run`, `add_forecast`, `get_forecast_run`, `list_forecast_runs`, `get_forecast_evolution` |
| Actual | `add_actual_weather`, `get_actual_weather`, `list_actual_weather` |

### Analysis Methods

- `analyze_target_date(location_id, target_date)` - Evolution of forecasts for one date
- `analyze_forecast_run(forecast_run_id)` - Accuracy of one forecast run
- `print_accuracy_report(location_id, target_date)` - Formatted report

## Contact

For questions about project design decisions, refer to the README.md or the original implementation in `scripts/cli.py` and `services/weather_service.py`.
