import os
import time
import requests
import threading
from src.utils.constants import (
    CHAT_GPT_MODEL,
    CHAT_GPT_BASE_URL,
    TIMEOUT,
    RATE_LIMIT_CHAT_GPT_SECONDS,
)
from src.utils.utils import format_rate_limit_exceeded_message


lock: threading.Lock = threading.Lock()
prev_call_time: float = time.time() - RATE_LIMIT_CHAT_GPT_SECONDS


def get_response(prompt: str) -> str:
    global prev_call_time
    with lock:
        curr_time: float = time.time()
        time_diff: float = curr_time - prev_call_time
        if time_diff < RATE_LIMIT_CHAT_GPT_SECONDS:
            return format_rate_limit_exceeded_message(
                RATE_LIMIT_CHAT_GPT_SECONDS, time_diff
            )

        prev_call_time = curr_time

    request_body: dict = {
        "model": CHAT_GPT_MODEL,
        "messages": [{"role": "user", "content": f"{prompt}\nBe concise!"}],
    }

    headers: dict = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPEN_AI_KEY']}",
        "OpenAI-Organization": os.environ["OPEN_AI_ORGANIZATION"],
        "OpenAI-Project": os.environ["OPEN_AI_PROJECT"],
    }

    try:
        response: requests.Response = requests.post(
            CHAT_GPT_BASE_URL, headers=headers, json=request_body, timeout=TIMEOUT
        )
        response.raise_for_status()

        data: dict = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(e)
        return "Error getting chat response!"
