"""
config.py
─────────
Configuration centrale de ForgeBot.
Modifie ce fichier pour personnaliser le comportement du bot.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
#  Token Discord (depuis .env)
# ─────────────────────────────────────────────
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# ─────────────────────────────────────────────
#  Sessions
# ─────────────────────────────────────────────
SESSION_TIMEOUT = 30 * 60  # 30 minutes en secondes

# ─────────────────────────────────────────────
#  PayPal
# ─────────────────────────────────────────────
PAYPAL_EMAIL      = os.getenv("PAYPAL_EMAIL", "danielfezeu40@gmail.com")
PAYPAL_WEBHOOK_URL = os.getenv("PAYPAL_WEBHOOK_URL", "https://TON_SERVEUR.com/paypal/webhook")
PAYPAL_RETURN_URL  = "https://discord.com"
PAYPAL_PRIX        = "3.50"
PAYPAL_DEVISE      = "EUR"

# ─────────────────────────────────────────────
#  Bienvenue
# ─────────────────────────────────────────────
# Nom du rôle attribué automatiquement à chaque nouveau membre
# ➜ Crée ce rôle manuellement dans Discord avant de lancer le bot
WELCOME_ROLE_NAME = "Membre"

# ─────────────────────────────────────────────
#  Modération
# ─────────────────────────────────────────────
# Nom du canal où les actions de modération sont loguées
# ➜ Crée ce canal manuellement (ex: #logs-modération)
LOG_CHANNEL_NAME = "logs-modération"

# Nom du rôle Mute (créé automatiquement par le bot si inexistant)
MUTE_ROLE_NAME = "Muted"

# Durée du mute automatique en minutes (niveau 2)
MUTE_DURATION_MINUTES = 10