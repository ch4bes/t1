"""
Database models for weather forecast tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from models.database import Base


class Location(Base):
    """A location where weather is tracked."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    forecast_runs = relationship("ForecastRun", back_populates="location", cascade="all, delete-orphan")
    actuals = relationship("ActualWeather", back_populates="location", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Location(name='{self.name}')>"


class ForecastRun(Base):
    """
    A forecast run represents a single forecast release from a weather source.
    For example, the 10-day forecast published on Feb 16, 2026.
    """
    __tablename__ = "forecast_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_date = Column(Date, nullable=False, index=True)
    source = Column(String, nullable=False, default="manual")
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="forecast_runs")
    daily_forecasts = relationship("Forecast", back_populates="forecast_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ForecastRun(run_date={self.run_date}, location_id={self.location_id})>"


class Forecast(Base):
    """
    A single day's forecast within a forecast run.
    Tracks what was predicted for a target date, made on a specific forecast date.
    """
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id"), nullable=False)
    target_date = Column(Date, nullable=False, index=True)  # The day being forecast
    forecast_date = Column(Date, nullable=False, index=True)  # When the forecast was made

    # Temperature (in Celsius or Fahrenheit - user's choice)
    temp_high = Column(Float, nullable=True)
    temp_low = Column(Float, nullable=True)

    # Weather conditions
    conditions = Column(String, nullable=True)  # e.g., "Sunny", "Rainy", "Partly Cloudy"
    precipitation_chance = Column(Integer, nullable=True)  # 0-100%
    precipitation_amount = Column(Float, nullable=True)  # mm or inches

    # Additional fields
    wind_speed = Column(Float, nullable=True)
    humidity = Column(Integer, nullable=True)  # 0-100%
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    forecast_run = relationship("ForecastRun", back_populates="daily_forecasts")

    def __repr__(self):
        return f"<Forecast(target_date={self.target_date}, forecast_date={self.forecast_date})>"


class ActualWeather(Base):
    """
    The actual weather that occurred on a specific date.
    Used to compare against forecasts for accuracy analysis.
    """
    __tablename__ = "actual_weather"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Temperature
    temp_high = Column(Float, nullable=True)
    temp_low = Column(Float, nullable=True)

    # Weather conditions
    conditions = Column(String, nullable=True)
    precipitation_amount = Column(Float, nullable=True)

    # Additional fields
    wind_speed = Column(Float, nullable=True)
    humidity = Column(Integer, nullable=True)

    recorded_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    # Relationships
    location = relationship("Location", back_populates="actuals")

    def __repr__(self):
        return f"<ActualWeather(date={self.date}, location_id={self.location_id})>"
