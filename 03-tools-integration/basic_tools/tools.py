"""
Basic tools for LangGraph examples that don't require external APIs.
These tools demonstrate various tool patterns and serve as examples.
"""

from langchain_core.tools import tool
from typing import Optional
import random
from datetime import datetime, timedelta


@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


@tool
def get_simulated_weather(location: str) -> str:
    """
    Get simulated weather forecast for a location (demo purposes only).
    Note: This returns simulated data for demonstration. Real weather API integration available in later modules.
    """
    # Mock weather data in Open Meteo style
    conditions = ["clear sky", "partly cloudy", "overcast", "light rain", "fog"]
    temps_c = range(10, 30)
    
    # Generate consistent weather for same location (pseudo-random)
    seed = sum(ord(c) for c in location)
    random.seed(seed)
    
    temp = random.choice(temps_c)
    condition = random.choice(conditions)
    wind_speed = random.randint(5, 25)
    precipitation = random.choice([0, 0, 0, 2, 5, 10])  # mm
    
    return f"Weather in {location}: {temp}°C, {condition}, wind: {wind_speed} km/h, precipitation: {precipitation}mm"


@tool
def count_words(text: str) -> dict:
    """
    Count the number of words and characters in text.
    Returns a dictionary with word count, character count, and line count.
    """
    words = text.split()
    lines = text.split('\n')
    
    return {
        "word_count": len(words),
        "character_count": len(text),
        "character_count_no_spaces": len(text.replace(" ", "")),
        "line_count": len(lines),
        "average_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0
    }


@tool
def get_current_time(timezone: Optional[str] = None) -> str:
    """
    Get the current date and time.
    Timezone parameter is ignored in this mock implementation.
    """
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def calculate_days_between(start_date: str, end_date: str) -> int:
    """
    Calculate the number of days between two dates.
    Dates should be in YYYY-MM-DD format.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        delta = end - start
        return abs(delta.days)
    except ValueError as e:
        return f"Error: Invalid date format. Use YYYY-MM-DD. {str(e)}"


@tool
def reverse_text(text: str) -> str:
    """Reverse the given text."""
    return text[::-1]


@tool
def agricultural_advice(crop: str, condition: str) -> str:
    """
    Provide agricultural advice based on crop type and weather conditions.
    Integrates with Open Meteo weather data for informed decision making.
    """
    advice_map = {
        ("corn", "dry"): "Open Meteo shows low precipitation. Consider irrigation - corn needs adequate moisture.",
        ("corn", "wet"): "High precipitation in Open Meteo data. Ensure drainage to prevent root rot.",
        ("corn", "hot"): "Open Meteo shows high temperatures. Monitor for heat stress using hourly temperature data.",
        ("wheat", "dry"): "Low soil moisture from Open Meteo data. Consider drought-resistant varieties.",
        ("wheat", "wet"): "High humidity in Open Meteo forecast. Watch for fungal diseases.",
        ("wheat", "cold"): "Check Open Meteo frost warnings. Winter wheat tolerates cold better than spring wheat.",
        ("soybeans", "dry"): "Monitor Open Meteo precipitation forecasts. Soybeans need water during pod development.",
        ("soybeans", "wet"): "Open Meteo shows excess moisture. Ensure proper field drainage.",
    }
    
    key = (crop.lower(), condition.lower())
    default_advice = f"Check Open Meteo API for detailed weather data to optimize {crop} growing in {condition} conditions."
    
    return advice_map.get(key, default_advice)


# List of all available tools for easy import
ALL_TOOLS = [
    add_numbers,
    multiply_numbers,
    get_simulated_weather,
    count_words,
    get_current_time,
    calculate_days_between,
    reverse_text,
    agricultural_advice
]