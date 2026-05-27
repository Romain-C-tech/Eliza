import discord


def generate_structure(server_type: str, size: str, special_channels: list) -> dict:
    """
    Generate the complete server structure (categories, channels, roles)
    based on the server type and size.

    Args:
        server_type (str): Type of server ('école', 'gaming', 'communauté').
        size (str): Server size ('small', 'large', etc.).
        special_channels (list): List of additional channel names requested by the user.

    Returns:
        dict: A dictionary containing roles, categories, and channels to create.
    """

    templates = {
        "école": {
            "roles": [
                {"name": "Admin", "color": "0xFF0000"},
                {"name": "Professeur", "color": "0xFFA500"},
                {"name": "Élève", "color": "0x5865F2"},
            ],
            "categories": [
                {
                    "name": "📢 Informations",
                    "channels": [
                        {"name": "annonces", "type": "text", "description": "Official announcements"},
                        {"name": "règles", "type": "text", "description": "Server rules"},
                    ]
                },
                {
                    "name": "📚 Cours",
                    "channels": [
                        {"name": "général", "type": "text", "description": "General discussion"},
                        {"name": "devoirs", "type": "text", "description": "Homework questions"},
                        {"name": "ressources", "type": "text", "description": "Shared resources"},
                    ]
                },
                {
                    "name": "🔊 Vocal",
                    "channels": [
                        {"name": "Cours vocal", "type": "voice"},
                        {"name": "Détente", "type": "voice"},
                    ]
                },
            ]
        },
        "gaming": {
            "roles": [
                {"name": "Admin", "color": "0xFF0000"},
                {"name": "Modérateur", "color": "0xFFA500"},
                {"name": "Joueur", "color": "0x5865F2"},
            ],
            "categories": [
                {
                    "name": "📢 Informations",
                    "channels": [
                        {"name": "annonces", "type": "text", "description": "Announcements"},
                        {"name": "règles", "type": "text", "description": "Rules"},
                    ]
                },
                {
                    "name": "🎮 Gaming",
                    "channels": [
                        {"name": "général", "type": "text", "description": "General discussion"},
                        {"name": "recherche-équipe", "type": "text", "description": "LFG"},
                        {"name": "clips-highlights", "type": "text", "description": "Your best moments"},
                    ]
                },
                {
                    "name": "🔊 Vocal",
                    "channels": [
                        {"name": "Gaming 1", "type": "voice"},
                        {"name": "Gaming 2", "type": "voice"},
                    ]
                },
            ]
        },
        "communauté": {
            "roles": [
                {"name": "Admin", "color": "0xFF0000"},
                {"name": "Modérateur", "color": "0xFFA500"},
                {"name": "Membre", "color": "0x5865F2"},
            ],
            "categories": [
                {
                    "name": "📢 Informations",
                    "channels": [
                        {"name": "annonces", "type": "text", "description": "Announcements"},
                        {"name": "règles", "type": "text", "description": "Rules"},
                    ]
                },
                {
                    "name": "💬 Discussion",
                    "channels": [
                        {"name": "général", "type": "text", "description": "General discussion"},
                        {"name": "présentations", "type": "text", "description": "Introduce yourself!"},
                        {"name": "off-topic", "type": "text", "description": "Off-topic"},
                    ]
                },
                {
                    "name": "🔊 Vocal",
                    "channels": [
                        {"name": "Salon vocal", "type": "voice"},
                    ]
                },
            ]
        },
    }

    # Fall back to the community template if the server type is not recognized
    base = templates.get(server_type, templates["communauté"])

    # Add extra moderation channels for large servers
    if size == "large":
        base["categories"].append({
            "name": "🛡️ Modération",
            "channels": [
                {"name": "logs", "type": "text", "description": "Moderation logs"},
                {"name": "rapports", "type": "text", "description": "Reports"},
            ]
        })

    # Append any special channels requested by the user
    if special_channels:
        base["categories"].append({
            "name": "⭐ Spécial",
            "channels": [
                {"name": ch.lower().replace(" ", "-"), "type": "text", "description": f"Channel {ch}"}
                for ch in special_channels
            ]
        })

    return base


async def build_server(guild: discord.Guild, structure: dict) -> dict:
    """
    Build the Discord server structure from the generated dictionary.
    Creates all roles, categories, and channels defined in the structure.

    Args:
        guild (discord.Guild): The Discord guild (server) to configure.
        structure (dict): The structure dictionary returned by generate_structure().

    Returns:
        dict: A summary containing counts of created items and any errors encountered.
    """
    created = {"categories": 0, "channels": 0, "roles": 0, "errors": []}

    # 1. Create roles
    existing_roles = [r.name.lower() for r in guild.roles]
    for role_data in structure.get("roles", []):
        try:
            # Skip role creation if it already exists on the server
            if role_data["name"].lower() not in existing_roles:
                color_int = int(role_data.get("color", "0x5865F2"), 16)
                await guild.create_role(
                    name=role_data["name"],
                    color=discord.Color(color_int),
                    reason="Created by ForgeBot"
                )
                created["roles"] += 1
        except discord.Forbidden:
            created["errors"].append(f"Missing permission to create role {role_data['name']}")
        except Exception as e:
            created["errors"].append(f"Error creating role {role_data['name']}: {str(e)}")

    # 2. Create categories and their channels
    for cat_data in structure.get("categories", []):
        try:
            category = await guild.create_category(
                name=cat_data["name"],
                reason="Created by ForgeBot"
            )
            created["categories"] += 1

            for ch_data in cat_data.get("channels", []):
                try:
                    # Normalize channel name: lowercase and replace spaces with hyphens
                    ch_name = ch_data["name"].lower().replace(" ", "-")
                    topic = ch_data.get("description", "")

                    if ch_data.get("type") == "voice":
                        # Create a voice channel under the current category
                        await guild.create_voice_channel(
                            name=ch_data["name"],
                            category=category,
                            reason="Created by ForgeBot"
                        )
                    else:
                        # Create a text channel with an optional topic
                        await guild.create_text_channel(
                            name=ch_name,
                            category=category,
                            topic=topic,
                            reason="Created by ForgeBot"
                        )
                    created["channels"] += 1

                except discord.Forbidden:
                    created["errors"].append(f"Missing permission to create #{ch_data['name']}")
                except Exception as e:
                    created["errors"].append(f"Error creating channel {ch_data['name']}: {str(e)}")

        except discord.Forbidden:
            created["errors"].append(f"Missing permission to create category {cat_data['name']}")
        except Exception as e:
            created["errors"].append(f"Error creating category {cat_data['name']}: {str(e)}")

    return created


async def post_welcome_message(guild: discord.Guild, server_name: str, server_type: str):
    """
    Post a welcome embed message in the first available 'général' or 'annonces' channel.

    Args:
        guild (discord.Guild): The Discord guild to post the message in.
        server_name (str): The display name of the server used in the embed title.
        server_type (str): The type of server, shown in the embed description.
    """
    # Look for a suitable channel to post the welcome message
    target_channel = None
    for ch in guild.text_channels:
        if ch.name in ["annonces", "général", "general"]:
            target_channel = ch
            break

    # Abort silently if no suitable channel was found
    if target_channel is None:
        return

    embed = discord.Embed(
        title=f"🎉 Welcome to {server_name}!",
        description=f"This server was set up by **ForgeBot** for a **{server_type}** community.",
        color=discord.Color(0x5865F2)
    )
    embed.add_field(
        name="📋 Getting started",
        value="• Read the rules in #règles\n• Introduce yourself in #général\n• Explore the channels!",
        inline=False
    )
    embed.set_footer(text="Configured by ForgeBot • /setup to reconfigure")

    await target_channel.send(embed=embed)


async def post_rules(guild: discord.Guild):
    """
    Post a default set of server rules as an embed in the 'règles' channel.
    Does nothing if the channel does not exist.

    Args:
        guild (discord.Guild): The Discord guild to post the rules in.
    """
    # Retrieve the rules channel by name
    rules_channel = discord.utils.get(guild.text_channels, name="règles")
    if rules_channel is None:
        return

    embed = discord.Embed(
        title="📜 Server Rules",
        color=discord.Color(0xFF6B00)
    )
    rules = [
        "**1.** Be respectful to all members.",
        "**2.** No spam, flooding, or unauthorized advertising.",
        "**3.** Stay on topic in each channel.",
        "**4.** No NSFW or offensive content.",
        "**5.** Respect moderators' decisions.",
    ]
    # Join all rules into a single description block
    embed.description = "\n".join(rules)
    embed.set_footer(text="Failure to follow the rules may result in a ban.")

    await rules_channel.send(embed=embed)