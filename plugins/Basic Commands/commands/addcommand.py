async def add_command_callback(ctx, bot, cmd_name, cmd_response, aliases):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)

    if user_level < 1:
        await ctx.send("You do not have permission to add commands.")
        return

    if cmd_name in plugin.CUSTOM_COMMANDS:
        await ctx.send(f"The command '{cmd_name}' already exists.")
        return

    plugin.CUSTOM_COMMANDS[cmd_name] = {
        "response": cmd_response,
        "level": 0,
        "aliases": aliases
    }
    await ctx.send(f"Command '{cmd_name}' has been added successfully.")

COMMAND_DEFINITION = {
    "!addcommand": {
        "response": None,
        "level": 1,
        "aliases": [],
        "callback": add_command_callback
    }
}
