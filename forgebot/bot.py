"""
ForgeBot is a Discord bot that guides administrators through the complete setup of their server in 5 interactive steps. It includes:

welcome.py → automatic welcome message + role assignment
moderation.py → toxicity detection by level + automatic sanctions
payment_server.py → PayPal webhook server for the /setup paywall
model.py → ML-based classification of user responses (type, size, etc.)
builder.py → actual creation of Discord categories, channels, and roles
session.py → in-memory user session management

Main flow:
/setup → step 1 (type) → step 2 (name) → step 3 (size + optional paywall) → step 4 (special channels) → step 5 (confirmation) → build_server()
"""

import discord
from discord import app_commands
from discord.ext import tasks
import time
import urllib.parse

from config import (
    DISCORD_TOKEN, SESSION_TIMEOUT,
    PAYPAL_EMAIL, PAYPAL_WEBHOOK_URL, PAYPAL_RETURN_URL,
    PAYPAL_PRIX, PAYPAL_DEVISE,
)
import session as sess
from model import classify, load_or_train, RESPONSES
from builder import build_server, post_welcome_message, post_rules, generate_structure
from welcome import setup_welcome
from moderation import check_message
from payment_server import start_webhook_server


#  Setup of bot
intents = discord.Intents.default()
intents.message_content = True  # Nécessaire pour lire le contenu des messages
intents.members = True          # Nécessaire pour détecter les nouveaux membres

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Automatic cleanup of expired sessions

@tasks.loop(minutes=5)
async def cleanup_sessions():
    """
    Periodic task executed every 5 minutes.
    It scans all active sessions and removes those whose last activity exceeds SESSION_TIMEOUT seconds (defined in config.py). 
    This prevents an unlimited buildup of abandoned sessions in memory.
    """
    now = time.time()
    expired = [
        k for k, v in sess.sessions.items()
        if now - v["last_activity"] > SESSION_TIMEOUT
    ]
    for k in expired:
        del sess.sessions[k]


#  Helpers PayPal

def build_paypal_link(user_id: int, guild_id: int, size_label: str) -> str:
    """
    Generates a PayPal payment link with encoded session metadata.
    Builds a URL to the PayPal payment form (cgi-bin/webscr) by encoding the required information so the webhook can identify the user
    and the server involved after the payment is completed.
    """
    metadata = f"{user_id}:{guild_id}"
    params = {
        "cmd": "_xclick",
        "business": PAYPAL_EMAIL,
        "item_name": f"ForgeBot Abonnement {size_label}",
        "amount": PAYPAL_PRIX,
        "currency_code": PAYPAL_DEVISE,
        "custom": metadata,
        "notify_url": PAYPAL_WEBHOOK_URL,
        "return": PAYPAL_RETURN_URL,
        "cancel_return": PAYPAL_RETURN_URL,
        "no_shipping": "1",
        "rm": "2",
    }
    return "https://www.paypal.com/cgi-bin/webscr?" + urllib.parse.urlencode(params)


#  Event : bot ready

@client.event
async def on_ready():
    """
    Event triggered once the bot is connected and ready.
    Performs the following steps in order:
    Synchronizes slash commands with Discord (tree.sync).
    Starts the expired session cleanup task.
    Initializes the welcome module (setup_welcome).
    Starts the PayPal webhook HTTP server (start_webhook_server).
    Prints the bot’s username in the console.
    Updates the bot’s visible Discord status.
    """
    await tree.sync()
    cleanup_sessions.start()
    setup_welcome(client)
    start_webhook_server(client)

    print(f"✅ ForgeBot connecté en tant que {client.user}")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/setup pour configurer votre serveur"
        )
    )


#  COMMAND : /setup
@tree.command(name="setup", description="🔧 Lance la configuration guidée de votre serveur Discord")
async def setup(interaction: discord.Interaction):
    """
    Slash command /setup — Starts the guided 5-step server configuration process.

It first checks whether the user has administrator permissions in the server, then verifies that no active session already exists for this user in the same server. It then creates a new session and sends the first message of the setup flow.

Setup flow steps:

Step 1 → Server type (gaming, school, community)
Step 2 → Server name
Step 3 → Size (small / medium / large) + paywall if medium or large
Step 4 → Desired special channels
Step 5 → Confirmation and server build execution

Behavior:

Sends ephemeral responses (visible only to the user) when an error occurs.
Sends a public message to start the interactive setup session in the server.
    """
    user_id  = interaction.user.id
    guild_id = interaction.guild_id

    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="🚫 Accès refusé",
            description="Tu dois être **administrateur** pour utiliser `/setup`.",
            color=discord.Color(0xFF6A00)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if sess.get_session(user_id, guild_id):
        embed = discord.Embed(
            title="⚠️ Session déjà active",
            description="Tu as déjà une session en cours ! Utilise `/cancel` pour recommencer.",
            color=discord.Color(0xFF6A00)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    sess.create_session(user_id, guild_id)
    sess.update_session(user_id, guild_id, step=1)

    embed = discord.Embed(
        title="⚙️ Bienvenue dans ForgeBot !",
        description=(
            "Je vais configurer ton serveur Discord en **5 étapes rapides**.\n\n"
            + RESPONSES["step_1_ask"]
        ),
        color=discord.Color(0xFF6A00)
    )
    embed.set_footer(text="Tape /cancel pour annuler à tout moment")
    await interaction.response.send_message(embed=embed)


#  COMMAND : /cancel
@tree.command(name="cancel", description="❌ Annule la configuration en cours")
async def cancel(interaction: discord.Interaction):
    """
Slash command /cancel — Cancels and deletes the current configuration session.
It immediately removes the active session for the user in the server, regardless of the current step. The user can restart the process at any time using /setup.

Behavior:
Responds ephemerally (only visible to the command author).
If no session exists, the command does nothing (no-op) and fails silently.
    """
    sess.delete_session(interaction.user.id, interaction.guild_id)
    embed = discord.Embed(
        title="🗑️ Configuration annulée",
        description="Lance `/setup` quand tu veux recommencer !",
        color=discord.Color(0xFF6A00)
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


#  COMMAND : /status
@tree.command(name="status", description="📋 Affiche l'état de ta session")
async def status(interaction: discord.Interaction):
    """
  Slash command /status — Displays a summary of the current /setup session.

It retrieves the user’s active session and shows:

The current step (with a human-readable label)
The selected server type
The entered server name
The selected size
A special message if the session is waiting for PayPal payment

Behavior:

The response is always ephemeral (only visible to the user).
If no session is active, it informs the user to start /setup.
    """
    session = sess.get_session(interaction.user.id, interaction.guild_id)
    if not session:
        embed = discord.Embed(
            title="❌ Aucune session active",
            description="Lance `/setup` pour démarrer une configuration !",
            color=discord.Color(0xFF6A00)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    steps_labels = {
        1: "Type de serveur",
        2: "Nom du serveur",
        3: "Taille",
        "awaiting_payment": "⏳ En attente de paiement",
        4: "Channels spéciaux",
        5: "Confirmation",
    }
    step_display = steps_labels.get(session["step"], str(session["step"]))

    embed = discord.Embed(title="📋 Ta configuration en cours", color=discord.Color(0x5865F2))
    embed.add_field(name="Étape",    value=step_display,                inline=False)
    embed.add_field(name="Type",     value=session["server_type"]  or "—", inline=True)
    embed.add_field(name="Nom",      value=session["server_name"]  or "—", inline=True)
    embed.add_field(name="Membres",  value=session["member_count"] or "—", inline=True)

    if session["step"] == "awaiting_payment":
        embed.add_field(
            name="💳 Paiement",
            value="En attente de confirmation PayPal. Si tu as déjà payé, patiente quelques secondes.",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


#  COMMAND : /modconfig
@tree.command(name="modconfig", description="🔧 Affiche la configuration de modération")
async def modconfig(interaction: discord.Interaction):
    """
   Slash command /modconfig — Displays the current configuration of the moderation module.

This command is restricted to administrators. It provides a readable summary of the moderation settings currently active on the server by directly reading constants imported from moderation.py and config.py.

Displayed information:

The log channel used for moderation actions
The name of the mute role applied to users
The mute duration in minutes
The number of banned words and an example for each of the 4 severity levels:
Level 1 → Warning
Level 2 → Temporary mute
Level 3 → Server kick
Level 4 → Permanent ban

Behavior:

The response is ephemeral (only visible to the command issuer).
The banned word lists are defined in moderation.py (BANNED_WORDS).
    """
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="🚫 Accès refusé",
            description="Cette commande est réservée aux **administrateurs**.",
            color=discord.Color(0xFF6A00)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    from moderation import BANNED_WORDS, MUTE_DURATION_MINUTES
    from config import MUTE_ROLE_NAME, LOG_CHANNEL_NAME

    embed = discord.Embed(title="🛡️ Configuration de modération", color=discord.Color(0x5865F2))
    embed.add_field(name="Canal de logs",   value=f"`#{LOG_CHANNEL_NAME}`", inline=True)
    embed.add_field(name="Rôle Mute",       value=f"`{MUTE_ROLE_NAME}`",   inline=True)
    embed.add_field(name="Durée du mute",   value=f"{MUTE_DURATION_MINUTES} min", inline=True)
    embed.add_field(
        name="⚠️ Niveau 1 — Avertissement",
        value=f"{len(BANNED_WORDS[1])} mots · ex: `{BANNED_WORDS[1][0]}`",
        inline=False
    )
    embed.add_field(
        name="🔇 Niveau 2 — Mute",
        value=f"{len(BANNED_WORDS[2])} mots · ex: `{BANNED_WORDS[2][0]}`",
        inline=False
    )
    embed.add_field(
        name="👢 Niveau 3 — Kick",
        value=f"{len(BANNED_WORDS[3])} mots · ex: `{BANNED_WORDS[3][0]}`",
        inline=False
    )
    embed.add_field(
        name="🔨 Niveau 4 — Ban",
        value=f"{len(BANNED_WORDS[4])} mots · ex: `{BANNED_WORDS[4][0]}`",
        inline=False
    )
    embed.set_footer(text="Modifie les listes dans moderation.py")
    await interaction.response.send_message(embed=embed, ephemeral=True)


#  COMMANDE : /help
HELP_CATEGORIES = {
    """
    Static dictionary defining ForgeBot help categories.

Structure:

Key (str) → displayed category name (including emoji)
Value → dictionary containing:
"color": embed color in hexadecimal format
"commands": list of command objects { name, desc, perm }

It is used by HelpView to build paginated embeds for the /help command.
    """
    "🔧 Configuration": {
        "color": 0xFF6A00,
        "commands": [
            {"name": "/setup",  "desc": "Lance la configuration guidée en 5 étapes.", "perm": "Administrateur"},
            {"name": "/cancel", "desc": "Annule la session de configuration en cours.", "perm": "Administrateur"},
            {"name": "/status", "desc": "Affiche l'état de ta session /setup.", "perm": "Tout le monde"},
        ],
    },
    "🛡️ Modération": {
        "color": 0xFF6A00,
        "commands": [
            {"name": "Détection auto", "desc": "Analyse chaque message et applique une sanction selon la gravité (avertissement → mute → kick → ban).", "perm": "—"},
            {"name": "/modconfig",     "desc": "Affiche la config de modération : mots interdits, durée du mute, canal de logs.", "perm": "Administrateur"},
        ],
    },
    "👋 Bienvenue": {
        "color": 0xFF6A00,
        "commands": [
            {"name": "Message auto", "desc": "Envoie un embed de bienvenue et attribue le rôle Membre à chaque nouveau membre.", "perm": "—"},
        ],
    },
    "💳 Abonnement": {
        "color": 0xFF6A00,
        "commands": [
            {"name": "Paywall /setup", "desc": "Les serveurs moyen ou grand nécessitent un abonnement PayPal de 3,50€/mois, débloqué automatiquement après paiement.", "perm": "Administrateur"},
        ],
    },
}


class HelpView(discord.ui.View):
    """
   Interactive paginated view for the /help command.

Displays the categories defined in HELP_CATEGORIES one at a time, with navigation buttons to switch between pages. Only the user who invoked the command can interact with the buttons.

Attributes:

author_id (int): Discord ID of the user who initiated /help
categories (list): List of HELP_CATEGORIES keys (category names)
current_idx (int): Index of the currently displayed category (0-based)
    """

    def __init__(self, author_id: int):
        """
Initializes the HelpView with the author’s ID and sets up the pagination state.
        """
        super().__init__(timeout=120)
        self.author_id   = author_id
        self.categories  = list(HELP_CATEGORIES.keys())
        self.current_idx = 0
        self._refresh_buttons()

    def _refresh_buttons(self):
        """
Updates the state (enabled/disabled) and labels of the navigation buttons based on the current index and total categories.
        """
        self.btn_prev.disabled = self.current_idx == 0
        self.btn_next.disabled = self.current_idx == len(self.categories) - 1
        self.btn_page.label    = f"{self.current_idx + 1} / {len(self.categories)}"

    def build_embed(self) -> discord.Embed:
        
        """
Builds and returns the embed for the currently displayed category, including the list of commands and their descriptions.
        """
        
        cat_name = self.categories[self.current_idx]
        cat_data = HELP_CATEGORIES[cat_name]
        embed = discord.Embed(title=f"📖 Aide ForgeBot — {cat_name}", color=discord.Color(cat_data["color"]))
        for cmd in cat_data["commands"]:
            embed.add_field(
                name=cmd["name"],
                value=f"{cmd['desc']}\n▸ **Permission :** {cmd['perm']}",
                inline=False
            )
        embed.set_footer(text=f"Page {self.current_idx + 1}/{len(self.categories)} • expire dans 2 min")
        return embed

    async def _check_author(self, interaction: discord.Interaction) -> bool:
        
        """
Checks if the interaction user is the same as the author of the command. If not, sends an ephemeral error message and returns False. Otherwise, returns True.
        """
        
        if interaction.user.id != self.author_id:
            embed = discord.Embed(
                title="❌ Action non autorisée",
                description="Tape `/help` pour ouvrir ton propre menu !",
                color=discord.Color(0xFF6A00)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        """
        Button ◀ — Navigates to the previous category.
        """
        
        if not await self._check_author(interaction): return
        self.current_idx -= 1
        self._refresh_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="1 / 4", style=discord.ButtonStyle.primary, disabled=True)
    async def btn_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        """
        Central button displaying the current page .

        Always disabled — serves only as a visual indicator of pagination.
        """
        
        pass

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        """
        Button ▶ — Navigates to the next category.
        """
        
        if not await self._check_author(interaction): return
        self.current_idx += 1
        self._refresh_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


@tree.command(name="help", description="📖 Affiche la liste des commandes ForgeBot")
async def help_cmd(interaction: discord.Interaction):
    
    """
Slash command /help — Displays the help menu with all available commands and features.
    """
    
    view = HelpView(author_id=interaction.user.id)
    await interaction.response.send_message(embed=view.build_embed(), view=view, ephemeral=True)


#  Button-based view for server creation confirmation (manual mode).

class ManualConfirmView(discord.ui.View):
    """
   Manual server build confirmation view.

Displayed after the user selects the ⚙️ Manual mode in ConfirmView. It allows the user to validate the proposed server architecture, add an additional channel, or cancel the configuration process.

This view provides interactive control over the final structure before it is applied to the Discord server.

Attributes:

user_id (int): ID of the user who owns the session
guild_id (int): ID of the target Discord server
message (discord.Message): Context message used to access the guild and channels
archi (dict): Server architecture generated by generate_structure() awaiting confirmation
    """

    def __init__(self, user_id, guild_id, message, archi):
        """
       Initializes the view with the session data and the server architecture to be validated.

Args:

user_id (int): Discord ID of the user
guild_id (int): Discord ID of the server (guild)
message (discord.Message): Context message used to access the guild
archi (dict): Generated server architecture containing categories, channels, and roles to be confirmed
        """
        super().__init__(timeout=180)
        self.user_id  = user_id
        self.guild_id = guild_id
        self.message  = message
        self.archi    = archi

    async def _check_author(self, interaction):
        
        """
        Checks if the interaction user is the owner of the session.

        Returns:
            bool: True if authorized, False otherwise (with ephemeral error message).
        """
        
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title="❌ Action non autorisée",
                description="Ce bouton ne t'appartient pas.",
                color=discord.Color(0xFF6A00)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    async def _disable_all(self, interaction):
        
        """
     Disables all buttons in the view and updates the Discord message.

This method is called before any irreversible action (such as validation or cancellation) to prevent double-clicks or further interactions after the action has been executed.
        """
        
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label=" Valider", style=discord.ButtonStyle.success)
    async def btn_validate(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        """
        Button Validate — Starts the server creation process using the manual architecture.

Sequence:

Disables all buttons in the view.
Sends a loading embed message.
Calls build_server() using the architecture stored in self.archi.
Sends the welcome message and server rules.
Displays a summary of created categories, channels, and roles.
Deletes the active session.
        """
        
        if not await self._check_author(interaction): return
        await self._disable_all(interaction)

        session = sess.get_session(self.user_id, self.guild_id)

        loading_embed = discord.Embed(
            title="⏳ Construction en cours...",
            description="ForgeBot applique l'architecture à ton serveur. (~30 secondes)",
            color=discord.Color(0xFF6A00)
        )
        await interaction.response.send_message(embed=loading_embed)

        result = await build_server(self.message.guild, self.archi)
        await post_welcome_message(self.message.guild, session["server_name"], session["server_type"])
        await post_rules(self.message.guild)

        embed = discord.Embed(title="🎉 Serveur configuré (mode manuel) !", color=discord.Color(0xFF6A00))
        embed.add_field(name="📁 Catégories", value=str(result["categories"]), inline=True)
        embed.add_field(name="💬 Channels",   value=str(result["channels"]),   inline=True)
        embed.add_field(name="🎭 Rôles",      value=str(result["roles"]),      inline=True)
        if result["errors"]:
            embed.add_field(name="⚠️ Erreurs", value="\n".join(result["errors"][:3]), inline=False)
        embed.set_footer(text="Merci d'avoir utilisé ForgeBot ! 🤖")

        await interaction.followup.send(embed=embed)
        sess.delete_session(self.user_id, self.guild_id)

    @discord.ui.button(label="➕ Ajouter un channel", style=discord.ButtonStyle.primary)
    async def btn_add(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        """
       Button ➕ Add a channel — Switches the session to manual channel input mode.

It sets the session step to "manual_add_channel" and prompts the user to provide channel details in the following format:

channel-name | CATEGORY NAME | text or voice

The processing of this input is handled in the on_message() event.
        """
        
        if not await self._check_author(interaction): return

        sess.update_session(self.user_id, self.guild_id, step="manual_add_channel")
        embed = discord.Embed(
            title="💬 Ajouter un channel",
            description=(
                "Réponds sous ce format :\n"
                "`nom-du-channel | NOM CATÉGORIE | text ou voice`\n\n"
                "**Exemple :** `hors-sujet | GÉNÉRAL | text`"
            ),
            color=discord.Color(0x5865F2)
        )
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def btn_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Bouton ❌ Annuler — Annule la configuration et supprime la session.

        Désactive les boutons, supprime la session et informe l'utilisateur
        qu'il peut relancer /setup à tout moment.
        """
        if not await self._check_author(interaction): return
        await self._disable_all(interaction)
        sess.delete_session(self.user_id, self.guild_id)
        embed = discord.Embed(
            title="🗑️ Configuration annulée",
            description="Lance `/setup` quand tu veux recommencer !",
            color=discord.Color(0xED4245)
        )
        await interaction.response.send_message(embed=embed)


class ConfirmView(discord.ui.View):
    
    """
 Final confirmation view displayed at step 4 of the /setup flow.

It allows the user to choose between two server creation modes:

⚒️ Automatic: directly triggers build_server() using the generated structure.
⚙️ Manual: displays the full architecture for review via ManualConfirmView.

A ❌ Cancel button is also available to abort the setup process.

Attributes:

user_id (int): ID of the user who owns the session
guild_id (int): ID of the target Discord server
message (discord.Message): Context message used for guild access and interaction handling
    """

    def __init__(self, user_id: int, guild_id: int, message: discord.Message):
        """
        Initialise la vue de confirmation avec le contexte de session.

        Args:
            user_id (int):            ID de l'utilisateur.
            guild_id (int):           ID du serveur.
            message (discord.Message): Message de contexte pour accéder au guild.
        """
        super().__init__(timeout=120)
        self.user_id  = user_id
        self.guild_id = guild_id
        self.message  = message

    async def _check_author(self, interaction: discord.Interaction) -> bool:
        
        """
Checks whether the interacting user is the owner of the session.

Returns:

bool: True if the user is authorized, False otherwise (with an ephemeral error message).
        """
        
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title="❌ Action non autorisée",
                description="Ce bouton ne t'appartient pas.",
                color=discord.Color(0xED4245)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    async def _disable_all(self, interaction: discord.Interaction):
        
        """
       Disables all buttons and edits the message to reflect the updated state.

This method is called before any irreversible action to prevent multiple interactions or duplicate executions.

Args:

interaction (discord.Interaction): The interaction that triggered the action.
        """
        
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="⚒️ Automatique", style=discord.ButtonStyle.success)
    async def btn_auto(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Button ⚒️ Automatic — Immediately starts server construction.

It generates the server structure using generate_structure() based on session data, then calls build_server() to create categories, channels, and roles on Discord. After that, it posts the welcome message and server rules.

Finally, it sends a summary embed showing the number of created elements and any possible errors, and deletes the active session.
        """
        if not await self._check_author(interaction): return
        await self._disable_all(interaction)

        session = sess.get_session(self.user_id, self.guild_id)

        loading_embed = discord.Embed(
            title="⏳ Construction en cours...",
            description="ForgeBot construit ton serveur. (~30 secondes)",
            color=discord.Color(0x5865F2)
        )
        await interaction.response.send_message(embed=loading_embed)

        structure = generate_structure(
            server_type=session["server_type"],
            size=session["member_count"],
            special_channels=session["special_channels"],
        )
        result = await build_server(self.message.guild, structure)
        await post_welcome_message(self.message.guild, session["server_name"], session["server_type"])
        await post_rules(self.message.guild)

        embed = discord.Embed(title="🎉 Serveur configuré !", color=discord.Color(0x5865F2))
        embed.add_field(name="📁 Catégories", value=str(result["categories"]), inline=True)
        embed.add_field(name="💬 Channels",   value=str(result["channels"]),   inline=True)
        embed.add_field(name="🎭 Rôles",      value=str(result["roles"]),      inline=True)
        if result["errors"]:
            embed.add_field(name="⚠️ Erreurs", value="\n".join(result["errors"][:3]), inline=False)
        embed.set_footer(text="Merci d'avoir utilisé ForgeBot ! ⚒️")

        await interaction.followup.send(embed=embed)
        sess.delete_session(self.user_id, self.guild_id)

    @discord.ui.button(label="⚙️ Manuel", style=discord.ButtonStyle.primary)
    async def btn_manual(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        """
       Button ⚙️ Manual — Displays the proposed architecture for review before server creation.

It generates the structure using generate_structure(), stores it in the session (step="manual_confirm"), then displays a detailed embed showing each category with its channels, as well as the planned roles.

It then hands control over to ManualConfirmView, allowing the user to validate, add a channel, or cancel the setup process.
        """
        
        if not await self._check_author(interaction): return
        await self._disable_all(interaction)

        session = sess.get_session(self.user_id, self.guild_id)

        archi = generate_structure(
           server_type=session["server_type"],
           size=session["member_count"],
           special_channels=session["special_channels"],
        )

        sess.update_session(self.user_id, self.guild_id, step="manual_confirm", custom_archi=archi)

        embed = discord.Embed(
           title=f"⚙️ Architecture proposée pour **{session['server_name']}**",
           description=(
            "Voici l'architecture adaptée à ton serveur.\n"
            "Tu peux **valider**, **modifier** un élément, ou **annuler**."
           ),
           color=discord.Color.blurple()
        )

        for cat in archi.get("categories", []):
            channels_text = "\n".join(
                 f"{'💬' if c.get('type') == 'text' else '🔊'} `#{c['name']}`"
                 for c in cat.get("channels", [])
            )
            embed.add_field(name=f"📁 {cat['name']}", value=channels_text or "—", inline=False)

        roles = archi.get("roles", [])
        if roles:
            embed.add_field(
                name="🎭 Rôles",
                value="\n".join(f"🎭 **{r}**" for r in roles),
                inline=False
            )

        embed.set_footer(text="Tape le nom d'un channel à ajouter/supprimer après avoir cliqué Modifier.")

        await interaction.response.send_message(
            embed=embed,
            view=ManualConfirmView(self.user_id, self.guild_id, self.message, archi)
        )

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def btn_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
       Button ❌ Cancel — Cancels the configuration and deletes the session.

It disables all buttons, removes the active session, and notifies the user that the setup process has been cancelled.
        """
        if not await self._check_author(interaction): return
        await self._disable_all(interaction)

        sess.delete_session(self.user_id, self.guild_id)
        embed = discord.Embed(
            title="🗑️ Configuration annulée",
            description="Lance `/setup` quand tu veux recommencer !",
            color=discord.Color(0xED4245)
        )
        await interaction.response.send_message(embed=embed)

    async def on_timeout(self):
        
        """
        Callback automatically triggered after 120 seconds of inactivity.

It disables all buttons to visually indicate that the view has expired. The session will be cleaned up by cleanup_sessions() during its next scheduled execution.
        """
        
        for item in self.children:
            item.disabled = True


#  MESSAGES RECEPTIONS AND SESSION FLOW CONTROL
@client.event
async def on_message(message: discord.Message):
    """
Event triggered every time a message is received in a server.

It plays a central role in the /setup conversational flow. Each message is first processed by the moderation module, then routed according to the active session step of the message author.

Processing pipeline:

Ignores bot messages and direct messages (outside servers).
Sends the message to check_message() for moderation.
If toxic → immediate return (message already handled).
Retrieves the active session for the author in the current server.
If no session exists → message is ignored.
Routes processing based on the current step (step):
Step 1 → ML classification of server type
Step 2 → validation and saving of server name
Step 3 → ML classification of server size + optional paywall
Step "awaiting_payment" → payment waiting message
Step 4 → ML classification of special channels + recap
Step 5 → ML classification of final confirmation + server build

Args:

message (discord.Message): Incoming Discord message containing author, content, guild, channel, etc.

Notes:

ML classifications are handled by classify() from model.py.
Server creation is handled by build_server() from builder.py.
Sessions are managed by the session.py module.
    """
    if message.author.bot or message.guild is None:
        return

    # Modération in priority 
    was_toxic = await check_message(message)
    if was_toxic:
        return

    # Traitement of sessions /setup 
    user_id  = message.author.id
    guild_id = message.guild.id
    session  = sess.get_session(user_id, guild_id)

    if session is None:
        return

    user_input = message.content.strip()
    step       = session["step"]

    # ── Step 1 : server type (ML)
    if step == 1:
        
        """
Step 1 — Detects the server type using the ML classifier.

Possible labels: "gaming", "school", "community", "unknown".

If the result is "unknown" → sends a help message and remains on step 1.
If the result is valid → stores the value in the session and moves to step 2.
        """
        
        label, confidence = classify("server_type", user_input)

        if label == "unknown":
            embed = discord.Embed(
                title="❓ Type non reconnu",
                description=RESPONSES["step_1_unknown"],
                color=discord.Color(0xFF6A00)
            )
            embed.set_footer(text="Tape /cancel pour annuler à tout moment")
            await message.channel.send(embed=embed)
            return

        sess.update_session(user_id, guild_id, server_type=label, step=2)
        type_emojis = {"gaming": "🎮", "école": "🎓", "communauté": "💼"}
        emoji = type_emojis.get(label, "")

        embed = discord.Embed(
            title=f"{emoji} Type détecté : **{label}**",
            description=RESPONSES["step_2_ask"],
            color=discord.Color(0xFF6A00)
        )
        embed.set_footer(text="Tape /cancel pour annuler à tout moment")
        await message.channel.send(embed=embed)

    # Step 2 : server name (validation)
    elif step == 2:
        """
Step 2 — Validates and stores the server name.

Constraints: 2 to 50 characters.

If invalid → sends an error message and remains on step 2.
If valid → saves the name and proceeds to step 3
        """
        if len(user_input) < 2 or len(user_input) > 50:
            embed = discord.Embed(
                title="⚠️ Nom invalide",
                description="Le nom doit faire entre **2 et 50 caractères**.",
                color=discord.Color(0xFF6A00)
            )
            await message.channel.send(embed=embed)
            return

        sess.update_session(user_id, guild_id, server_name=user_input, step=3)
        embed = discord.Embed(
            title=f"✅ Nom enregistré : **{user_input}**",
            description=RESPONSES["step_3_ask"],
            color=discord.Color(0xFF6A00)
        )
        embed.set_footer(text="Tape /cancel pour annuler à tout moment")
        await message.channel.send(embed=embed)

    # Step 3 : size (ML) + PAYWALL
    elif step == 3:
        """
Step 3 — Detects the server size and triggers the paywall if needed.

ML labels: "small", "medium", "large", "unknown".

Paywall logic:

"small" → continues freely to step 4.
"medium" or "large" → generates a PayPal payment link and switches the session to "awaiting_payment".
The session is preserved, and the payment_server.py webhook automatically resumes the flow once the payment is confirmed.
        """
        label, confidence = classify("member_count", user_input)

        if label == "unknown":
            embed = discord.Embed(
                title="❓ Taille non reconnue",
                description="Réponds `petit`, `moyen` ou `grand`, ou décris en quelques mots !",
                color=discord.Color(0xFF6A00)
            )
            await message.channel.send(embed=embed)
            return

        size_labels = {
            "small":  "petit (< 50 membres)",
            "medium": "moyen (50-200 membres)",
            "large":  "grand (200+ membres)",
        }

        # 🔒 PAYWALL — medium ou large
        if label in ("medium", "large"):
            sess.update_session(
                user_id, guild_id,
                member_count=label,
                step="awaiting_payment"
            )

            paypal_link = build_paypal_link(user_id, guild_id, size_labels[label])

            embed = discord.Embed(
                title="🔒 Abonnement requis",
                description=(
                    f"La taille **{size_labels[label]}** est une fonctionnalité **Premium**.\n\n"
                    f"**Prix : {PAYPAL_PRIX} {PAYPAL_DEVISE} / mois**\n\n"
                    f"[👉 Payer avec PayPal]({paypal_link})\n\n"
                    "✅ Une fois le paiement confirmé, ta configuration reprendra **automatiquement** !\n"
                    "⏳ Ta session est sauvegardée pendant 30 minutes."
                ),
                color=discord.Color.orange()
            )
            embed.set_footer(text="Problème de paiement ? Contacte un administrateur.")
            await message.channel.send(embed=embed)
            return

        # ✅ Taille "small" — continue normalement
        sess.update_session(user_id, guild_id, member_count=label, step=4)
        embed = discord.Embed(
            title=f"✅ Taille : **{size_labels[label]}**",
            description=RESPONSES["step_4_ask"],
            color=discord.Color(0xFF6A00)
        )
        embed.set_footer(text="Tape /cancel pour annuler à tout moment")
        await message.channel.send(embed=embed)

    # Step awaiting_payment 
    elif step == "awaiting_payment":
        """
Step awaiting_payment — Handles any message sent while waiting for payment confirmation.

It informs the user that the session is currently pending PayPal verification and suggests using /status to track the current state.

The session will be automatically unlocked by payment_server.py once the payment is confirmed.
        """
        embed = discord.Embed(
            title="⏳ En attente de paiement",
            description=(
                "Si tu viens de payer, attends quelques secondes — "
                "la session se débloque **automatiquement**.\n\n"
                "Tape `/status` pour voir l'état de ta session."
            ),
            color=discord.Color(0xFF6A00)
        )
        await message.channel.send(embed=embed)

    # ── Étape 4 : channels spéciaux (ML) ────────────────────────────────────
    elif step == 4:
        
        """
Step 4 — Detects desired special channels using the ML classifier.

Possible ML labels: "none" (no special channels) or any other label indicating that the user wants custom channels.

If "none" → sets an empty list of special channels.
Otherwise → extracts meaningful keywords from the user input after filtering stop words.

It then displays a full session summary and shows the ConfirmView for final confirmation.
        """
        
        label, confidence = classify("special_channels", user_input)

        if label == "none":
            special = []
        else:
            stop_words = {"oui", "yes", "j'ai", "besoin", "de", "ajoute", "met", "aussi", "je", "veux"}
            special = [
                w.strip(".,!?") for w in user_input.lower().split()
                if w not in stop_words and len(w) > 2
            ]

        sess.update_session(user_id, guild_id, special_channels=special, step=5)
        session = sess.get_session(user_id, guild_id)

        size_display = {"small": "< 50 membres", "medium": "50-200 membres", "large": "200+ membres"}
        type_emojis  = {"gaming": "🎮", "école": "🎓", "communauté": "💼"}

        embed = discord.Embed(
            title="📋 Récapitulatif de ta configuration",
            color=discord.Color(0xFF6A00)
        )
        embed.add_field(
            name="Type",
            value=f"{type_emojis.get(session['server_type'], '')} {session['server_type']}",
            inline=True
        )
        embed.add_field(name="Nom",   value=session["server_name"], inline=True)
        embed.add_field(
            name="Taille",
            value=size_display.get(session["member_count"], session["member_count"]),
            inline=True
        )
        embed.add_field(
            name="Channels spéciaux",
            value=", ".join(f"`{c}`" for c in special) if special else "Aucun",
            inline=False
        )
        embed.add_field(
            name="⚒️ On y va ?",
            value="Choisis une option ci-dessous.",
            inline=False
        )
        await message.channel.send(embed=embed, view=ConfirmView(user_id, guild_id, message))

    # ── Étape 5 : confirmation (ML) ──────────────────────────────────────────
    elif step == 5:
        """
Step 5 — Final confirmation using ML (fallback text handling if buttons are not used).

Possible ML labels: "yes", "no", "unknown".

"yes" → generates the structure, builds the server, posts the welcome message and rules, shows a summary, and deletes the session.
"no" → deletes the session and sends a cancellation message.
"unknown" → asks the user to rephrase their response.

Note: In the normal flow, confirmation is handled via ConfirmView buttons. This block handles cases where the user types “yes” or “no” directly instead of using the UI.
        """
        label, confidence = classify("confirmation", user_input)

        if label == "yes":
            session = sess.get_session(user_id, guild_id)

            loading_embed = discord.Embed(
                title="⏳ Construction en cours...",
                description="ForgeBot construit ton serveur. (~30 secondes)",
                color=discord.Color(0xFF6A00)
            )
            loading = await message.channel.send(embed=loading_embed)

            structure = generate_structure(
                server_type=session["server_type"],
                size=session["member_count"],
                special_channels=session["special_channels"],
            )

            result = await build_server(message.guild, structure)
            await post_welcome_message(message.guild, session["server_name"], session["server_type"])
            await post_rules(message.guild)

            await loading.delete()

            embed = discord.Embed(title="🎉 Serveur configuré !", color=discord.Color(0x5865F2))
            embed.add_field(name="📁 Catégories", value=str(result["categories"]), inline=True)
            embed.add_field(name="💬 Channels",   value=str(result["channels"]),   inline=True)
            embed.add_field(name="🎭 Rôles",      value=str(result["roles"]),      inline=True)
            if result["errors"]:
                embed.add_field(
                    name="⚠️ Erreurs",
                    value="\n".join(result["errors"][:3]),
                    inline=False
                )
            embed.set_footer(text="Merci d'avoir utilisé ForgeBot ! 🤖")
            await message.channel.send(embed=embed)
            sess.delete_session(user_id, guild_id)

        elif label == "no":
            sess.delete_session(user_id, guild_id)
            embed = discord.Embed(
                title="🗑️ Configuration annulée",
                description=RESPONSES["step_5_confirm_no"],
                color=discord.Color(0xFF8C42)
            )
            await message.channel.send(embed=embed)

        else:
            embed = discord.Embed(
                title="❓ Réponse non comprise",
                description=RESPONSES["step_5_unknown"],
                color=discord.Color(0xFF8C42)
            )
            await message.channel.send(embed=embed)


#  Lancement
if __name__ == "__main__":
    
    """
Main entry point of the script.

It checks for the presence of the Discord token (DISCORD_TOKEN in .env), loads or trains the ML model using load_or_train(), and then starts the bot using client.run().

The ML model is loaded before the bot starts to avoid any delay during the first user interactions.
    """
    
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN manquant dans le fichier .env !")
        exit(1)

    print("⚒️ Chargement du modèle ML...")
    load_or_train()

    client.run(DISCORD_TOKEN)