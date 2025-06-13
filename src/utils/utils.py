def format_rate_limit_exceeded_message(
    rate_limit_seconds: int, seconds_after_prev_trigger: float
) -> str:
    return (
        f"Rate limit exceeded! You can only use this command every once per {rate_limit_seconds} seconds."
        f"Try again in {round(rate_limit_seconds - seconds_after_prev_trigger)} seconds."
    )


def get_user_query(user_message: str, default: str = "") -> str:
    parts: list[str] = user_message.split(" ", maxsplit=1)
    return parts[1] if len(parts) > 1 else default
