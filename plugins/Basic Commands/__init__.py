import os
import importlib.util
from twitchio.ext import commands

metadata = {
    "name": "Commands Plugin",
    "version": "2.4",
    "author": "Jinxy",
    "description": "A plugin to handle custom chat commands dynamically."
}

USER_LEVELS = {
    "viewer": 0,
    "moderator": 1,
    "broadcaster": 2
}

class CommandsPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CUSTOM_COMMANDS = self.load_commands()

    def load_commands(self):
        """
        Dynamically load commands from the 'commands' subdirectory.
        Each command file defines COMMAND_DEFINITION, e.g.:

        COMMAND_DEFINITION = {
            "!command": {
                "response": "Some response text or None",
                "level": 0,
                "aliases": ["!alias1", "!alias2"],
                "callback": async function or None
            }
        }
        """
        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        custom_commands = {}

        if not os.path.isdir(commands_dir):
            os.makedirs(commands_dir)

        for filename in os.listdir(commands_dir):
            if filename.endswith(".py"):
                file_path = os.path.join(commands_dir, filename)
                command_name = filename[:-3]

                spec = importlib.util.spec_from_file_location(command_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "COMMAND_DEFINITION"):
                    for cmd, details in module.COMMAND_DEFINITION.items():
                        custom_commands[cmd] = details
                else:
                    print(f"WARNING: {filename} does not define COMMAND_DEFINITION. Skipping...")

        return custom_commands

    def get_user_level(self, user):
        if user.is_broadcaster:
            return USER_LEVELS["broadcaster"]
        elif user.is_mod:
            return USER_LEVELS["moderator"]
        else:
            return USER_LEVELS["viewer"]

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        # Convert message to lowercase for matching commands
        content_lower = message.content.strip().lower()

        for command, details in self.CUSTOM_COMMANDS.items():
            # Check if the message matches the command or one of its aliases
            all_triggers = [command] + details.get("aliases", [])
            if content_lower.split(" ")[0] in all_triggers:
                user_level = self.get_user_level(message.author)
                if user_level >= details["level"]:
                    callback = details.get("callback")

                    # A minimal ctx-like object for callback convenience
                    class Ctx:
                        def __init__(self, message, bot):
                            self.message = message
                            self.channel = message.channel
                            self.author = message.author
                            self.bot = bot
                        async def send(self, content):
                            await self.channel.send(content)

                    ctx = Ctx(message, self.bot)

                    if callback:
                        # Handle arguments if needed by specific commands
                        if command == "!game":
                            parts = message.content.strip().split(" ", 1)
                            if len(parts) > 1:
                                game_name = parts[1]
                                await callback(ctx, self.bot, game_name)
                            else:
                                await ctx.send("Please specify a game name.")
                        elif command == "!addcommand":
                            # Example argument handling for addcommand:
                            # !addcommand <command> <response> <aliases...>
                            parts = message.content.strip().split(" ", 3)
                            if len(parts) < 3:
                                await ctx.send("Usage: !addcommand <command> <response> [aliases]")
                            else:
                                # parts[1]: command
                                # parts[2]: response
                                # parts[3]: aliases (optional)
                                cmd_name = parts[1]
                                cmd_response = parts[2]
                                aliases = parts[3].split() if len(parts) > 3 else []
                                await callback(ctx, self.bot, cmd_name, cmd_response, aliases)
                        else:
                            # No extra args needed
                            await callback(ctx, self.bot)
                    else:
                        # No callback, just send the response if available
                        if details.get("response"):
                            await ctx.send(details["response"])
                else:
                    await message.channel.send("You do not have permission to use this command.")
                return  # Stop after handling the first matching command

def setup(bot):
    if "CommandsPlugin" in bot.cogs:
        bot.remove_cog("CommandsPlugin")
    bot.add_cog(CommandsPlugin(bot))
