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
from datetime import datetime


class BehaviorVoiceRole:
    """
    Behavior voice roles

    Add a role to a member when being joined to a voice channel. The role given
    is has the same name as the voice channel, prefixed with "voice ".

    If the role doesn't exist, the channel is ignored
    """

    def __init__(self, guild):
        self.guild = guild

    def _voice_role_name(self, channel):
        return "voice " + channel.name

    def _role_by_name(self, role_name):
        for role in self.guild.roles:
            if role.name == role_name:
                return role
        return None

    async def voice_leave(self, member, channel):
        # Remove voice role if available. On-stage text channel permissions
        role = self._role_by_name(self._voice_role_name(channel))
        if role:
            print(self.guild, "voice part", role, member)
            await member.remove_roles(role, atomic=True)

    async def voice_join(self, member, channel):
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

    def __init__(self, guild):
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

    async def voice_leave(self, member, channel):
        stchn = self._stats_channel(channel)
        if stchn is None:
            # If no stats channel is available, ignore
            return

        now = datetime.now().strftime("%H:%M:%S")

        async for msg in stchn.history(limit=self.HISTORY_LENGTH):
            if msg.content.startswith("join ") and member.mentioned_in(msg):
                await msg.edit(content="leave " + now + " " + msg.content)

    async def voice_join(self, member, channel):
        stchn = self._stats_channel(channel)
        if stchn is None:
            # If no stats channel is available, ignore
            return

        now = datetime.now().strftime("%H:%M:%S")

        # Don't mention directly, but edit message to the mention. This ensures
        # the user won't get an annoying notificatoin, since only sending a
        # message will trigger the notification
        msg = await stchn.send("(temp)")
        await msg.edit(content="join " + now + "  " + member.mention)


class VoiceToolGuild:
    """
    Add behaviors to a guild

    Models the behavior of the voice part of the guild, and coordinates
    behavior objects
    """

    def __init__(self, guild):
        self.guild = guild
        self.behaviors = [
            BehaviorVoiceRole(guild),
            BehaviorStatsChannel(guild)
        ]

    async def voice_leave(self, member, channel):
        for behavior in self.behaviors:
            if behavior.voice_leave:
                await behavior.voice_leave(member, channel)

    async def voice_join(self, member, channel):
        for behavior in self.behaviors:
            if behavior.voice_join:
                await behavior.voice_join(member, channel)


class VoiceTools(discord.Client):
    def __init__(self):
        super(VoiceTools, self).__init__()

    def _wrap_guild(self, guild):
        # Small scale for now, so don't cache...
        return VoiceToolGuild(guild)

    async def on_connect(self):
        print("on_connect")

    async def on_disconnect(self):
        print("on_disconnect")

    async def on_ready(self):
        print("on_ready")

    async def on_error(self, event, *argv, **kwargs):
        print("on_error", event, argv, kwargs)

    async def on_voice_state_update(self, member, before, after):
        if before.channel and after.channel and before.channel.id == after.channel.id:
            # Change state (mute etc.), rather than channel. Ignore
            return

        # Workaround, refetch since discord.js seems to have problem with role caches
        fetched_member = await member.guild.fetch_member(member.id)
        # print("fetched", fetched_member)
        if not fetched_member:
            return

        # Get our guild storage
        guild = self._wrap_guild(fetched_member.guild)

        if before.channel:
            await guild.voice_leave(fetched_member, before.channel)

        if after.channel:
            await guild.voice_join(fetched_member, after.channel)


if __name__ == '__main__':
    import os
    client = VoiceTools()
    client.run(os.environ['DISCORD_TOKEN'])
