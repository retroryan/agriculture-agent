"""Open-Meteo parameter definitions for weather and climate data."""

from typing import List, Dict, Any


# Temperature parameters (daily)
TEMPERATURE_PARAMS = [
    "temperature_2m_max",
    "temperature_2m_min", 
    "temperature_2m_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "apparent_temperature_mean"
]

# Note: Soil temperature is only available in hourly data, not daily
SOIL_TEMPERATURE_PARAMS = []

# Precipitation parameters
PRECIPITATION_PARAMS = [
    "precipitation_sum",
    "rain_sum",
    "showers_sum",
    "snowfall_sum",
    "precipitation_hours",
    "precipitation_probability_max"
]

# Soil moisture parameters (volumetric water content)
SOIL_MOISTURE_PARAMS = [
    "soil_moisture_0_to_1cm",
    "soil_moisture_1_to_3cm",
    "soil_moisture_3_to_9cm", 
    "soil_moisture_9_to_27cm",
    "soil_moisture_27_to_81cm"
]

# Additional weather parameters
WEATHER_PARAMS = [
    "weather_code",
    "cloud_cover",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant"
]

# Solar and radiation parameters
SOLAR_PARAMS = [
    "shortwave_radiation_sum",
    "direct_radiation_instant",
    "diffuse_radiation_instant",
    "direct_normal_irradiance_instant",
    "terrestrial_radiation_instant",
    "uv_index_max",
    "uv_index_clear_sky_max"
]

# Daylight parameters
DAYLIGHT_PARAMS = [
    "sunrise",
    "sunset",
    "daylight_duration",
    "sunshine_duration"
]

# Agricultural parameters
AGRICULTURAL_PARAMS = [
    "et0_fao_evapotranspiration",
    "vapor_pressure_deficit_max",
    "growing_degree_days_base_0_limit_50",
    "leaf_wetness_probability_mean"
]

# Parameter groups for different use cases
PARAMETER_GROUPS = {
    "temperature": TEMPERATURE_PARAMS,  # Removed soil temperature since it's hourly only
    "precipitation": PRECIPITATION_PARAMS,
    "soil_moisture": SOIL_MOISTURE_PARAMS,
    "basic_weather": WEATHER_PARAMS + ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "agricultural": AGRICULTURAL_PARAMS + SOIL_MOISTURE_PARAMS,
    "solar": SOLAR_PARAMS + DAYLIGHT_PARAMS
}


def get_parameters_for_analysis(analysis_type: str) -> List[str]:
    """
    Get relevant parameters for a specific analysis type.
    
    Args:
        analysis_type: Type of analysis (temperature, precipitation, soil_moisture)
        
    Returns:
        List of parameter names
    """
    return PARAMETER_GROUPS.get(analysis_type, [])


def get_all_parameters() -> List[str]:
    """Get all available parameters."""
    all_params = []
    for params in PARAMETER_GROUPS.values():
        all_params.extend(params)
    return list(set(all_params))  # Remove duplicates


def format_parameter_description(param: str) -> str:
    """Get human-readable description for a parameter."""
    descriptions = {
        "temperature_2m_max": "Maximum temperature at 2 meters",
        "temperature_2m_min": "Minimum temperature at 2 meters",
        "temperature_2m_mean": "Mean temperature at 2 meters",
        "precipitation_sum": "Total precipitation",
        "rain_sum": "Total liquid rain",
        "snowfall_sum": "Total snowfall",
        "soil_moisture_0_to_1cm": "Soil moisture 0-1cm depth",
        "soil_moisture_1_to_3cm": "Soil moisture 1-3cm depth",
        "soil_moisture_3_to_9cm": "Soil moisture 3-9cm depth",
        "soil_moisture_9_to_27cm": "Soil moisture 9-27cm depth",
        "soil_moisture_27_to_81cm": "Soil moisture 27-81cm depth",
        "et0_fao_evapotranspiration": "Reference evapotranspiration (FAO method)",
        "vapor_pressure_deficit_max": "Maximum vapor pressure deficit",
        "growing_degree_days_base_0_limit_50": "Growing degree days (base 0°C, limit 50°C)",
        "leaf_wetness_probability_mean": "Mean leaf wetness probability"
    }
    return descriptions.get(param, param.replace("_", " ").title())