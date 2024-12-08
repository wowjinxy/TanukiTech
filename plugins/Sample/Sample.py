metadata = {
    "name": "Sample Plugin",
    "version": "1.0",
    "author": "Jinxy",
    "description": "This is a sample plugin for the Twitch bot."
}

async def on_message(bot, message):
    if "hello" in message.content.lower():
        await message.channel.send(f"Hello, {message.author.name}!")