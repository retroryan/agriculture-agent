"""
Parameter definitions for Open-Meteo API.

Organized groups of weather parameters for different use cases.
"""

# Basic weather parameters
BASIC_WEATHER = [
    "temperature_2m",
    "relative_humidity_2m", 
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
    "weather_code"
]

# Temperature-related parameters
TEMPERATURE_PARAMS = [
    "temperature_2m",
    "apparent_temperature",
    "dew_point_2m"
]

# Precipitation parameters
PRECIPITATION_PARAMS = [
    "precipitation",
    "rain",
    "showers",
    "snowfall"
]

# Agricultural parameters
AGRICULTURAL_PARAMS = [
    "et0_fao_evapotranspiration",
    "vapour_pressure_deficit",
    "soil_moisture_0_to_1cm",
    "soil_moisture_1_to_3cm",
    "soil_moisture_3_to_9cm",
    "soil_moisture_9_to_27cm",
    "soil_moisture_27_to_81cm",
    "soil_temperature_0cm",
    "soil_temperature_6cm",
    "soil_temperature_18cm",
    "soil_temperature_54cm"
]

# Solar radiation parameters
SOLAR_PARAMS = [
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "uv_index",
    "uv_index_clear_sky"
]

# Standard daily weather parameters for forecast
WEATHER_DAILY_PARAMS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "precipitation_sum",
    "rain_sum",
    "showers_sum",
    "snowfall_sum",
    "precipitation_hours",
    "weather_code",
    "sunrise",
    "sunset",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "uv_index_max",
    "et0_fao_evapotranspiration"
]

# Standard hourly weather parameters for forecast
WEATHER_HOURLY_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "weather_code",
    "pressure_msl",
    "surface_pressure",
    "cloud_cover",
    "visibility",
    "wind_speed_10m",
    "wind_direction_10m"
]

# Predefined agricultural locations
AGRICULTURAL_LOCATIONS = {
    "Grand Island, Nebraska": {
        "coordinates": (40.9264, -98.3420),
        "crops": "corn/soybeans",
        "state": "Nebraska"
    },
    "Scottsbluff, Nebraska": {
        "coordinates": (41.8666, -103.6672),
        "crops": "sugar beets/corn",
        "state": "Nebraska"
    },
    "Ames, Iowa": {
        "coordinates": (42.0347, -93.6200),
        "crops": "corn/soybeans",
        "state": "Iowa"
    },
    "Cedar Rapids, Iowa": {
        "coordinates": (41.9779, -91.6656),
        "crops": "corn/soybeans",
        "state": "Iowa"
    },
    "Fresno, California": {
        "coordinates": (36.7468, -119.7726),
        "crops": "grapes/almonds",
        "state": "California"
    },
    "Salinas, California": {
        "coordinates": (36.6777, -121.6555),
        "crops": "lettuce/strawberries",
        "state": "California"
    },
    "Lubbock, Texas": {
        "coordinates": (33.5779, -101.8552),
        "crops": "cotton/sorghum",
        "state": "Texas"
    },
    "Amarillo, Texas": {
        "coordinates": (35.2220, -101.8313),
        "crops": "wheat/cattle",
        "state": "Texas"
    }
}