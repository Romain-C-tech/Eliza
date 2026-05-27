"""
payment_server.py
Mini Flask server that receives PayPal IPN webhooks, verifies payments, and unlocks the corresponding ForgeBot session.

Startup: automatically called from bot.py via start_webhook_server().
Port: 5000 (configurable via the PORT variable).
"""

import threading
import asyncio
import logging

import requests as req
from flask import Flask, request, abort

import session as sess
from model import RESPONSES


#  Configuration

PORT = 5000

# URL de vérification IPN PayPal
# ➜ En production  : https://ipnpb.paypal.com/cgi-bin/webscr
# ➜ En sandbox     : https://ipnpb.sandbox.paypal.com/cgi-bin/webscr
PAYPAL_IPN_VERIFY_URL = "https://ipnpb.paypal.com/cgi-bin/webscr"

# Logger dédié
logging.basicConfig(level=logging.INFO, format="%(asctime)s [PayPal] %(levelname)s %(message)s")
log = logging.getLogger("payment_server")


#  App Flask
app = Flask(__name__)

# Référence au client Discord — injectée par start_webhook_server()
_discord_client = None


#  Route principale : webhook PayPal IPN
@app.route("/paypal/webhook", methods=["POST"])
def paypal_ipn():
    """
    PayPal envoie une requête POST à cette URL après chaque paiement.
    On doit répondre 200 rapidement, puis vérifier l'authenticité.
    """
    # 1. Lire les données brutes envoyées par PayPal
    raw_data = request.get_data(as_text=True)
    log.info("IPN reçue : %s", raw_data[:200])

    # 2. Vérification IPN (anti-fraude obligatoire)
    try:
        verify_response = req.post(
            PAYPAL_IPN_VERIFY_URL,
            data="cmd=_notify-validate&" + raw_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
    except req.exceptions.RequestException as e:
        log.error("Erreur lors de la vérification IPN : %s", e)
        abort(500, "Impossible de vérifier l'IPN PayPal")

    if verify_response.text != "VERIFIED":
        log.warning("IPN INVALIDE reçue — ignorée. Réponse PayPal : %s", verify_response.text)
        abort(400, "IPN non vérifiée")

    # 3. Parser le payload
    import urllib.parse
    payload = dict(urllib.parse.parse_qsl(raw_data))
    payment_status = payload.get("payment_status", "")
    log.info("Statut du paiement : %s", payment_status)

    # 4. On ne traite que les paiements complétés
    if payment_status != "Completed":
        log.info("Statut ignoré : %s", payment_status)
        return "OK", 200

    # 5. Extraire user_id et guild_id du champ custom
    custom = payload.get("custom", "")
    try:
        user_id, guild_id = [int(x) for x in custom.split(":")]
    except (ValueError, AttributeError):
        log.error("Champ 'custom' invalide ou manquant : '%s'", custom)
        abort(400, "Champ custom invalide")

    log.info("Paiement confirmé pour user_id=%s guild_id=%s", user_id, guild_id)

    # 6. Vérifier que la session existe et est bien en attente de paiement
    session = sess.get_session(user_id, guild_id)
    if not session:
        log.warning("Session introuvable pour user_id=%s guild_id=%s", user_id, guild_id)
        return "OK", 200  # Session expirée — rien à faire

    if session["step"] != "awaiting_payment":
        log.warning(
            "Session trouvée mais step='%s' (attendu 'awaiting_payment') — ignorée.",
            session["step"]
        )
        return "OK", 200

    # 7. update session step to 4 (channels spéciaux) to unblock the setup process in the bot
    sess.update_session(user_id, guild_id, step=4)
    log.info("Session débloquée pour user_id=%s guild_id=%s", user_id, guild_id)

    # 8. Notify the user on Discord (via the bot’s asyncio event loop).
    if _discord_client and _discord_client.loop:
        asyncio.run_coroutine_threadsafe(
            _notify_user_discord(user_id, guild_id),
            _discord_client.loop,
        )

    return "OK", 200


#  Route de santé (optionnel — utile pour monitoring)
@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "ForgeBot Payment Server"}, 200


#  Notification Discord après paiement confirmé
async def _notify_user_discord(user_id: int, guild_id: int):
    """
    Sends a message to the user on Discord informing them that their payment has been confirmed and that the setup process is resuming.
    """
    if _discord_client is None:
        return

    guild = _discord_client.get_guild(guild_id)
    if not guild:
        log.warning("Guild introuvable : guild_id=%s", guild_id)
        return

    member = guild.get_member(user_id)
    if not member:
        log.warning("Membre introuvable : user_id=%s", user_id)
        return

    message = (
        "✅ **Paiement PayPal confirmé !**\n\n"
        "Ton abonnement ForgeBot Premium est actif 🎉\n"
        "Retourne dans le channel où tu as lancé `/setup` et continue ta configuration !\n\n"
        + RESPONSES.get("step_4_ask", "Quels channels spéciaux veux-tu ajouter ?")
    )

    # test 1 : DM 
    try:
        await member.send(message)
        log.info("DM envoyé à user_id=%s", user_id)
        return
    except Exception as e:
        log.warning("Impossible d'envoyer un DM à user_id=%s : %s", user_id, e)

    # test 2 : general channel of the guild
    try:
        channel = guild.system_channel or next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )
        if channel:
            await channel.send(f"{member.mention} {message}")
            log.info("Message envoyé dans #%s pour user_id=%s", channel.name, user_id)
    except Exception as e:
        log.error("Impossible d'envoyer le message Discord : %s", e)


#  start server in a separate thread to avoid blocking the main bot loop
def start_webhook_server(discord_client):

    global _discord_client
    _discord_client = discord_client

    def _run():
        log.info("🌐 Serveur webhook PayPal démarré sur le port %s", PORT)
        # use_reloader=False obligatoire dans un thread non-principal
        app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

    thread = threading.Thread(target=_run, daemon=True, name="PayPalWebhookServer")
    thread.start()
    log.info("Thread webhook démarré : %s", thread.name)