import os
import time
import requests
import threading
from urllib.parse import quote
from src.utils.constants import (
    WEATHER_API_BASE_URL,
    TIMEOUT,
    RATE_LIMIT_WEATHER_API_SECONDS,
)
from src.utils.utils import format_rate_limit_exceeded_message

lock: threading.Lock = threading.Lock()
prev_call_time: float = time.time() - RATE_LIMIT_WEATHER_API_SECONDS


def get_current_weather(city_name: str):
    global prev_call_time
    with lock:
        curr_time: float = time.time()
        time_diff: float = curr_time - prev_call_time
        if time_diff < RATE_LIMIT_WEATHER_API_SECONDS:
            return format_rate_limit_exceeded_message(
                RATE_LIMIT_WEATHER_API_SECONDS, time_diff
            )

        prev_call_time = curr_time

    try:
        url: str = (
            f"{WEATHER_API_BASE_URL}/current.json"
            f"?key={os.environ['WEATHER_API_KEY']}"
            f"&q={quote(city_name)}"
        )
        response = requests.get(url, timeout=TIMEOUT)
        data = response.json()

        location: dict = data["location"]
        weather: dict = data["current"]
        condition: dict = weather["condition"]

        return (
            f"***Weather for {location['name']}, {location['region']}, {location['country']}***\n\n"
            f"- **Local Time:** {location['localtime']}\n"
            f"- **Condition:** {condition['text']}\n"
            f"- **Temperature:** {weather['temp_c']}°C / {weather['temp_f']}°F\n"
            f"- **Feels Like:** {weather['feelslike_c']}°C / {weather['feelslike_f']}°F\n"
            f"- **Heat Index:** {weather['heatindex_c']}°C / {weather['heatindex_f']}°F\n"
            f"- **Wind Chill:** {weather['windchill_c']}°C / {weather['windchill_f']}°F\n"
            f"- **Dew Point:** {weather['dewpoint_c']}°C / {weather['dewpoint_f']}°F\n"
            f"- **Humidity:** {weather['humidity']}%\n"
            f"- **Wind:** {weather['wind_kph']} kph / {weather['wind_mph']} mph ({weather['wind_dir']})\n"
            f"- **Pressure:** {weather['pressure_mb']} mb / {weather['pressure_in']} in\n"
            f"- **Precipitation:** {weather['precip_mm']} mm / {weather['precip_in']} in\n"
            f"- **Visibility:** {weather['vis_km']} km / {weather['vis_miles']} miles\n"
            f"- **UV Index:** {weather['uv']}\n"
            f"- **Last Updated:** {weather['last_updated']}"
        )

    except Exception as e:
        print(e)
        return "Error getting the current weather!"
