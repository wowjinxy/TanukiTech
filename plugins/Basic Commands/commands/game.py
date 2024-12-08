import aiohttp

async def change_game_callback(ctx, bot, game_name):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)
    if user_level < 1:  # moderator level
        await ctx.send("You do not have permission to change the category.")
        return

    oauth_data = bot.oauth_data
    oauth_token = oauth_data.get("oauth_token")
    broadcaster_id = oauth_data.get("broadcaster_id")
    client_id = oauth_data.get("client_id")

    if not all([oauth_token, broadcaster_id, client_id]):
        await ctx.send("Missing OAuth configuration. Cannot change category.")
        return

    game_id = await fetch_game_id(game_name, oauth_token, client_id)
    if not game_id:
        await ctx.send(f"Could not find a category for '{game_name}'. Check spelling and try again.")
        return

    success = await update_category(broadcaster_id, game_id, oauth_token, client_id)
    if success:
        await ctx.send(f"Successfully changed the category to '{game_name}'.")
    else:
        await ctx.send("Failed to update the category. Check logs and token scopes.")

async def fetch_game_id(game_name: str, oauth_token: str, client_id: str):
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

async def update_category(broadcaster_id: str, game_id: str, oauth_token: str, client_id: str):
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

COMMAND_DEFINITION = {
    "!game": {
        "response": None,
        "level": 1,
        "aliases": [],
        "callback": change_game_callback
    }
}
