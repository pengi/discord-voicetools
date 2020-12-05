VoiceTools
==========

Discord bot to simplify voice tools

This is currently not intended for public use, but for private servers, which means UI and configuration may change or be added without further notice.

Role for voice channel
----------------------

When added to server and given "Manage Roles" permission, for every user joining or leaving a voice chat, it will automatically remove all roles beginning with the string "voice " and add a role "voice Channename" if exists

This makes it possible to have a chat that is only visible for people actually in a voice channel, making it possible to share for example invites to games

Start the bot
-------------

To start the bot, install all dependencies and enter virtualenv.

Set the environment variable DISCORD_TOKEN to the token for the bot and start main.py