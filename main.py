import discord

class VoiceTools(discord.Client):
    async def on_connect(self):
        print("on_connect")
        
    async def on_disconnect(self):
        print("on_disconnect")
        
    async def on_ready(self):
        print("on_ready")
        
    async def on_error(self, event, *argv, **kwargs):
        print("on_error", event, argv, kwargs)
    
    async def on_voice_state_update(self, member, before, after):
        print("on_voice_state_update", member, before, after)
        
        roles_remove = []
        roles_add = []
        
        next_voice_role = None
        if after.channel:
            next_voice_role = "voice " + after.channel.name

        print(next_voice_role)

        # Workaround, refetch since discord.js seems to have problem with role caches
        fetched_member = await member.guild.fetch_member(member.id)
        # print("fetched", fetched_member)
        if not fetched_member:
            return

        # Remove all voice roles per default
        for role in fetched_member.roles:
            # print("role", role)
            if role.name.startswith("voice "):
                if role.name != next_voice_role:
                    roles_remove.append(role)
        
        if next_voice_role:
            for role in member.guild.roles:
                if role.name == next_voice_role:
                    roles_add.append(role)
        
        if len(roles_add) > 0:
            await fetched_member.add_roles(*roles_add, atomic=True)
        if len(roles_remove) > 0:
            await fetched_member.remove_roles(*roles_remove, atomic=True)

if __name__ == '__main__':
    import os
    client = VoiceTools()
    client.run(os.environ['DISCORD_TOKEN'])
