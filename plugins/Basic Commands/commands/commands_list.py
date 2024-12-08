async def list_commands_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)
    available_commands = []

    for command, details in plugin.CUSTOM_COMMANDS.items():
        if details["level"] <= user_level:
            available_commands.append(command)
            available_commands.extend(details.get("aliases", []))

    if "!commands" not in available_commands:
        available_commands.append("!commands")

    await ctx.send(", ".join(available_commands))

COMMAND_DEFINITION = {
    "!commands": {
        "response": None,
        "level": 0,
        "aliases": [],
        "callback": list_commands_callback
    }
}
