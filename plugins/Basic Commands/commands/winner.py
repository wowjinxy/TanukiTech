import aiohttp
import random

# Seed the random number generator for good measure (usually not needed)
random.seed()

async def pick_winner_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)

    # Require at least a moderator to run this command
    if user_level < 1:
        await ctx.send("You do not have permission to pick a winner.")
        return

    # Fetch a fresh list of chatters each time
    chatter_list = await fetch_chatters_helix(bot)
    if chatter_list is None:
        await ctx.send("Failed to retrieve chatters due to an API error.")
        return

    if not chatter_list:
        await ctx.send("There are no viewers in chat right now.")
        return

    # Optionally exclude the bot itself to avoid choosing the bot as a winner
    bot_name = bot.nick.lower() if bot.nick else None
    filtered_chatters = [user for user in chatter_list if user.lower() != bot_name]

    if not filtered_chatters:
        await ctx.send("No eligible viewers to pick from (excluding the bot).")
        return

    # Print the chatter list for debugging
    print("Chatter list:", filtered_chatters)

    # Randomly choose a winner from the filtered list
    winner = random.choice(filtered_chatters)
    await ctx.send(f"The winner is: {winner}!")

async def fetch_chatters_helix(bot):
    """Fetch chatters using the Helix API endpoint.
       Requires `moderator:read:chatters` scope and a valid moderator_id."""
    oauth_data = bot.oauth_data
    oauth_token = oauth_data.get("oauth_token")
    client_id = oauth_data.get("client_id")
    broadcaster_id = oauth_data.get("broadcaster_id")

    if not all([oauth_token, client_id, broadcaster_id]):
        print("Missing OAuth configuration for fetching chatters.")
        return None

    # Use the broadcaster_id as the moderator_id if the broadcaster is considered a mod in their own channel.
    # Otherwise, provide a known moderator's user ID here.
    moderator_id = broadcaster_id

    url = f"https://api.twitch.tv/helix/chat/chatters?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": client_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                # Extract user_names from the returned data
                chatters = [chatter["user_name"] for chatter in data.get("data", [])]
                return chatters
            else:
                # Log the error for debugging
                error_text = await response.text()
                print(f"Failed to fetch chatters (Status: {response.status}): {error_text}")
                return None

COMMAND_DEFINITION = {
    "!winner": {
        "response": None,
        "level": 1,  # Moderators or above
        "aliases": [],
        "callback": pick_winner_callback
    }
}
