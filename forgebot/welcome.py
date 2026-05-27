"""
welcome.py
Handles new members joining the server.

Custom welcome embed sent in the system channel
Automatic assignment of a default role
Logging in #moderation-logs

Integrated into bot.py via setup_welcome(client)
"""

import discord
from config import (
    WELCOME_ROLE_NAME,
    LOG_CHANNEL_NAME,
)


def setup_welcome(client: discord.Client):
    """Registers the on_member_join event on the Discord client."""

    @client.event
    async def on_member_join(member: discord.Member):
        guild = member.guild

        # 1. Attribution du rôle de base 
        role = discord.utils.get(guild.roles, name=WELCOME_ROLE_NAME)
        if role:
            try:
                await member.add_roles(role, reason="Rôle attribué automatiquement à l'arrivée")
            except discord.Forbidden:
                pass  # bot doesn't have permission to assign roles, ignore silently

        # 2. Embed of welcome message in system channel or fallback to a general channel
        channel = guild.system_channel or discord.utils.get(
            guild.text_channels,
            name="général"
        ) or next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )

        if channel:
            embed = discord.Embed(
                title=f"👋 Bienvenue sur **{guild.name}** !",
                description=(
                    f"Salut {member.mention}, on est super content de t'accueillir ici ! 🎉\n\n"
                    f"📌 Consulte les règles du serveur avant de commencer.\n"
                    f"💬 N'hésite pas à te présenter dans le canal dédié.\n\n"
                    f"Bonne aventure parmi nous ! 🚀"
                ),
                color=discord.Color(0x57F287)
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"Membre #{guild.member_count}",
                icon_url=guild.icon.url if guild.icon else None
            )
            await channel.send(embed=embed)

        #  3. Log in #moderation-logs 
        log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if log_channel:
            log_embed = discord.Embed(
                title="📥 Nouveau membre",
                color=discord.Color(0x5865F2)
            )
            log_embed.add_field(name="Utilisateur", value=f"{member} (`{member.id}`)", inline=False)
            log_embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
            log_embed.add_field(name="Membres total", value=str(guild.member_count), inline=True)
            log_embed.set_thumbnail(url=member.display_avatar.url)
            await log_channel.send(embed=log_embed)