#
# This file is part of the Discord Voicetools by pengi
# Copyright (c) 2021 pengi
#
# Contact: max@pengi.se
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import discord
import re
import io
from datetime import datetime, timezone
import pytz

config_re = re.compile(r'([a-z-_]+):([^ ]*)')


class BehaviorVoiceRole:
    """
    Behavior voice roles

    Add a role to a member when being joined to a voice channel. The role given
    is has the same name as the voice channel, prefixed with "voice ".

    If the role doesn't exist, the channel is ignored
    """

    def __init__(self, client, guild):
        self.client = client
        self.guild = guild

    def _voice_role_name(self, channel):
        return "voice " + channel.name

    def _role_by_name(self, role_name):
        for role in self.guild.roles:
            if role.name == role_name:
                return role
        return None

    async def on_voice_leave(self, member, channel):
        # Remove voice role if available. On-stage text channel permissions
        role = self._role_by_name(self._voice_role_name(channel))
        if role:
            print(self.guild, "voice part", role, member)
            await member.remove_roles(role, atomic=True)

    async def on_voice_join(self, member, channel):
        # Add voice role if available. On-stage text channel permissions
        role = self._role_by_name(self._voice_role_name(channel))
        if role:
            print(self.guild, "voice join", role, member)
            await member.add_roles(role, atomic=True)


class BehaviorStatsChannel:
    """
    Beavior stats channel

    For a waiting room voice channel, it is helpful to get stats out for how
    long people has been waiting.

    Add a text channel with the same name as the voice channel, in the format
    as all alphanumeric letters is in lowercase, all other letters is ignored,
    all spaces is converted to only one, prefixed with "stats-"

    Such as a channel named "⌚ waiting room" will be called #stats-waiting-room
    """
    HISTORY_LENGTH = 200

    def __init__(self, client, guild):
        self.client = client
        self.guild = guild

    def _get_channel_by_name(self, name):
        for channel in self.guild.channels:
            if channel.name == name:
                return channel
        return None

    def _stats_channel(self, voice_channel):
        voice_name = voice_channel.name
        filtered = re.sub(r'[^a-zA-Z0-9 ]+', '', voice_name)
        stats_channel = 'stats-' + \
            re.sub(r'[ ]+', '-', filtered.strip().lower())
        return self._get_channel_by_name(stats_channel)

    def _channel_config(self, channel):
        config = {}
        if channel.topic:
            for k, v in config_re.findall(channel.topic):
                config[k] = v
        return config

    def _format_now(self, config, include_timezone=False):
        tz = timezone.utc
        if 'tz' in config:
            try:
                conf_tz = pytz.timezone(config['tz'])
                tz = conf_tz
            except pytz.exceptions.UnknownTimeZoneError:
                pass
        now_fmt = datetime.now(tz).strftime("%H:%M:%S")
        if include_timezone:
            now_fmt += " " + str(tz)
        return now_fmt

    async def on_voice_leave(self, member, channel):
        stchn = self._stats_channel(channel)
        if stchn is None:
            # If no stats channel is available, ignore
            return

        config = self._channel_config(stchn)
        now = self._format_now(config, False)

        async for msg in stchn.history(limit=self.HISTORY_LENGTH):
            if msg.content.startswith("join ") and member.mentioned_in(msg):
                await msg.edit(content="leave " + now + " " + msg.content)

    async def on_voice_join(self, member, channel):
        stchn = self._stats_channel(channel)
        if stchn is None:
            # If no stats channel is available, ignore
            return

        config = self._channel_config(stchn)
        now = self._format_now(config, True)

        # Don't mention directly, but edit message to the mention. This ensures
        # the user won't get an annoying notificatoin, since only sending a
        # message will trigger the notification
        msg = await stchn.send("(temp)")
        await msg.edit(content="join " + now + "  " + member.mention)


class BehaviorStaticMessages:
    """
    Behaviour to add static messages

    Static messages is messages intended for rules listings, with possibility
    reaction roles.

    All messages posted by this bot can be updated as static messages, so no
    configuration is needed.

    To create a message, a person with administartor permission tags a message
    [static], for this bot to copy and take over the message.

    To change a message, a person with administrator permission replies to the
    message, with the tag [static] to the beginning of the message
    """

    def __init__(self, client, guild):
        self.client = client
        self.guild = guild

    async def on_message(self, message):
        # The bot should never process messages from itself
        if message.author.id == self.client.user.id:
            return

        author = message.author
        channel = message.channel
        perm = message.author.permissions_in(message.channel)

        if not perm.administrator:
            # ignore messages from non-administrators
            return

        # Check if the message is a static message
        if not message.content.startswith('-static '):
            # Not a static message, ignore
            return

        # Get the content without tag
        content = message.content[8:]

        if not content:
            # No empty messages allowed, ignore
            return

        if message.reference:
            # Update message, if possible
            orig_msg = await channel.fetch_message(message.reference.message_id)

            if orig_msg.author.id != self.client.user.id:
                # Not from myself, ignore
                return

            await orig_msg.edit(content=content)
            await message.delete()
        else:
            # No reply, create message
            await channel.send(content)
            await message.delete()


class BehaviorMessageExport:
    """
    Helper to get exports of raw content of messages

    In many cases, editing or copying messages is hard, since only formatted
    messages is easy to access.

    Reply to a message and type "-export" to get the raw message content
    """

    def __init__(self, client, guild):
        self.client = client
        self.guild = guild

    async def on_message(self, message):
        # The bot should never process messages from itself
        if message.author.id == self.client.user.id:
            return

        author = message.author
        channel = message.channel
        perm = message.author.permissions_in(message.channel)

        if not perm.administrator:
            # ignore messages from non-administrators
            return

        # Check if the message is a static message
        if message.content != '-export':
            # Not a static message, ignore
            return

        if not message.reference:
            # not a reply, ignore
            return

        orig_msg = await channel.fetch_message(message.reference.message_id)
        if not orig_msg:
            # No reply, create message
            await channel.send("error: unknown message", delete_after=5.0)
            await message.delete()
            return

        await channel.send(
            "raw",
            reference=orig_msg,
            file=discord.File(io.StringIO(orig_msg.content), 'raw_message.txt')
        )
        await message.delete()


class VoiceToolGuild:
    """
    Add behaviors to a guild

    Models the behavior of the voice part of the guild, and coordinates
    behavior objects
    """

    def __init__(self, client, guild):
        self.behaviors = [
            BehaviorVoiceRole(client, guild),
            BehaviorStatsChannel(client, guild),
            BehaviorStaticMessages(client, guild),
            BehaviorMessageExport(client, guild)
        ]

    async def on_voice_leave(self, member, channel):
        for behavior in self.behaviors:
            try:
                await behavior.on_voice_leave(member, channel)
            except AttributeError:
                pass

    async def on_voice_join(self, member, channel):
        for behavior in self.behaviors:
            try:
                await behavior.on_voice_join(member, channel)
            except AttributeError:
                pass

    async def on_message(self, message):
        for behavior in self.behaviors:
            try:
                await behavior.on_message(message)
            except AttributeError:
                pass


class VoiceTools(discord.Client):
    def __init__(self):
        super(VoiceTools, self).__init__()

    def _wrap_guild(self, guild):
        # Small scale for now, so don't cache...
        return VoiceToolGuild(self, guild)

    async def on_connect(self):
        print("on_connect")

    async def on_disconnect(self):
        print("on_disconnect")

    async def on_ready(self):
        print("on_ready")

    async def on_voice_state_update(self, member, before, after):
        if before.channel and after.channel and before.channel.id == after.channel.id:
            # Change state (mute etc.), rather than channel. Ignore
            return

        # Workaround, refetch since discord.js seems to have problem with role caches
        fetched_member = await member.guild.fetch_member(member.id)
        if not fetched_member:
            return

        # Get our guild storage
        guild = self._wrap_guild(fetched_member.guild)

        if before.channel:
            await guild.on_voice_leave(fetched_member, before.channel)

        if after.channel:
            await guild.on_voice_join(fetched_member, after.channel)

    async def on_message(self, message):
        # Get our guild storage
        guild = self._wrap_guild(message.guild)

        # Call event
        await guild.on_message(message)


if __name__ == '__main__':
    import os
    client = VoiceTools()
    client.run(os.environ['DISCORD_TOKEN'])
