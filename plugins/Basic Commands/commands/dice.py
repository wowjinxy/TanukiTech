import random

async def roll_dice_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)
    # No permission check needed, everyone can roll dice.
    
    # Expected formats:
    # !d <sides> [count]
    # If count not provided, defaults to 1 die.
    
    parts = ctx.message.content.strip().split()
    if len(parts) < 2:
        await ctx.send("Usage: !d <sides> [count]. For example, !d 6 4 to roll four d6.")
        return

    # parts[0] is "!d", parts[1] is sides, parts[2] if present is count
    sides_str = parts[1]
    if not sides_str.isdigit():
        await ctx.send("Please provide a valid number of sides. Example: !d 6 4")
        return
    
    sides = int(sides_str)
    if sides < 1:
        await ctx.send("Number of sides must be a positive integer.")
        return
    
    count = 1
    if len(parts) > 2:
        count_str = parts[2]
        if not count_str.isdigit():
            await ctx.send("Please provide a valid number of dice. Example: !d 6 4")
            return
        count = int(count_str)
        if count < 1:
            await ctx.send("Number of dice rolled must be at least 1.")
            return
    
    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)
    if count == 1:
        await ctx.send(f"You rolled a {rolls[0]} on a {sides}-sided die.")
    else:
        rolls_str = ", ".join(map(str, rolls))
        await ctx.send(f"You rolled {count}d{sides}: {rolls_str}. Total: {total}")

async def dice_help_callback(ctx, bot):
    await ctx.send(
        "To roll dice, use `!d <sides> [count]`.\n"
        "Examples:\n"
        "`!d 6` rolls one six-sided die.\n"
        "`!d 6 4` rolls four six-sided dice and sums them.\n"
        "`!d 20 2` rolls two twenty-sided dice and sums them.\n"
        "You can use any positive number as sides or count!"
    )

COMMAND_DEFINITION = {
    "!d": {
        "response": None,
        "level": 0,  # Everyone can use it
        "aliases": [],
        "callback": roll_dice_callback
    },
    "!dice": {
        "response": None,
        "level": 0,
        "aliases": [],
        "callback": dice_help_callback
    }
}
