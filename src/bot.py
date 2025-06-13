import os
import discord
import src.api.funny.funny as funny
import src.api.weather.weather as weather
from flask import Flask
from threading import Thread
from src.database import database
from src.utils.constants import (
    RESPONSE_TYPE_IMAGE_DIRECTORY,
    RESPONSE_TYPE_IMAGE_URL,
    RESPONSE_TYPE_STRING,
    RESPONSE_TYPE_JOKE,
    IMAGE_BASE_PATH,
)
from src.utils.utils import get_user_query

app = Flask("")


def get_response(user_message: str) -> tuple[str, any] | None:
    if not (
        user_message.startswith("?") or user_message.startswith("#")
    ):  # not a command
        return

    # returns (response_type, response message)
    user_message = user_message.lower()
    if user_message.startswith("#"):
        return (
            RESPONSE_TYPE_IMAGE_DIRECTORY,
            f"{IMAGE_BASE_PATH}/{user_message[1:]}.png",
        )

    if user_message.startswith("?weather"):
        city_name: str = get_user_query(user_message, default="Toronto")
        return (RESPONSE_TYPE_STRING, weather.get_current_weather(city_name))

    if user_message.startswith("?gpt"):
        return (RESPONSE_TYPE_STRING, "I dont understand that. Please be more clear.")

    if user_message.startswith("?meme"):
        return (RESPONSE_TYPE_IMAGE_URL, funny.get_random_meme())

    if user_message.startswith("?joke"):
        return (RESPONSE_TYPE_JOKE, funny.get_random_joke())

    if user_message.startswith("?advice"):
        return (RESPONSE_TYPE_STRING, funny.get_random_advice())

    return (RESPONSE_TYPE_STRING, "Failed to identify command!")


async def send_message(
    message_obj: discord.Message, response_type: str, response_message: any
) -> None:
    try:

        if response_type == RESPONSE_TYPE_IMAGE_URL:
            # response_message is an url
            embed: discord.embeds.Embed = discord.Embed()
            embed.set_image(url=response_message)

            await message_obj.channel.send(embed=embed)

        elif response_type == RESPONSE_TYPE_IMAGE_DIRECTORY:
            image: discord.file.File = discord.File(response_message)
            await message_obj.channel.send("Hello!", file=image)

        elif response_type == RESPONSE_TYPE_STRING:
            await message_obj.channel.send(response_message)

        elif response_type == RESPONSE_TYPE_JOKE:  # tuple[str, str]
            await message_obj.channel.send(
                f"{response_message[0]}\n{response_message[1]}"
            )

    except Exception as e:
        print(e)


def run_discord_bot() -> None:
    """runs discord bot"""
    TOKEN = os.environ["DISCORD_TOKEN"]
    intents = discord.Intents.all()

    intents.message_content = True

    client: discord.Client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        print(f"Logged in as {client.user.name}")

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return

        username: str = message.author.name
        content: str = message.content
        channel: discord.channel.TextChannel = message.channel

        print(f"\n{username} said: '{content}' in {str(channel)}\n")

        database.log_message(username=username, text=content)

        response: tuple[str, str] | None = get_response(content)

        if response:
            response_type, response_message = response
            await send_message(message, response_type, response_message)

    client.run(TOKEN)


@app.route("/")
def home() -> str:
    return "Discord bot is running"


def run_server() -> None:
    app.run(host="0.0.0.0", port=8080)


def thread_bot_server() -> None:
    t = Thread(target=run_server)
    t.start()


if __name__ == "__main__":

    if os.environ.get("RENDER") is None:
        from dotenv import load_dotenv

        load_dotenv()

    thread_bot_server()
    run_discord_bot()
