"""
Basic tools module - fundamental tools without external dependencies.

Available tools:
- Mathematical operations (add, multiply)
- Mock weather data
- Text analysis
- Date/time utilities
- Agricultural advice

Tools are organized by category for easier selection.
"""

from .tools import (
    add_numbers,
    multiply_numbers,
    get_simulated_weather,
    count_words,
    get_current_time,
    calculate_days_between,
    agricultural_advice,
    ALL_TOOLS
)

# Organize tools by category for easier selection
MATH_TOOLS = [add_numbers, multiply_numbers]
TEXT_TOOLS = [count_words]
TIME_TOOLS = [get_current_time, calculate_days_between]
WEATHER_TOOLS = [get_simulated_weather, agricultural_advice]

__all__ = [
    # Individual tools
    "add_numbers",
    "multiply_numbers",
    "get_simulated_weather",
    "count_words",
    "get_current_time",
    "calculate_days_between",
    "agricultural_advice",
    # Tool collections
    "ALL_TOOLS",
    "MATH_TOOLS",
    "TEXT_TOOLS",
    "TIME_TOOLS",
    "WEATHER_TOOLS"
]