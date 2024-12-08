# plugins/commands_plugin.py

from twitchio.ext import commands

metadata = {
    "name": "Commands Plugin",
    "version": "2.1",
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

        for command, details in CUSTOM_COMMANDS.items():
            if details["level"] <= user_level:
                available_commands.append(command)
                available_commands.extend(details.get("aliases", []))

        # Add "!commands" explicitly to the list
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
