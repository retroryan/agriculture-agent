"""
Open-Meteo parameter collections for weather data retrieval.

This module defines common parameter groups for different weather data use cases.
Parameters are organized by data type and measurement category.
"""

# Temperature-related parameters
TEMPERATURE_PARAMS = {
    "current": [
        "temperature_2m",
        "apparent_temperature",
        "is_day"
    ],
    "hourly": [
        "temperature_2m",
        "apparent_temperature",
        "dewpoint_2m"
    ],
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "apparent_temperature_max",
        "apparent_temperature_min",
        "apparent_temperature_mean"
    ]
}

# Precipitation-related parameters
PRECIPITATION_PARAMS = {
    "current": [
        "precipitation",
        "rain",
        "showers",
        "snowfall"
    ],
    "hourly": [
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "precipitation_probability"
    ],
    "daily": [
        "precipitation_sum",
        "rain_sum",
        "showers_sum",
        "snowfall_sum",
        "precipitation_hours",
        "precipitation_probability_max"
    ]
}

# Soil moisture parameters
# Note: Soil moisture is only available as hourly data in Open-Meteo
SOIL_MOISTURE_PARAMS = {
    "hourly": [
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm",
        "soil_moisture_9_to_27cm",
        "soil_moisture_27_to_81cm"
    ],
    "daily": []  # Not available as daily aggregates
}

# Soil temperature parameters
# Note: Soil temperature is only available as hourly data in Open-Meteo
SOIL_TEMPERATURE_PARAMS = {
    "hourly": [
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
        "soil_temperature_54cm"
    ],
    "daily": []  # Not available as daily aggregates
}

# Wind parameters
WIND_PARAMS = {
    "current": [
        "windspeed_10m",
        "winddirection_10m",
        "windgusts_10m"
    ],
    "hourly": [
        "windspeed_10m",
        "winddirection_10m",
        "windgusts_10m"
    ],
    "daily": [
        "windspeed_10m_max",
        "windgusts_10m_max",
        "winddirection_10m_dominant"
    ]
}

# Basic weather parameters
BASIC_WEATHER_PARAMS = {
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "weathercode",
        "cloudcover",
        "windspeed_10m",
        "winddirection_10m"
    ],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "weathercode",
        "cloudcover",
        "windspeed_10m",
        "winddirection_10m",
        "surface_pressure"
    ],
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "weathercode",
        "windspeed_10m_max",
        "winddirection_10m_dominant"
    ]
}

# Agricultural parameters
AGRICULTURAL_PARAMS = {
    "hourly": [
        "soil_temperature_0cm",
        "soil_moisture_0_to_1cm",
        "et0_fao_evapotranspiration",
        "vapour_pressure_deficit"
    ],
    "daily": [
        "et0_fao_evapotranspiration",
        "precipitation_sum",
        "temperature_2m_max",
        "temperature_2m_min"
    ]
}

# Common location presets for demonstration
LOCATIONS = {
    "Iowa City": {"latitude": 41.6611, "longitude": -91.5302},
    "Des Moines": {"latitude": 41.5868, "longitude": -93.6250},
    "Chicago": {"latitude": 41.8781, "longitude": -87.6298},
    "New York": {"latitude": 40.7128, "longitude": -74.0060},
    "London": {"latitude": 51.5074, "longitude": -0.1278},
    "Tokyo": {"latitude": 35.6762, "longitude": 139.6503},
    "Sydney": {"latitude": -33.8688, "longitude": 151.2093}
}