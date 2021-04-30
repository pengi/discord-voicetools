VoiceTools
==========

Discord bot to simplify voice tools

The bot is intended to be stateless and without configuration, which means all roles are updated and resolved at runtime.

Configuration and behavior only depends on naming of roles and channels to connect the behavior together

Scalability
-----------

It is built for smaller servers with just a few active voice channels, so no caching is implemented. That being said, it should probably handle a few bigger too.

To scale it up, more advanced caching of roles and stats channel is needed, which is out of scope for this project, to keep the project simple.

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

Timezone can be configured for the channel setting the topic in the stats channel to include "tz:timezone", for example "tz:CET". The timezone should be a name recognizable by pytz library, and defaults to UTC

Static message
--------------

To add static messages to a channel, write a message as an administrator, prefixing the message with "-static"

The bot will then create a message, copy the content and delete the original message

To edit a static message, reply to the message to be updated, and type "-static" and the new message

Tip: Use the -export command below to get the old content

Export original message
-----------------------

To get the unformatted version of a message, reply to the message as an administrator an type "-export". The bot will reply with a file download of the content of the message

Start the bot
-------------

To start the bot, install all dependencies and enter virtualenv.

Set the environment variable DISCORD_TOKEN to the token for the bot and start main.py

An example start script is available as start_example.sh

License
-------

Discord Voicetools by pengi
Copyright (c) 2021 pengi

Contact: max@pengi.se

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by  
the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program. If not, see <http://www.gnu.org/licenses/>.
