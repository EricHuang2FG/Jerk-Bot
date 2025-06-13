import requests
from src.utils.constants import TIMEOUT


def get_random_meme() -> str:
    url: str = "https://meme-api.com/gimme"
    response = requests.get(url, timeout=TIMEOUT)
    data: dict = response.json()

    return data["url"]


def get_random_joke() -> tuple[str, str]:
    """Returns a tuple of setup and punchline"""
    url: str = "https://official-joke-api.appspot.com/jokes/general/random"
    response = requests.get(url, timeout=TIMEOUT)
    data: dict = response.json()[0]
    return (data["setup"], data["punchline"])


def get_random_advice() -> str:
    url: str = "https://api.adviceslip.com/advice"
    response = requests.get(url, timeout=TIMEOUT)
    data: dict = response.json()

    return data["slip"]["advice"]


if __name__ == "__main__":
    get_random_meme()
    get_random_joke()
