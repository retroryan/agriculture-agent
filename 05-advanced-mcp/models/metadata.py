"""
Metadata and statistical models for weather data analysis.

These models support data aggregation, trend analysis, and
statistical summaries of weather information.
"""

from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum


class TrendDirection(str, Enum):
    """Direction of a weather trend."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VARIABLE = "variable"


class TrendSignificance(str, Enum):
    """Statistical significance of a trend."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    NONE = "none"


class ExtremeEventType(str, Enum):
    """Types of extreme weather events."""
    HEATWAVE = "heatwave"
    COLD_SNAP = "cold_snap"
    HEAVY_RAIN = "heavy_rain"
    DROUGHT = "drought"
    HIGH_WIND = "high_wind"
    FROST = "frost"
    HAIL = "hail"


class TemperatureStats(BaseModel):
    """Statistical analysis of temperature data."""
    mean: float = Field(..., description="Mean temperature")
    median: float = Field(..., description="Median temperature")
    std_dev: float = Field(..., description="Standard deviation")
    min: float = Field(..., description="Minimum temperature")
    max: float = Field(..., description="Maximum temperature")
    percentiles: Dict[int, float] = Field(
        default_factory=dict,
        description="Percentile values (e.g., {25: 15.2, 50: 18.5, 75: 22.1})"
    )
    
    # Agricultural specific
    growing_degree_days: Optional[float] = Field(
        None,
        description="Accumulated growing degree days"
    )
    frost_days: Optional[int] = Field(
        None,
        description="Number of days with frost"
    )
    heat_stress_days: Optional[int] = Field(
        None,
        description="Days exceeding heat stress threshold"
    )
    
    # Comfort metrics
    comfort_index: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Thermal comfort index (0-10)"
    )
    
    def get_percentile(self, p: int) -> Optional[float]:
        """Get specific percentile value."""
        return self.percentiles.get(p)
    
    def calculate_variability(self) -> float:
        """Calculate coefficient of variation."""
        if self.mean == 0:
            return 0
        return (self.std_dev / abs(self.mean)) * 100


class PrecipitationSummary(BaseModel):
    """Summary statistics for precipitation data."""
    total: float = Field(..., ge=0, description="Total precipitation in mm")
    days_with_rain: int = Field(..., ge=0, description="Number of days with measurable precipitation")
    days_without_rain: int = Field(..., ge=0, description="Number of dry days")
    max_daily: float = Field(..., ge=0, description="Maximum daily precipitation")
    max_hourly: Optional[float] = Field(None, ge=0, description="Maximum hourly precipitation if available")
    
    # Distribution
    light_rain_days: Optional[int] = Field(None, description="Days with 0.1-2.5mm")
    moderate_rain_days: Optional[int] = Field(None, description="Days with 2.5-10mm")
    heavy_rain_days: Optional[int] = Field(None, description="Days with >10mm")
    
    # Agricultural metrics
    effective_rainfall: Optional[float] = Field(
        None,
        description="Rainfall available for crop use"
    )
    runoff_estimate: Optional[float] = Field(
        None,
        description="Estimated runoff in mm"
    )
    
    def average_daily(self, total_days: int) -> float:
        """Calculate average daily precipitation."""
        return self.total / total_days if total_days > 0 else 0
    
    def rain_frequency(self) -> float:
        """Calculate rain frequency as percentage."""
        total_days = self.days_with_rain + self.days_without_rain
        return (self.days_with_rain / total_days * 100) if total_days > 0 else 0


class ExtremeEvent(BaseModel):
    """Record of an extreme weather event."""
    event_type: ExtremeEventType
    start_date: datetime
    end_date: Optional[datetime] = None
    severity: TrendSignificance = Field(default=TrendSignificance.MODERATE)
    description: str = Field(..., description="Human-readable description")
    
    # Event-specific metrics
    peak_value: Optional[float] = Field(None, description="Peak value during event")
    threshold_exceeded: Optional[float] = Field(None, description="Threshold that was exceeded")
    affected_parameters: List[str] = Field(default_factory=list)
    
    # Impacts
    estimated_impact: Optional[str] = Field(None, description="Estimated agricultural impact")
    recovery_time_days: Optional[int] = Field(None, description="Expected recovery time")
    
    def duration_days(self) -> Optional[float]:
        """Calculate event duration in days."""
        if self.end_date:
            return (self.end_date - self.start_date).total_seconds() / 86400
        return None
    
    def is_ongoing(self) -> bool:
        """Check if event is still ongoing."""
        return self.end_date is None


class Trend(BaseModel):
    """Weather parameter trend analysis."""
    parameter: str = Field(..., description="Weather parameter being analyzed")
    direction: TrendDirection
    significance: TrendSignificance
    change_rate: float = Field(..., description="Rate of change per time unit")
    change_unit: str = Field(..., description="Unit of change (e.g., '°C/decade', 'mm/year')")
    
    # Statistical measures
    r_squared: Optional[float] = Field(None, ge=0, le=1, description="Coefficient of determination")
    p_value: Optional[float] = Field(None, ge=0, le=1, description="Statistical p-value")
    confidence_interval: Optional[tuple[float, float]] = Field(None)
    
    # Context
    period_start: date
    period_end: date
    data_points: int = Field(..., ge=2, description="Number of data points analyzed")
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if trend is statistically significant."""
        if self.p_value is not None:
            return self.p_value < alpha
        return self.significance in [TrendSignificance.HIGH, TrendSignificance.MODERATE]
    
    def format_description(self) -> str:
        """Generate human-readable trend description."""
        direction_text = {
            TrendDirection.INCREASING: "increasing",
            TrendDirection.DECREASING: "decreasing",
            TrendDirection.STABLE: "stable",
            TrendDirection.VARIABLE: "variable"
        }
        
        return (
            f"{self.parameter} is {direction_text[self.direction]} "
            f"at {abs(self.change_rate):.2f} {self.change_unit}"
        )


class WeatherAggregations(BaseModel):
    """
    Comprehensive weather data aggregations and statistics.
    
    This model provides a complete statistical overview of weather
    data over a specified period.
    """
    location: str
    period_start: date
    period_end: date
    
    # Core statistics
    temperature_stats: Optional[TemperatureStats] = None
    precipitation_summary: Optional[PrecipitationSummary] = None
    
    # Extreme events
    extreme_events: List[ExtremeEvent] = Field(default_factory=list)
    
    # Trends
    trends: List[Trend] = Field(default_factory=list)
    
    # Additional aggregations
    wind_stats: Optional[Dict[str, float]] = None
    humidity_stats: Optional[Dict[str, float]] = None
    pressure_stats: Optional[Dict[str, float]] = None
    
    # Agricultural specific
    total_evapotranspiration: Optional[float] = Field(None, description="Total ET0 in mm")
    irrigation_requirement: Optional[float] = Field(None, description="Estimated irrigation need in mm")
    suitable_planting_days: Optional[int] = Field(None, description="Days suitable for planting")
    
    # Data quality
    data_coverage: float = Field(
        ...,
        ge=0,
        le=1,
        description="Percentage of period with available data"
    )
    missing_days: List[date] = Field(default_factory=list)
    
    def get_trend_for_parameter(self, parameter: str) -> Optional[Trend]:
        """Get trend analysis for specific parameter."""
        for trend in self.trends:
            if trend.parameter == parameter:
                return trend
        return None
    
    def get_extreme_events_by_type(self, event_type: ExtremeEventType) -> List[ExtremeEvent]:
        """Filter extreme events by type."""
        return [e for e in self.extreme_events if e.event_type == event_type]
    
    def calculate_period_days(self) -> int:
        """Calculate total days in period."""
        return (self.period_end - self.period_start).days + 1
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Create a summary dictionary for reporting."""
        summary = {
            "location": self.location,
            "period": f"{self.period_start} to {self.period_end}",
            "days": self.calculate_period_days(),
            "data_coverage": f"{self.data_coverage * 100:.1f}%"
        }
        
        if self.temperature_stats:
            summary["temperature"] = {
                "avg": self.temperature_stats.mean,
                "min": self.temperature_stats.min,
                "max": self.temperature_stats.max
            }
        
        if self.precipitation_summary:
            summary["precipitation"] = {
                "total": self.precipitation_summary.total,
                "rain_days": self.precipitation_summary.days_with_rain,
                "frequency": f"{self.precipitation_summary.rain_frequency():.1f}%"
            }
        
        if self.extreme_events:
            summary["extreme_events"] = len(self.extreme_events)
        
        return summary


class CacheMetadata(BaseModel):
    """Metadata for cached responses."""
    cache_key: str = Field(..., description="Unique cache identifier")
    cached_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Cache expiration time")
    hit_count: int = Field(default=0, description="Number of cache hits")
    size_bytes: Optional[int] = Field(None, description="Size of cached data")
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() > self.expires_at
    
    def time_until_expiry(self) -> timedelta:
        """Calculate time until cache expires."""
        return self.expires_at - datetime.utcnow()
    
    def increment_hits(self):
        """Increment hit counter."""
        self.hit_count += 1