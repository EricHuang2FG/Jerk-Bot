import os
import discord
from discord.ext import tasks
import src.api.funny.funny as funny
import src.api.weather.weather as weather
import src.api.chat_gpt.chat_gpt as chat
import src.api.space_launches.launches as launches
from flask import Flask
from threading import Thread
from src.database import database
from src.utils.constants import (
    RESPONSE_TYPE_IMAGE_DIRECTORY,
    RESPONSE_TYPE_IMAGE_URL,
    RESPONSE_TYPE_STRING,
    RESPONSE_TYPE_JOKE,
    RESPONSE_TYPE_LAUNCHES,
    IMAGE_BASE_PATH,
)
from src.utils.utils import get_user_query

app = Flask("")

IMAGE_CHANNEL_ID = 1460723596971475065

@tasks.loop(minutes=10) # Run every 10 mins to respect rate limits
async def update_image_count_task(client):
    try:
        # Ensure channel exists and is a text channel/thread
        channel = client.get_channel(IMAGE_CHANNEL_ID)
        if not channel or not hasattr(channel, "history"):
            return

        count = 0
        # Iterate through history
        async for message in channel.history(limit=None):
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'heic']):
                    count += 1

        if count > 1:
            new_name = f"{count}-useful-images"
            new_topic = f"this channel can only contain {count} images at a time. if another one is sent, the first image sent will be deleted."
        else:
            new_name = "useful-image"
            new_topic = "this channel can only contain 1 image at a time. if another one is sent, the first image sent will be deleted."

        # Only update if there is a change to save on API calls
        if channel.name != new_name or channel.topic != new_topic:
            await channel.edit(name=new_name, topic=new_topic)
            print(f"Updated {channel.name} to {count} images.")
    except Exception as e:
        print(f"Error in update_image_count_task: {e}")



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

    if user_message.startswith("?chat"):
        prompt: str = get_user_query(user_message, default="")
        if prompt:
            return (RESPONSE_TYPE_STRING, chat.get_response(prompt))
        return (RESPONSE_TYPE_STRING, "Please enter a non-empty prompt!")

    if user_message.startswith("?meme"):
        return (RESPONSE_TYPE_IMAGE_URL, funny.get_random_meme())

    if user_message.startswith("?joke"):
        return (RESPONSE_TYPE_JOKE, funny.get_random_joke())

    if user_message.startswith("?advice"):
        return (RESPONSE_TYPE_STRING, funny.get_random_advice())

    if user_message.startswith("?future_launches"):
        return (RESPONSE_TYPE_LAUNCHES, launches.get_future_launches())

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

        elif (
            response_type == RESPONSE_TYPE_LAUNCHES
        ):  # list[tuple[title, description_string, image_url]]
            for title, description_string, image_url in response_message:
                embed: discord.embeds.Embed = discord.Embed(
                    title=title, description=description_string
                )
                embed.set_image(url=image_url)

                await message_obj.channel.send(embed=embed)

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
        if not update_image_count_task.is_running():
            update_image_count_task.start(client)

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
