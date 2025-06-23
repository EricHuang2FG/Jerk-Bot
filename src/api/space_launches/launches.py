import time
import threading
import requests
import urllib.parse
from datetime import datetime
from src.utils.constants import (
    SPACE_LAUNCHES_BASE_URL,
    RATE_LIMIT_SPACE_LAUNCHES_SECONDS,
    NUM_FUTURE_LAUNCHES_TO_GET,
    ERROR_IMAGE_URL,
    TIMEOUT,
)
from src.utils.utils import format_rate_limit_exceeded_message


lock: threading.Lock = threading.Lock()
prev_call_time: float = time.time() - RATE_LIMIT_SPACE_LAUNCHES_SECONDS


def get_future_launches() -> list[tuple[str, str, str]]:
    global prev_call_time
    with lock:
        curr_time: float = time.time()
        time_diff: float = curr_time - prev_call_time
        if time_diff < RATE_LIMIT_SPACE_LAUNCHES_SECONDS:
            return [
                (
                    "Rate Limit Exceeded!",
                    format_rate_limit_exceeded_message(
                        RATE_LIMIT_SPACE_LAUNCHES_SECONDS, time_diff
                    ),
                    ERROR_IMAGE_URL,
                )
            ]

        prev_call_time = curr_time

    query_params: dict = {
        "mode": "normal",
        "hide_recent_previous": True,
        "limit": NUM_FUTURE_LAUNCHES_TO_GET,
    }

    try:
        response: requests.Response = requests.get(
            f"{SPACE_LAUNCHES_BASE_URL}/launches/upcoming/?{urllib.parse.urlencode(query_params)}",
            timeout=TIMEOUT,
        )
        response.raise_for_status()

        data: dict = response.json()
        launches_list_raw: list = data["results"]

        # returns a list of tuple
        # where each tuple is (title, description_string, image_url)
        return [
            (
                f"***{launch_info['name']}***",
                (
                    f"- **Status:** {launch_info['status']['name']}\n"
                    f"- **T-0:** {datetime.strptime(launch_info['net'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S UTC")}\n"
                    f"- **Rocket:** {launch_info['rocket']['configuration']['full_name']}\n"
                    f"- **Launch Provider: ** {launch_info['launch_service_provider']['name']}\n"
                    f"- **Target Orbit: ** {launch_info['mission']['orbit']['abbrev']}\n"
                    f"- **Launch Location: ** {launch_info['pad']['name']}, {launch_info['pad']['location']['name']}"
                ),
                launch_info["image"]["image_url"],
            )
            for launch_info in launches_list_raw
        ]

    except Exception as e:
        print(e)
        return [
            (
                "Error getting future launches!",
                "Please try again later.",
                ERROR_IMAGE_URL,
            )
        ]
