"""
Weather data service - handles data entry and retrieval.
"""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from models.models import Location, ForecastRun, Forecast, ActualWeather


class WeatherService:
    """Service for managing weather forecast and actual data."""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Location Management ====================

    def create_location(self, name: str, latitude: float = None,
                        longitude: float = None, description: str = None) -> Location:
        """Create a new location for weather tracking."""
        location = Location(
            name=name,
            latitude=latitude,
            longitude=longitude,
            description=description
        )
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def get_location(self, location_id: int) -> Optional[Location]:
        """Get a location by ID."""
        return self.db.query(Location).filter(Location.id == location_id).first()

    def get_location_by_name(self, name: str) -> Optional[Location]:
        """Get a location by name."""
        return self.db.query(Location).filter(Location.name == name).first()

    def list_locations(self) -> List[Location]:
        """List all locations."""
        return self.db.query(Location).all()

    # ==================== Forecast Management ====================

    def create_forecast_run(self, run_date: date, location_id: int,
                            source: str = "manual") -> ForecastRun:
        """Create a new forecast run (e.g., the 10-day forecast published on a specific date)."""
        forecast_run = ForecastRun(
            run_date=run_date,
            location_id=location_id,
            source=source
        )
        self.db.add(forecast_run)
        self.db.commit()
        self.db.refresh(forecast_run)
        return forecast_run

    def add_forecast(self, forecast_run_id: int, target_date: date,
                     temp_high: float = None, temp_low: float = None,
                     conditions: str = None, precipitation_chance: int = None,
                     precipitation_amount: float = None,
                     wind_speed: float = None, humidity: int = None,
                     notes: str = None) -> Forecast:
        """Add a daily forecast to a forecast run."""
        forecast_run = self.db.query(ForecastRun).filter(
            ForecastRun.id == forecast_run_id
        ).first()

        if not forecast_run:
            raise ValueError(f"Forecast run {forecast_run_id} not found")

        forecast = Forecast(
            forecast_run_id=forecast_run_id,
            target_date=target_date,
            forecast_date=forecast_run.run_date,
            temp_high=temp_high,
            temp_low=temp_low,
            conditions=conditions,
            precipitation_chance=precipitation_chance,
            precipitation_amount=precipitation_amount,
            wind_speed=wind_speed,
            humidity=humidity,
            notes=notes
        )
        self.db.add(forecast)
        self.db.commit()
        self.db.refresh(forecast)
        return forecast

    def get_forecast_run(self, forecast_run_id: int) -> Optional[ForecastRun]:
        """Get a forecast run by ID with its daily forecasts."""
        return self.db.query(ForecastRun).filter(
            ForecastRun.id == forecast_run_id
        ).first()

    def get_forecasts_for_run(self, forecast_run_id: int) -> List[Forecast]:
        """Get all daily forecasts in a forecast run."""
        return self.db.query(Forecast).filter(
            Forecast.forecast_run_id == forecast_run_id
        ).order_by(Forecast.target_date).all()

    def list_forecast_runs(self, location_id: int = None) -> List[ForecastRun]:
        """List all forecast runs, optionally filtered by location."""
        query = self.db.query(ForecastRun)
        if location_id:
            query = query.filter(ForecastRun.location_id == location_id)
        return query.order_by(ForecastRun.run_date.desc()).all()

    def get_forecast_evolution(self, location_id: int, target_date: date) -> List[Forecast]:
        """
        Get all forecasts made for a specific target date.
        This shows how the forecast evolved over time.
        """
        return self.db.query(Forecast).join(ForecastRun).filter(
            Forecast.target_date == target_date,
            ForecastRun.location_id == location_id
        ).order_by(Forecast.forecast_date).all()

    def get_forecast_evolution(self, location_id: int, target_date: date) -> List[Forecast]:
        """
        Get all forecasts made for a specific target date.
        This shows how the forecast evolved over time.
        """
        return self.db.query(Forecast).join(ForecastRun).filter(
            Forecast.target_date == target_date,
            ForecastRun.location_id == location_id
        ).order_by(Forecast.forecast_date).all()

    # ==================== Actual Weather Management ====================

    def add_actual_weather(self, location_id: int, date: date,
                           temp_high: float = None, temp_low: float = None,
                           conditions: str = None, precipitation_amount: float = None,
                           wind_speed: float = None, humidity: int = None,
                           notes: str = None) -> ActualWeather:
        """Record the actual weather that occurred on a specific date."""
        actual = ActualWeather(
            location_id=location_id,
            date=date,
            temp_high=temp_high,
            temp_low=temp_low,
            conditions=conditions,
            precipitation_amount=precipitation_amount,
            wind_speed=wind_speed,
            humidity=humidity,
            notes=notes
        )
        self.db.add(actual)
        self.db.commit()
        self.db.refresh(actual)
        return actual

    def get_actual_weather(self, location_id: int, date: date) -> Optional[ActualWeather]:
        """Get actual weather for a specific location and date."""
        return self.db.query(ActualWeather).filter(
            ActualWeather.location_id == location_id,
            ActualWeather.date == date
        ).first()

    def list_actual_weather(self, location_id: int = None) -> List[ActualWeather]:
        """List all actual weather records, optionally filtered by location."""
        query = self.db.query(ActualWeather)
        if location_id:
            query = query.filter(ActualWeather.location_id == location_id)
        return query.order_by(ActualWeather.date.desc()).all()
