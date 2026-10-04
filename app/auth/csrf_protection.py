import hashlib
import json
import os
import secrets


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")
CSRF_FILE = os.path.join(DATA_DIR, "csrf_tokens.json")


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_store() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(CSRF_FILE):
        return {}

    try:
        with open(CSRF_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_store(store: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    temp_file = CSRF_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(store, file, indent=2)

    os.replace(temp_file, CSRF_FILE)


def create_csrf_token(session_id: str) -> str:
    store = _load_store()

    # Only one CSRF token per session.
    if session_id in store:
        return store[session_id]["token"]

    token = secrets.token_urlsafe(32)

    store[session_id] = {
        "token": token,
        "token_hash": _hash(token),
    }

    _save_store(store)

    return token


def validate_csrf_token(session_id: str, token: str) -> bool:
    store = _load_store()
    record = store.get(session_id)

    if not record:
        return False

    return secrets.compare_digest(
        record["token_hash"],
        _hash(token),
    )


def revoke_csrf_token(session_id: str) -> None:
    store = _load_store()

    if session_id in store:
        store.pop(session_id)
        _save_store(store)