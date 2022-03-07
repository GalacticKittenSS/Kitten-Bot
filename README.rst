============
KITTEN BOT
============
Leaderboard bot allows you to access leaderboard data from steam and create a more competition in your discord servers. Currently Only for Portal 2

Using discord.py
===========
.. image:: https://img.shields.io/pypi/v/discord.py.svg
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/discord.py.svg
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI supported Python versions   
   
A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

Installation
===========

1. Head to `Kitten Bot
<https://discord.com/api/oauth2/authorize?client_id=796667304816410675&permissions=1512567205062&scope=bot>`_

2. Select Sever you wish to add it to.

Getting Started
===========
Kittenbot uses `!` prefix by default but can be changed

Head to the Server and setup the bot using `%Settings`. Many Features may be turned off by default as It requires additional settings to get running.

Customisability
===========

Since Kittenbot v1.2, Kittenbot has had a rewrite to include many customisability settings. These can currently only be altered through the settings command (listed below) or by asking me `GalacticKittenSS` to change them for you. Kittenbot Stores these settings in a json file and will be updated in future to include a better way to edit them with more customisability.

Settings
-----------
The Settings commands can only be edited by a server administrator.

Settings is split into categories:
	- **Commands** : `!Settings Commands [Command Name] [Command Settings]`
	- **Events** : `!Settings Events [Event Name] [Event Settings]`
	- **Delete Messages** : `!Settings Delete_Messages [Should the bot delete the message?]`
	- **Moderator Roles** : `!Settings Moderator_Roles [List of Moderator Role Names]`
	- **Prefix**: `!Settings Prefix [prefix]`

Use `!help Settings [Category]` or `!help Settings [Category] [Command]` for more help

Commands
===========

- **ping**: 
	- Pings the bot. Sends back the latency 
- **say**:
	- Allows Users to make the bot say anything!
- **embed**:
	- Allows Users to send anything in an embed
	- `!embed [Message] [Title] [Description] [Colour (int value)] [Image (https)] [Thumbnail (https)] `
- **who**:
	- Sends back information about a user
	- `!who [User (optional)]`
- And More:
  Use `!help` for more!

Moderation
-----------

Kittenbot has list of basic moderation commands to make moderating easier. Commands are limited to users with specific permissions based on what command  These include:

	- **kick** : Kicks a user
	- **ban** : Bans a User
	- **unban** : Unbans a User
	- **banned** : Get a list of banned users
	- **clear**: Clears a number messages
	- **clearUser** : Clears a number messages from user