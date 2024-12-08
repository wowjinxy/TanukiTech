import aiohttp
import json

async def create_poll_callback(ctx, bot):
    plugin = bot.cogs["CommandsPlugin"]
    user_level = plugin.get_user_level(ctx.author)
    if user_level < 1:  # moderators or broadcaster
        await ctx.send("You do not have permission to create polls.")
        return

    # Expected format: !poll "Title" "Option1" "Option2" ... [duration in seconds]
    # e.g. !poll "Favorite Game?" "Zelda" "Mario" "Metroid" 60
    # The last argument is duration, everything else before that is considered title and options.
    
    parts = ctx.message.content.strip().split(" ")
    # The command is tricky since we have quotes. Let's assume the user formats it with quotes.
    # Better to parse quotes properly. If user doesn't provide quotes, we must define a simpler format.
    # For simplicity, let's say user does: !poll "Title with spaces" "Option 1" "Option 2" 60
    # We'll need to parse quoted strings. Here's a simple approach using 'shlex':
    
    import shlex
    parsed = shlex.split(ctx.message.content)
    # parsed will be something like ["!poll", "Title with spaces", "Option 1", "Option 2", "60"]
    if len(parsed) < 4:
        await ctx.send("Usage: !poll \"Title\" \"Option1\" \"Option2\" [\"Option3\" ...] duration_in_seconds")
        return

    # The last element should be duration
    try:
        duration = int(parsed[-1])
    except ValueError:
        await ctx.send("Please provide a valid duration in seconds as the last argument.")
        return

    title = parsed[1]  # The first quoted string after !poll is title
    choices = parsed[2:-1]  # Everything between title and the duration is an option
    
    if len(choices) < 2 or len(choices) > 5:
        await ctx.send("You must provide between 2 to 5 options.")
        return

    oauth_data = bot.oauth_data
    oauth_token = oauth_data.get("oauth_token")
    broadcaster_id = oauth_data.get("broadcaster_id")
    client_id = oauth_data.get("client_id")

    if not all([oauth_token, broadcaster_id, client_id]):
        await ctx.send("Missing OAuth configuration. Cannot create poll.")
        return

    success = await create_poll(broadcaster_id, title, choices, duration, oauth_token, client_id)
    if success:
        await ctx.send(f"Poll created: {title}")
    else:
        await ctx.send("Failed to create the poll. Check logs and token scopes.")

async def create_poll(broadcaster_id, title, choices, duration, oauth_token, client_id):
    url = "https://api.twitch.tv/helix/polls"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json"
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "title": title,
        "choices": [{"title": c} for c in choices],
        "duration": duration
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                # If we want, we can inspect `data` for poll info
                return True
            else:
                error_text = await response.text()
                print(f"Failed to create poll: {response.status} - {error_text}")
                return False

COMMAND_DEFINITION = {
    "!poll": {
        "response": None,
        "level": 1,  # moderator or above
        "aliases": [],
        "callback": create_poll_callback
    }
}
