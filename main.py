import json
import os
import importlib.util
import asyncio
import traceback
import aiohttp
from twitchio.ext import commands

async def fetch_broadcaster_id(oauth_token, client_id, username):
    """Fetch the broadcaster's user ID from the Helix API using their username."""
    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": client_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["id"]
            else:
                print(f"Failed to fetch broadcaster_id: {response.status} - {await response.text()}")
    return None

def load_oauth():
    """Load OAuth credentials from oauth.json."""
    while True:
        try:
            if not os.path.exists("oauth.json"):
                raise FileNotFoundError

            with open("oauth.json", "r") as f:
                oauth_data = json.load(f)

            # Validate essential keys
            if "oauth_token" not in oauth_data or "channels" not in oauth_data:
                raise ValueError("oauth.json must contain 'oauth_token' and 'channels' keys.")

            if "client_id" not in oauth_data:
                raise ValueError("oauth.json must contain 'client_id' key for Helix calls.")

            return oauth_data
        except FileNotFoundError:
            print("ERROR: Missing 'oauth.json'. Please create this file with your OAuth token and required details.")
            print("Example:")
            print(json.dumps({"oauth_token": "your_token_here", "channels": ["your_channel"], "client_id": "your_client_id"}, indent=4))
        except ValueError as e:
            print(f"ERROR: {e}")
        except json.JSONDecodeError:
            print("ERROR: 'oauth.json' is not valid JSON. Please check the file format.")

        input("Press Enter to try again...")

class TanukiTechBot(commands.Bot):
    def __init__(self, oauth_data):
        print("============================================")
        print("Welcome to Tanuki Tech Bot!")
        print("Initializing...")
        print("============================================")

        self.oauth_data = oauth_data
        self.channels = oauth_data.get("channels", [])

        super().__init__(
            token=oauth_data.get("oauth_token", ""),
            prefix="!",
            initial_channels=self.channels
        )
        self.plugins = []

    def load_plugins(self):
        """
        Load or reload plugins from the plugins folder.
        """
        plugins = []
        PLUGINS_FOLDER = "plugins"

        if not os.path.exists(PLUGINS_FOLDER):
            os.makedirs(PLUGINS_FOLDER)

        for root, _, files in os.walk(PLUGINS_FOLDER):
            for filename in files:
                if filename.endswith(".py"):
                    plugin_path = os.path.join(root, filename)
                    spec = importlib.util.spec_from_file_location(filename[:-3], plugin_path)
                    module = importlib.util.module_from_spec(spec)

                    try:
                        spec.loader.exec_module(module)

                        if hasattr(module, "setup"):
                            # If plugin is already loaded as a Cog, remove it before reloading
                            cog_name = getattr(module, 'metadata', {}).get('name', filename)
                            if cog_name in self.cogs:
                                self.remove_cog(cog_name)

                            module.setup(self)
                            plugins.append(module)
                            print(f"Loaded plugin: {getattr(module, 'metadata', {}).get('name', filename)}")
                        else:
                            print(f"Plugin '{filename}' does not have a setup function.")
                    except Exception as e:
                        print(f"Failed to load plugin '{filename}': {e}")
                        traceback.print_exc()

        return plugins

    async def event_ready(self):
        print("============================================")
        print(f"Logged in as {self.nick}")
        print(f"Connected to channel(s): {', '.join(self.channels)}")
        print("============================================")

        # Load plugins
        self.plugins = self.load_plugins()
        print(f"Loaded {len(self.plugins)} plugins.")

        # Attempt to listen for plugin reload via keyboard input (F5)
        await self.attempt_keyboard_reload()

    async def attempt_keyboard_reload(self):
        """Try importing 'keyboard' and if successful, listen for F5 to reload plugins."""
        print("Attempting to enable plugin reloading via F5...")
        try:
            import keyboard
            self.keyboard_available = True
            self.loop.create_task(self.listen_for_reload())
            print("Plugin reloading via F5 enabled.")
        except ImportError:
            print("The `keyboard` library is not installed. Install it with `pip install keyboard` to enable F5 reload functionality.")
            print("Plugin reloading via F5 is disabled.")

    async def listen_for_reload(self):
        """Listen for F5 key press to reload plugins dynamically if `keyboard` is available."""
        if not getattr(self, 'keyboard_available', False):
            return
        import keyboard
        print("Press F5 to reload plugins at any time.")

        while True:
            try:
                await asyncio.sleep(0.1)
                if keyboard.is_pressed("F5"):
                    print("Reloading plugins...")
                    self.plugins = self.load_plugins()
                    print("Plugins reloaded successfully.")
            except Exception as e:
                print(f"Error during plugin reload: {e}")

    async def event_message(self, message):
        if message.echo:
            return

        await self.handle_commands(message)

    @commands.command(name="hello")
    async def hello_command(self, ctx):
        await ctx.send(f"Hello, {ctx.author.name}!")

    @commands.command(name="reloadplugins")
    async def reload_plugins_command(self, ctx):
        """Reload plugins from chat. Only the broadcaster can do this."""
        if ctx.author.is_broadcaster:
            self.plugins = self.load_plugins()
            await ctx.send("Plugins reloaded successfully.")
        else:
            await ctx.send("Only the broadcaster can reload plugins.")


if __name__ == "__main__":
    # Load OAuth data first
    oauth_data = load_oauth()

    # Attempt to fetch broadcaster_id before creating the bot
    broadcaster_name = oauth_data["channels"][0] if oauth_data["channels"] else None
    if broadcaster_name:
        # Instead of calling asyncio.run() here, we'll create a temporary loop:
        temp_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(temp_loop)
        broadcaster_id = temp_loop.run_until_complete(fetch_broadcaster_id(
            oauth_data["oauth_token"], oauth_data["client_id"], broadcaster_name
        ))
        temp_loop.close()

        # After we are done fetching, we can create a fresh event loop for the bot.
        asyncio.set_event_loop(asyncio.new_event_loop())

        if broadcaster_id:
            oauth_data["broadcaster_id"] = broadcaster_id
        else:
            print(f"Could not fetch broadcaster_id for {broadcaster_name}.")
    else:
        print("No channels found in oauth.json, unable to fetch broadcaster_id.")

    # Now instantiate the bot after ensuring a default event loop exists.
    asyncio.set_event_loop(asyncio.new_event_loop())  # Create and set a clean loop for the bot
    bot = TanukiTechBot(oauth_data)
    bot.run()
