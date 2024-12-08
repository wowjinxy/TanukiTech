import aiohttp

async def change_title_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)

    if user_level < 1:  # moderator or above
        await ctx.send("You do not have permission to change the title.")
        return

    # Expected format: !title New Title Here
    parts = ctx.message.content.strip().split(" ", 1)
    if len(parts) < 2:
        await ctx.send("Usage: !title <new title>")
        return

    new_title = parts[1]

    oauth_data = bot.oauth_data
    oauth_token = oauth_data.get("oauth_token")
    broadcaster_id = oauth_data.get("broadcaster_id")
    client_id = oauth_data.get("client_id")

    if not all([oauth_token, broadcaster_id, client_id]):
        await ctx.send("Missing OAuth configuration. Cannot change title.")
        return

    success = await update_title(broadcaster_id, new_title, oauth_token, client_id)
    if success:
        await ctx.send(f"Title changed to: {new_title}")
    else:
        await ctx.send("Failed to update the title. Check logs and scopes.")

async def update_title(broadcaster_id, new_title, oauth_token, client_id):
    url = "https://api.twitch.tv/helix/channels"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json"
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "title": new_title
    }

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, headers=headers, json=payload) as response:
            if response.status == 204:
                return True
            else:
                print(f"Failed to update title: {response.status} - {await response.text()}")
                return False

COMMAND_DEFINITION = {
    "!title": {
        "response": None,
        "level": 1,  # Moderator or above
        "aliases": [],
        "callback": change_title_callback
    }
}
