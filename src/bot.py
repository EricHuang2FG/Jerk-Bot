import os
import discord
from flask import Flask
from threading import Thread
from src.database import database

app = Flask("")


async def send_message(message_obj: discord.Message, user_message: str) -> None:
    try:
        await message_obj.channel.send(user_message)
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

        # database.log_message(username=username, text=content)
        await send_message(message, "testing hello testing")

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
