"""
Forecast accuracy analysis utilities.
"""
from datetime import date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from models.models import Forecast, ActualWeather, ForecastRun
from services.weather_service import WeatherService


@dataclass
class ForecastAccuracy:
    """Represents the accuracy of a single forecast compared to actual weather."""
    target_date: date
    forecast_date: date
    days_before: int  # How many days before the target date was this forecast made

    # Temperature accuracy
    forecast_high: Optional[float]
    actual_high: Optional[float]
    high_error: Optional[float]  # forecast - actual

    forecast_low: Optional[float]
    actual_low: Optional[float]
    low_error: Optional[float]  # forecast - actual

    # Conditions match
    forecast_conditions: Optional[str]
    actual_conditions: Optional[str]
    conditions_match: Optional[bool]

    @property
    def high_error_abs(self) -> Optional[float]:
        """Absolute error for high temperature."""
        return abs(self.high_error) if self.high_error is not None else None

    @property
    def low_error_abs(self) -> Optional[float]:
        """Absolute error for low temperature."""
        return abs(self.low_error) if self.low_error is not None else None


class AccuracyAnalyzer:
    """Analyze forecast accuracy over time."""

    def __init__(self, db: Session):
        self.db = db
        self.weather_service = WeatherService(db)

    def analyze_target_date(self, location_id: int, target_date: date) -> List[ForecastAccuracy]:
        """
        Analyze all forecasts made for a specific target date.
        Shows how forecast accuracy changed as the date approached.
        """
        actual = self.weather_service.get_actual_weather(location_id, target_date)
        forecasts = self.weather_service.get_forecast_evolution(location_id, target_date)

        accuracies = []
        for forecast in forecasts:
            days_before = (target_date - forecast.forecast_date).days

            high_error = None
            if forecast.temp_high is not None and actual and actual.temp_high is not None:
                high_error = forecast.temp_high - actual.temp_high

            low_error = None
            if forecast.temp_low is not None and actual and actual.temp_low is not None:
                low_error = forecast.temp_low - actual.temp_low

            conditions_match = None
            if forecast.conditions and actual and actual.conditions:
                conditions_match = forecast.conditions.lower() == actual.conditions.lower()

            accuracy = ForecastAccuracy(
                target_date=target_date,
                forecast_date=forecast.forecast_date,
                days_before=days_before,
                forecast_high=forecast.temp_high,
                actual_high=actual.temp_high if actual else None,
                high_error=high_error,
                forecast_low=forecast.temp_low,
                actual_low=actual.temp_low if actual else None,
                low_error=low_error,
                forecast_conditions=forecast.conditions,
                actual_conditions=actual.conditions if actual else None,
                conditions_match=conditions_match
            )
            accuracies.append(accuracy)

        return accuracies

    def analyze_forecast_run(self, forecast_run_id: int) -> Dict:
        """
        Analyze accuracy of all forecasts in a specific forecast run.
        Only includes dates that have already passed (have actual data).
        """
        forecast_run = self.weather_service.get_forecast_run(forecast_run_id)
        if not forecast_run:
            return {"error": "Forecast run not found"}

        forecasts = self.weather_service.get_forecasts_for_run(forecast_run_id)
        today = date.today()

        results = {
            "forecast_run_id": forecast_run_id,
            "run_date": forecast_run.run_date,
            "location_id": forecast_run.location_id,
            "forecasts_analyzed": 0,
            "temp_high_errors": [],
            "temp_low_errors": [],
            "conditions_correct": 0,
            "conditions_total": 0
        }

        for forecast in forecasts:
            # Only analyze dates that have passed
            if forecast.target_date >= today:
                continue

            actual = self.weather_service.get_actual_weather(
                forecast_run.location_id, forecast.target_date
            )

            if not actual:
                continue

            results["forecasts_analyzed"] += 1

            if forecast.temp_high is not None and actual.temp_high is not None:
                error = abs(forecast.temp_high - actual.temp_high)
                results["temp_high_errors"].append(error)

            if forecast.temp_low is not None and actual.temp_low is not None:
                error = abs(forecast.temp_low - actual.temp_low)
                results["temp_low_errors"].append(error)

            if forecast.conditions and actual.conditions:
                results["conditions_total"] += 1
                if forecast.conditions.lower() == actual.conditions.lower():
                    results["conditions_correct"] += 1

        # Calculate averages
        if results["temp_high_errors"]:
            results["avg_high_error"] = sum(results["temp_high_errors"]) / len(results["temp_high_errors"])
        if results["temp_low_errors"]:
            results["avg_low_error"] = sum(results["temp_low_errors"]) / len(results["temp_low_errors"])
        if results["conditions_total"]:
            results["conditions_accuracy"] = results["conditions_correct"] / results["conditions_total"]

        return results

    def print_accuracy_report(self, location_id: int, target_date: date):
        """Print a human-readable accuracy report for a specific target date."""
        accuracies = self.analyze_target_date(location_id, target_date)

        if not accuracies:
            print(f"No forecasts found for target date {target_date}")
            return

        actual = self.weather_service.get_actual_weather(location_id, target_date)
        print(f"\n{'='*60}")
        print(f"Forecast Accuracy Report for {target_date}")
        print(f"{'='*60}")

        if actual:
            print(f"\nActual Weather:")
            print(f"  High: {actual.temp_high}°  |  Low: {actual.temp_low}°")
            print(f"  Conditions: {actual.conditions}")
        else:
            print(f"\n⚠️  No actual weather recorded for this date")

        print(f"\n{'Forecast Date':<15} {'Days Before':>12} {'High':>8} {'Low':>8} {'Conditions':>20}")
        print(f"{'-'*60}")

        for acc in accuracies:
            high_str = f"{acc.forecast_high:.0f}°" if acc.forecast_high else "N/A"
            low_str = f"{acc.forecast_low:.0f}°" if acc.forecast_low else "N/A"
            cond_str = acc.forecast_conditions or "N/A"

            # Add error indicator
            if acc.high_error is not None:
                error_sign = "+" if acc.high_error > 0 else ""
                high_str += f" ({error_sign}{acc.high_error:.0f})"

            print(f"{str(acc.forecast_date):<15} {acc.days_before:>12} {high_str:>8} {low_str:>8} {cond_str:>20}")

        print(f"{'='*60}\n")
