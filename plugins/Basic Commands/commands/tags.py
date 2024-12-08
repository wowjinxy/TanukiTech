import aiohttp

async def list_tags_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)
    # Anyone can see the current tags
    tags = await fetch_current_tags(bot)
    if tags is None:
        await ctx.send("Failed to fetch current tags.")
        return

    if tags:
        await ctx.send("Current tags: " + ", ".join(tags))
    else:
        await ctx.send("No tags currently set.")

async def add_tag_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)
    if user_level < 1:
        await ctx.send("You do not have permission to modify tags.")
        return

    parts = ctx.message.content.strip().split(" ", 2)
    if len(parts) < 3:
        await ctx.send("Usage: !tags add <tag_id>")
        return

    tag_id = parts[2]
    current_tags = await fetch_current_tags(bot)
    if current_tags is None:
        await ctx.send("Failed to fetch current tags.")
        return

    if tag_id in current_tags:
        await ctx.send("That tag is already set.")
        return

    current_tags.append(tag_id)
    success = await update_tags(bot, current_tags)
    if success:
        await ctx.send(f"Tag '{tag_id}' added successfully.")
    else:
        await ctx.send("Failed to update tags. Check logs and scopes.")

async def remove_tag_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)
    if user_level < 1:
        await ctx.send("You do not have permission to modify tags.")
        return

    parts = ctx.message.content.strip().split(" ", 2)
    if len(parts) < 3:
        await ctx.send("Usage: !tags remove <tag_id>")
        return

    tag_id = parts[2]
    current_tags = await fetch_current_tags(bot)
    if current_tags is None:
        await ctx.send("Failed to fetch current tags.")
        return

    if tag_id not in current_tags:
        await ctx.send("That tag is not currently set.")
        return

    current_tags.remove(tag_id)
    success = await update_tags(bot, current_tags)
    if success:
        await ctx.send(f"Tag '{tag_id}' removed successfully.")
    else:
        await ctx.send("Failed to update tags.")

async def fetch_current_tags(bot):
    oauth_data = bot.oauth_data
    oauth_token = oauth_data.get("oauth_token")
    broadcaster_id = oauth_data.get("broadcaster_id")
    client_id = oauth_data.get("client_id")

    if not all([oauth_token, broadcaster_id, client_id]):
        print("Missing OAuth configuration for tags.")
        return None

    url = f"https://api.twitch.tv/helix/channels?broadcaster_id={broadcaster_id}"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": client_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and data["data"]:
                    return data["data"][0].get("tag_ids", [])
            else:
                print(f"Failed to fetch current tags: {response.status} - {await response.text()}")
                return None

async def update_tags(bot, tags):
    oauth_data = bot.oauth_data
    oauth_token = oauth_data.get("oauth_token")
    broadcaster_id = oauth_data.get("broadcaster_id")
    client_id = oauth_data.get("client_id")

    if not all([oauth_token, broadcaster_id, client_id]):
        print("Missing OAuth configuration for tag updates.")
        return False

    url = "https://api.twitch.tv/helix/channels"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json"
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "tag_ids": tags
    }

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, headers=headers, json=payload) as response:
            if response.status == 204:
                return True
            else:
                print(f"Failed to update tags: {response.status} - {await response.text()}")
                return False

COMMAND_DEFINITION = {
    "!tags": {
        "response": None,
        "level": 0,
        "aliases": [],
        "callback": list_tags_callback  # Changed from list_commands_callback to list_tags_callback
    },
    "!tags add": {
        "response": None,
        "level": 1,
        "aliases": [],
        "callback": add_tag_callback
    },
    "!tags remove": {
        "response": None,
        "level": 1,
        "aliases": [],
        "callback": remove_tag_callback
    }
}
