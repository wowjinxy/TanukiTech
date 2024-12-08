# plugins/commands_plugin.py

from twitchio.ext import commands

metadata = {
    "name": "Commands Plugin",
    "version": "1.5",
    "author": "Jinxy",
    "description": "A plugin to handle custom chat commands with user-level filtering."
}

# Define your custom commands and their required user levels here
CUSTOM_COMMANDS = {
    "!greet": {"response": "Hello there! How can I assist you today?", "level": 0},
    "!info": {"response": "I am TanukiTechBot, here to help manage your chat and entertain your audience!", "level": 0},
    "!help": {"response": "Available commands: !greet, !info, !help, !commands", "level": 0},
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
        available_commands = [
            command for command, details in CUSTOM_COMMANDS.items()
            if details["level"] <= user_level
        ]
        response = "Available commands: " + ", ".join(available_commands)
        await ctx.send(response)

    @commands.Cog.event()
    async def event_message(self, message):
        """Listen for custom commands."""
        if message.echo:
            return

        if message.content in CUSTOM_COMMANDS:
            command_details = CUSTOM_COMMANDS[message.content]
            user_level = get_user_level(message.author)
            if user_level >= command_details["level"]:
                await message.channel.send(command_details["response"])
            else:
                await message.channel.send("You do not have permission to use this command.")

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

