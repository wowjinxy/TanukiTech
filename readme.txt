# Tanuki Tech Bot

Tanuki Tech Bot is a modular and customizable Twitch bot designed to enhance chat interaction and stream management. Built with a plugin-based architecture, it allows users to dynamically load and manage features, create custom commands, and interact with the Twitch API for advanced functionality. Ideal for streamers seeking a powerful yet user-friendly bot, Tanuki Tech Bot offers permission-based command handling, alias support, and the ability to extend its capabilities with minimal effort. Whether you're managing your community or adding fun chat interactions, Tanuki Tech Bot is your go-to solution for Twitch automation.

---

## Features

- **Modular Plugin Architecture**: Extend functionality by adding, removing, or reloading plugins at runtime.
- **Dynamic Command Management**: Create, modify, and remove custom commands directly from chat.
- **Twitch API Integration**: 
  - Update stream category and title via `!game` and `!title`.
  - Manage tags, run polls, and retrieve chatters using official Helix endpoints.
- **Permission-Based Commands**: Grant or restrict commands based on user roles (Viewer, Moderator, Broadcaster).
- **Alias Support**: Assign multiple aliases to commands for easier recall.
- **Interactive Features**:
  - Roll dice of any size and quantity (`!d <sides> [count]`).
  - Choose a random viewer winner with `!winner`.
  - Shout out other streamers using `!so`.
  
---

## Requirements

- Python 3.8+
- Twitch API Credentials:
  - Client ID
  - OAuth Token (with required scopes)
- Recommended: Virtual environment for dependency management

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/tanuki-tech-bot.git
   cd tanuki-tech-bot
   ```

2. Create and activate a virtual environment:
   ```bash
	python -m venv venv
	source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your Twitch credentials:
   - Create a `.env` file in the root directory and add the following:
     ```env
     TWITCH_CLIENT_ID=your_client_id
     TWITCH_OAUTH_TOKEN=your_oauth_token
     ```

---

## Usage

1. Start the bot:
   ```bash
   Run TanukiTech.bat
   ```

2. Interact with the bot in your Twitch channel. The bot automatically joins the specified channels based on your Twitch configuration.

3. Reload plugins on the fly by pressing `F5` while the bot is running.

---

## Built-in Commands

### General Commands
- **!greet**: Greets the user.
- **!info**: Provides information about the bot.
- **!help**: Lists basic help details.
- **!commands**: Displays available commands based on user permissions.
- **!dice / !d**: Shows how to roll dice (e.g. !d 6 4 rolls four d6 and sums them).

### Stream Management
- **!addcommand [command] [response] [aliases...]**: Adds a new command dynamically.
- **!game [game_name]**: Changes the stream's game category (Broadcaster-only).
- **!title <new title>**: Update the stream’s title (Moderator or Broadcaster).
- **!commercial**: Runs a Twitch ad (Moderator-only).
- **!poll "Title" "Option1" "Option2" ... duration**: Create a channel poll.
- **!winner**: Randomly select a viewer from the chat.
- **!so <username> <custom message>**: Send a shoutout to another streamer, including a custom message.
- **!d <sides> [count]**: Roll one or multiple dice (e.g. !d 20 2 rolls two d20 and sums the result).

---

## Creating Plugins

1. Create a new Python file in the `plugins` directory (e.g., `my_plugin.py`).

2. Define the `metadata` and plugin functionality:
   ```python
   from twitchio.ext import commands

   metadata = {
       "name": "My Custom Plugin",
       "version": "1.0",
       "author": "YourName",
       "description": "Description of your plugin."
   }

   class MyPlugin(commands.Cog):
       def __init__(self, bot):
           self.bot = bot

       @commands.command(name="mycommand")
       async def my_command(self, ctx):
           await ctx.send("This is my custom command!")

   def setup(bot):
       bot.add_cog(MyPlugin(bot))
   ```

3. Restart the bot or reload plugins with `F5` to activate your new plugin.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your fork.
4. Submit a pull request describing your changes.

---

## License

This project is released into the public domain under [The Unlicense](https://unlicense.org/). You are free to copy, modify, and distribute this software without any conditions.

---

## Support

For issues or feature requests, please open an issue on GitHub or contact the repository maintainer.

