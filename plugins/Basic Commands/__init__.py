import aiohttp
import json
import os
from twitchio.ext import commands

metadata = {
    "name": "Commands Plugin",
    "version": "2.2",
    "author": "Jinxy",
    "description": "A plugin to handle custom chat commands with user-level filtering and aliases."
}

# Define your custom commands, their aliases, and required user levels here
CUSTOM_COMMANDS = {
    "!greet": {"response": "Hello there! How can I assist you today?", "level": 0, "aliases": ["!hello", "!hi"]},
    "!info": {"response": "I am TanukiTechBot, here to help manage your chat and entertain your audience!", "level": 0, "aliases": []},
    "!help": {"response": "Available commands: !greet, !info, !help", "level": 0, "aliases": []},
}

# User levels
USER_LEVELS = {
    "viewer": 0,
    "moderator": 1,
    "broadcaster": 2
}

class CommandsPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commands")
    async def list_commands(self, ctx):
        """List available commands for the user."""
        user_level = get_user_level(ctx.author)
        available_commands = []
    
        # Include only the commands that the user level allows
        for command, details in CUSTOM_COMMANDS.items():
            if details["level"] <= user_level:
                available_commands.append(command)
                available_commands.extend(details.get("aliases", []))
    
        # Dynamically add !game if user is a moderator or broadcaster
        if user_level >= USER_LEVELS["moderator"]:
            available_commands.append("!game")
    
        # Add "!commands" explicitly
        available_commands.append("!commands")
        await ctx.send(", ".join(available_commands))

    @commands.command(name="addcommand")
    async def add_command(self, ctx, command: str, response: str, *aliases):
        """Add a new custom command dynamically with optional aliases."""
        if get_user_level(ctx.author) < USER_LEVELS["moderator"]:
            await ctx.send("You do not have permission to add commands.")
            return

        if command in CUSTOM_COMMANDS:
            await ctx.send(f"The command '{command}' already exists.")
            return

        CUSTOM_COMMANDS[command] = {"response": response, "level": 0, "aliases": list(aliases)}
        await ctx.send(f"Command '{command}' has been added successfully with aliases: {', '.join(aliases) if aliases else 'none'}.")

    @commands.command(name="game")
    async def change_game(self, ctx, *, game_name: str):
        """Change the stream's category (game) if the user is a mod or the broadcaster."""
        if get_user_level(ctx.author) < USER_LEVELS["moderator"]:
            await ctx.send("You do not have permission to change the category.")
            return

        oauth_data = self.bot.oauth_data
        oauth_token = oauth_data.get("oauth_token")
        broadcaster_id = oauth_data.get("broadcaster_id")
        client_id = oauth_data.get("client_id")

        if not all([oauth_token, broadcaster_id, client_id]):
            await ctx.send("Missing OAuth configuration. Cannot change category.")
            return

        game_id = await self.fetch_game_id(game_name, oauth_token, client_id)
        if not game_id:
            await ctx.send(f"Could not find a category for '{game_name}'. Check spelling and try again.")
            return

        success = await self.update_category(broadcaster_id, game_id, oauth_token, client_id)
        if success:
            await ctx.send(f"Successfully changed the category to '{game_name}'.")
        else:
            await ctx.send("Failed to update the category. Check logs and token scopes.")

    @commands.Cog.event()
    async def event_message(self, message):
        """Listen for custom commands and their aliases."""
        if message.echo:
            return

        # Prevent duplicate responses for !commands
        if message.content == "!commands":
            return

        for command, details in CUSTOM_COMMANDS.items():
            if message.content == command or message.content in details.get("aliases", []):
                user_level = get_user_level(message.author)
                if user_level >= details["level"]:
                    await message.channel.send(details["response"])
                else:
                    await message.channel.send("You do not have permission to use this command.")
                return

    async def fetch_game_id(self, game_name: str, oauth_token: str, client_id: str):
        """Fetch the Twitch game ID for a given game name."""
        url = f"https://api.twitch.tv/helix/games?name={game_name}"
        headers = {
            "Authorization": f"Bearer {oauth_token}",
            "Client-Id": client_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Error fetching game ID: {response.status}")
                    return None
                data = await response.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["id"]
                return None

    async def update_category(self, broadcaster_id: str, game_id: str, oauth_token: str, client_id: str):
        """Update the Twitch channel's category."""
        url = "https://api.twitch.tv/helix/channels"
        headers = {
            "Authorization": f"Bearer {oauth_token}",
            "Client-Id": client_id,
            "Content-Type": "application/json"
        }
        payload = {
            "broadcaster_id": broadcaster_id,
            "game_id": game_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=payload) as response:
                if response.status == 204:
                    return True
                else:
                    print(f"Failed to update category: {response.status} - {await response.text()}")
                    return False

# Helper function to determine a user's level
def get_user_level(user):
    if user.is_broadcaster:
        return USER_LEVELS["broadcaster"]
    elif user.is_mod:
        return USER_LEVELS["moderator"]
    else:
        return USER_LEVELS["viewer"]

# Add the cog to the bot
def setup(bot):
    # Remove existing Cog if it's already loaded
    if "CommandsPlugin" in bot.cogs:
        bot.remove_cog("CommandsPlugin")
    bot.add_cog(CommandsPlugin(bot))
