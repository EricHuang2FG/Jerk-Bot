from discord.ext import tasks
from src.utils.constants import IMAGE_CHANNEL_ID


@tasks.loop(minutes=10)  # Run every 10 mins to respect rate limits
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
                if any(
                    attachment.filename.lower().endswith(ext)
                    for ext in ["png", "jpg", "jpeg", "gif", "webp", "heic"]
                ):
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
