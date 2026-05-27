import time
from config import SESSION_TIMEOUT

# cache sessions in memory with a simple dict
# Key : "user_id_guild_id"
# Value : dict with the session info
sessions = {}


def get_session(user_id: int, guild_id: int) -> dict | None:
    """Récupère la session active d'un utilisateur."""
    key = f"{user_id}_{guild_id}"
    session = sessions.get(key)
    if session is None:
        return None
    # Vérifier le timeout
    if time.time() - session["last_activity"] > SESSION_TIMEOUT:
        delete_session(user_id, guild_id)
        return None
    return session


def create_session(user_id: int, guild_id: int) -> dict:
    """Crée une nouvelle session pour un utilisateur."""
    key = f"{user_id}_{guild_id}"
    sessions[key] = {
        "step": 0,
        "server_type": None,       # server type
        "server_name": None,       # server name
        "member_count": None,      # memeber count
        "special_channels": [],    # channels with special permissions 
        "language": "fr",          # server language (default to French)
        "last_activity": time.time(),
        "history": [],             # conversation history for context in the conversation
    }
    return sessions[key]


def update_session(user_id: int, guild_id: int, **kwargs):
    """update_session(user_id: int, guild_id: int, **kwargs):"""
    key = f"{user_id}_{guild_id}"
    if key in sessions:
        sessions[key].update(kwargs)
        sessions[key]["last_activity"] = time.time()


def delete_session(user_id: int, guild_id: int):
    """delete a session when it's completed or expired."""
    key = f"{user_id}_{guild_id}"
    sessions.pop(key, None)


def add_to_history(user_id: int, guild_id: int, role: str, content: str):
    """add input/output to session history for context in the conversation."""
    key = f"{user_id}_{guild_id}"
    if key in sessions:
        sessions[key]["history"].append({"role": role, "content": content})
        sessions[key]["last_activity"] = time.time()