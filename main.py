import discord

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

class VoiceToolGuild:
    """
    Add behaviors to a guild

    Models the behavior of the voice part of the guild, and coordinates
    behavior objects
    """
    def __init__(self, guild):
        self.guild = guild
        self.behaviors = [
            BehaviorVoiceRole(guild)
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
