from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """Calculate a simple mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception:  # noqa: BLE001
        return "Invalid mathematical expression."


@tool
def get_weather(city: str) -> str:
    """Get weather information for a city."""
    weather = {
        "mumbai": "32°C, humid",
        "delhi": "35°C, sunny",
        "london": "18°C, cloudy",
    }

    return weather.get(
        city.lower(),
        f"No weather data available for {city}.",
    )
