"""
moderation.py
Autonomous and intelligent moderation based on a banned word list.

4-level severity system:
  Level 1 — DM warning            (mild language)
  Level 2 — 10-minute mute        (moderate language)
  Level 3 — Server kick           (seriously offensive content)
  Level 4 — Permanent ban         (hate speech / threats)

Every action is logged in #logs-modération.
The offending message is automatically deleted.

Hooked into bot.py via setup_moderation(client).
"""

import asyncio
import datetime

import discord

from config import LOG_CHANNEL_NAME, MUTE_DURATION_MINUTES, MUTE_ROLE_NAME


# Banned word list by severity level 
# Add or remove words here to suit your server's needs.

BANNED_WORDS: dict[int, list[str]] = {
    1: [  # Warning — mild offensive language
        "merde", "putain", "con", "connard", "connasse",
        "idiot", "imbécile", "débile", "abruti", "crétin",
    ],
    2: [  # 10-min mute — direct insults
        "enculé", "fils de pute", "salope", "pute", "bâtard",
        "fdp", "tg", "va te faire", "ferme ta gueule",
    ],
    3: [  # Kick — highly offensive content
        "pédé", "tapette", "tranny", "nègre", "rebeu",
        "suicide toi", "tue toi", "crève",
    ],
    4: [  # Ban — hate speech, threats, illegal content
        "hitler", "heil", "terroriste", "attentat", "viol",
        "pédo", "pédophile", "je vais te tuer", "je vais te retrouver", "nigger",
    ],
}


# DM messages sent to the user based on their sanction level 

SANCTION_MESSAGES: dict[int, str] = {
    1: (
        "⚠️ **Warning**\n\n"
        "Your message on **{guild}** was deleted because it contains inappropriate language.\n"
        "Please respect the server rules. Repeated offences will result in a heavier sanction."
    ),
    2: (
        "🔇 **You have been muted**\n\n"
        "Your message on **{guild}** was deleted and you have been muted for **{duration} minutes**.\n"
        "Respect the server rules to avoid a kick or a ban."
    ),
    3: (
        "👢 **You have been kicked from the server**\n\n"
        "You were kicked from **{guild}** following an offensive message.\n"
        "You may rejoin, but any further violation will result in a permanent ban."
    ),
    4: (
        "🔨 **You have been permanently banned**\n\n"
        "You were banned from **{guild}** for hateful or threatening content.\n"
        "This decision is final."
    ),
}


# Severity detection 

def _detect_level(content: str) -> int:
    """
    Scan a message's content and return its severity level (1–4).
    Checks from the most severe level down to prioritise the worst offence.

    Args:
        content (str): The raw text content of the Discord message.

    Returns:
        int: Severity level between 1 and 4, or 0 if no banned word is found.
    """
    content_lower = content.lower()

    for level in [4, 3, 2, 1]:
        for word in BANNED_WORDS[level]:
            if word in content_lower:
                return level

    return 0  # No banned word detected


# Mute role helper 

async def _get_or_create_mute_role(guild: discord.Guild) -> discord.Role | None:
    """
    Retrieve the mute role from the guild, or create it if it does not exist.
    The role is configured to block message sending and reactions in all text channels.

    Args:
        guild (discord.Guild): The Discord guild to operate on.

    Returns:
        discord.Role | None: The mute role, or None if creation failed due to missing permissions.
    """
    role = discord.utils.get(guild.roles, name=MUTE_ROLE_NAME)

    if not role:
        try:
            role = await guild.create_role(
                name=MUTE_ROLE_NAME,
                reason="Mute role automatically created by ForgeBot"
            )
            # Apply send_messages=False to every existing text channel
            for channel in guild.text_channels:
                try:
                    await channel.set_permissions(
                        role,
                        send_messages=False,
                        add_reactions=False,
                        reason="Mute: automatic permission override"
                    )
                except discord.Forbidden:
                    pass  # Skip channels where permissions cannot be changed
        except discord.Forbidden:
            return None  # Cannot create roles — insufficient permissions

    return role


# Moderation log helper

async def _log_action(
    guild: discord.Guild,
    member: discord.Member,
    level: int,
    message_content: str,
    action: str,
) -> None:
    """
    Send a moderation log embed to the configured log channel.
    Does nothing silently if the log channel is not found.

    Args:
        guild (discord.Guild): The guild where the action took place.
        member (discord.Member): The member who triggered the sanction.
        level (int): The severity level of the offence (1–4).
        message_content (str): The content of the deleted message (truncated to 200 chars).
        action (str): A short description of the action taken (e.g. 'Kick', 'Mute 10 min').
    """
    log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if not log_channel:
        return

    colors = {
        1: discord.Color.yellow(),
        2: discord.Color.orange(),
        3: discord.Color(0xFF6B35),
        4: discord.Color.red(),
    }
    icons = {1: "⚠️", 2: "🔇", 3: "👢", 4: "🔨"}

    embed = discord.Embed(
        title=f"{icons[level]} Automatic sanction — Level {level}",
        color=colors[level],
        timestamp=datetime.datetime.utcnow(),
    )
    embed.add_field(name="User",            value=f"{member} (`{member.id}`)",      inline=True)
    embed.add_field(name="Action",          value=action,                           inline=True)
    embed.add_field(name="Deleted message", value=f"||{message_content[:200]}||",  inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="ForgeBot Moderation")

    await log_channel.send(embed=embed)


# Sanction dispatcher 

async def _apply_sanction(
    guild: discord.Guild,
    member: discord.Member,
    level: int,
    message_content: str,
) -> None:
    """
    Apply the appropriate sanction to a member based on the offence severity level.

    Levels:
        1 — DM warning only (message already deleted before this call).
        2 — Temporary mute, automatically lifted after MUTE_DURATION_MINUTES.
        3 — Kick from the server.
        4 — Permanent ban with 1-day message deletion.

    Args:
        guild (discord.Guild): The guild where the offence occurred.
        member (discord.Member): The offending member.
        level (int): The detected severity level (1–4).
        message_content (str): The content of the deleted message, used for logging.
    """
    if level == 1:
        # Level 1: warning already sent via DM — just log the action
        await _log_action(guild, member, level, message_content, "Warning (DM)")

    elif level == 2:
        # Level 2: apply temporary mute role, schedule automatic removal
        mute_role = await _get_or_create_mute_role(guild)
        if mute_role:
            try:
                await member.add_roles(mute_role, reason="ForgeBot: automatic mute — level 2")
                await _log_action(guild, member, level, message_content, f"Mute {MUTE_DURATION_MINUTES} min")

                async def _unmute() -> None:
                    """Coroutine that removes the mute role after the configured delay."""
                    await asyncio.sleep(MUTE_DURATION_MINUTES * 60)
                    try:
                        await member.remove_roles(mute_role, reason="ForgeBot: automatic mute expired")
                    except Exception:
                        pass  # Member may have left the server in the meantime

                asyncio.create_task(_unmute())

            except discord.Forbidden:
                await _log_action(guild, member, level, message_content, "Mute failed (permissions)")

    elif level == 3:
        # Level 3: kick the member from the server
        try:
            await member.kick(reason="ForgeBot: automatic kick — offensive content")
            await _log_action(guild, member, level, message_content, "Kick")
        except discord.Forbidden:
            await _log_action(guild, member, level, message_content, "Kick failed (permissions)")

    elif level == 4:
        # Level 4: permanently ban the member and delete their recent messages
        try:
            await member.ban(
                reason="ForgeBot: automatic ban — hate speech or threatening content",
                delete_message_days=1,  # Also remove messages from the past 24 hours
            )
            await _log_action(guild, member, level, message_content, "Permanent ban")
        except discord.Forbidden:
            await _log_action(guild, member, level, message_content, "Ban failed (permissions)")


# Shared pre-sanction logic 

async def _handle_offence(message: discord.Message) -> bool:
    """
    Delete the offending message, notify the member via DM, then dispatch the sanction.
    Returns True if the message was offending so the caller can halt further processing.

    Args:
        message (discord.Message): The Discord message to evaluate.

    Returns:
        bool: True if an offence was detected and handled, False otherwise.
    """
    # Skip bots and DMs
    if message.author.bot or message.guild is None:
        return False

    # Administrators are exempt from automated moderation
    if message.author.guild_permissions.administrator:
        return False

    level = _detect_level(message.content)
    if level == 0:
        return False  # Clean message — nothing to do

    guild  = message.guild
    member = message.author

    # Delete the offending message
    try:
        await message.delete()
    except discord.Forbidden:
        pass  # Cannot delete — log the action anyway

    # Notify the member via DM
    dm_text = SANCTION_MESSAGES[level].format(
        guild=guild.name,
        duration=MUTE_DURATION_MINUTES,
    )
    try:
        await member.send(dm_text)
    except discord.Forbidden:
        pass  # DMs disabled by the user — continue with the sanction

    # Dispatch the appropriate sanction
    await _apply_sanction(guild, member, level, message.content)

    return True  # Offence handled — caller should stop further processing


async def check_message(message: discord.Message) -> bool:
    """
    Public entry point called from on_message in bot.py.
    Delegates to _handle_offence and returns its result.

    Args:
        message (discord.Message): The incoming Discord message to check.

    Returns:
        bool: True if the message was offensive and has been handled, False otherwise.
    """
    return await _handle_offence(message)


def setup_moderation(client: discord.Client) -> None:
    """
    Register the moderation on_message event handler on the Discord client.
    Call this once during bot initialisation in bot.py.

    Args:
        client (discord.Client): The Discord client instance to attach the event to.
    """
    @client.event
    async def on_message_moderation(message: discord.Message) -> None:
        """
        Event handler called from on_message in bot.py.
        Analyses each message and applies an automatic sanction if necessary.

        Args:
            message (discord.Message): The Discord message received by the bot.
        """
        await _handle_offence(message)