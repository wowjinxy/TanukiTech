import json
import os
import importlib.util
import asyncio
from twitchio.ext import commands

class TanukiTechBot(commands.Bot):
    def __init__(self):
        print("============================================")
        print("Welcome to Tanuki Tech Bot!")
        print("Initializing...")
        print("============================================")

        # Load OAuth credentials
        oauth_data = self.load_oauth()

        self.channels = oauth_data.get("channels", [])  # Store channels explicitly

        super().__init__(
            token=oauth_data.get("oauth_token", ""),  # OAuth token
            prefix="!",  # Command prefix
            initial_channels=self.channels  # Pass channels to the bot
        )
        self.plugins = []

    def load_oauth(self):
        """Load OAuth credentials from oauth.json."""
        while True:
            try:
                if not os.path.exists("oauth.json"):
                    raise FileNotFoundError

                with open("oauth.json", "r") as f:
                    oauth_data = json.load(f)

                # Validate file contents
                if "oauth_token" not in oauth_data or "channels" not in oauth_data:
                    raise ValueError("oauth.json must contain 'oauth_token' and 'channels' keys.")

                return oauth_data
            except FileNotFoundError:
                print("ERROR: Missing 'oauth.json'. Please create this file with your OAuth token and required details.")
                print("Example:")
                print(json.dumps({"oauth_token": "your_token_here", "channels": ["your_channel"]}, indent=4))
            except ValueError as e:
                print(f"ERROR: {e}")
            except json.JSONDecodeError:
                print("ERROR: 'oauth.json' is not valid JSON. Please check the file format.")

            input("Press Enter to try again...")

    def load_plugins(self):
        """Load plugins from the plugins folder."""
        plugins = []
        PLUGINS_FOLDER = "plugins"
        REQUIRED_METADATA_KEYS = ["name", "version", "author", "description"]

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

                        if hasattr(module, "metadata"):
                            metadata = module.metadata
                            if all(key in metadata for key in REQUIRED_METADATA_KEYS):
                                plugins.append({"module": module, "metadata": metadata})
                                print(f"Loaded plugin: {metadata['name']} (v{metadata['version']}) by {metadata['author']}")
                            else:
                                print(f"Plugin '{filename}' metadata incomplete.")
                        else:
                            print(f"Plugin '{filename}' lacks a 'metadata' dictionary.")
                    except Exception as e:
                        print(f"Failed to load plugin '{filename}': {e}")

        return plugins

    async def event_ready(self):
        print("============================================")
        print(f"Logged in as {self.nick}")
        print(f"Connected to channel(s): {', '.join(self.channels)}")
        print("============================================")

        # Load plugins
        self.plugins = self.load_plugins()
        print(f"Loaded {len(self.plugins)} plugins.")

        # Start listening for plugin reload
        self.loop.create_task(self.listen_for_reload())

    async def listen_for_reload(self):
        """Listen for F5 key press to reload plugins dynamically."""
        print("Press F5 to reload plugins at any time.")
        try:
            import keyboard  # Requires the `keyboard` package
        except ImportError:
            print("The `keyboard` library is required for plugin reloading. Install it with `pip install keyboard`.")
            return

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

        for plugin in self.plugins:
            if hasattr(plugin["module"], "on_message"):
                await plugin["module"].on_message(self, message)

        await self.handle_commands(message)

    @commands.command(name="hello")
    async def hello_command(self, ctx):
        await ctx.send(f"Hello, {ctx.author.name}!")

if __name__ == "__main__":
    bot = TanukiTechBot()
    bot.run()
