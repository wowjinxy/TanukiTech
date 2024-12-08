# plugins/custom_name_plugin.py

metadata = {
    "name": "Custom Name Plugin",
    "version": "1.0",
    "author": "Jinxy",
    "description": "Allows the bot to use a custom display name in its messages."
}

CUSTOM_NAME = "TanukiTech"  # Replace with your desired bot display name

def format_message(author_name, message):
    """Formats the message with the custom display name."""
    return f"Hello, {author_name}! I am {CUSTOM_NAME}, your helpful bot. {message}"

async def on_message(bot, message):
    if "hello" in message.content.lower():
        formatted_message = format_message(message.author.name, "How can I assist you today?")
        await message.channel.send(formatted_message)
