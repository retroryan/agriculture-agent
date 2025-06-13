"""
Basic tools module - fundamental tools without external dependencies.

Available tools:
- Mathematical operations (add, multiply)
- Mock weather data
- Text analysis
- Date/time utilities
- Agricultural advice
"""

from .tools import (
    add_numbers,
    multiply_numbers,
    get_simulated_weather,
    count_words,
    get_current_time,
    calculate_days_between,
    reverse_text,
    agricultural_advice,
    ALL_TOOLS
)

__all__ = [
    "add_numbers",
    "multiply_numbers",
    "get_simulated_weather",
    "count_words",
    "get_current_time",
    "calculate_days_between",
    "reverse_text",
    "agricultural_advice",
    "ALL_TOOLS"
]