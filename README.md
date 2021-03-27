VoiceTools
==========

Discord bot to simplify voice tools

This is currently not intended for public use, but for private servers, which means UI and configuration may change or be added without further notice.

Role for voice channel
----------------------

When added to server and given "Manage Roles" permission, for every user joining or leaving a voice chat, it will automatically remove all roles beginning with the string "voice " and add a role "voice Channename" if exists

This makes it possible to have a chat that is only visible for people actually in a voice channel, making it possible to share for example invites to games

Stats for waiting room voice channel
------------------------------------

Many streamers is using a closed channel for live on stream, and a waiting room for the queue of viewers to get on stream, then drag people from waiting room to live when they should be allowed on stream.

It is quite often hard to keep track of who have been waiting longest in the waiting room. This adds the possibility to have a statistics channel attached to a voice channel to track the waiting time.

Add a channel called #stats-name-of-voice-channel, where "name-of-voice-channel" is replaced with the voice channel name.

Since text channels have much stricter names, only alfanumeric characters and and spaces is kept, converted to lowercase, and spaces to -. duplicate spaces are removed.

A channel with name "⏲ Waiting Room ⏲" will then have the stats channel name #stats-waiting-room

Start the bot
-------------

To start the bot, install all dependencies and enter virtualenv.

Set the environment variable DISCORD_TOKEN to the token for the bot and start main.py

An example start script is available as start_example.sh