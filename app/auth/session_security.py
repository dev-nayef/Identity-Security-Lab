from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import secrets


TOKEN_LIFETIME_MINUTES = 30

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")
SESSION_FILE = os.path.join(DATA_DIR, "sessions.json")


@dataclass
class TokenRecord:
    session_id: str
    token_hash: str
    user_agent_hash: str
    ip_address: str | None
    expires_at: str


def _hash(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _load_store() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(SESSION_FILE):
        return {}

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_store(store: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    temp_file = SESSION_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(
            store,
            file,
            indent=2,
        )

    os.replace(temp_file, SESSION_FILE)


def create_session(
    user_agent: str,
    ip_address: str | None = None,
) -> tuple[str, str]:

    store = _load_store()

    session_id = secrets.token_urlsafe(32)
    protection_token = secrets.token_urlsafe(32)

    record = TokenRecord(
        session_id=session_id,
        token_hash=_hash(protection_token),
        user_agent_hash=_hash(user_agent),
        ip_address=ip_address,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=TOKEN_LIFETIME_MINUTES)
        ).isoformat(),
    )

    store[session_id] = asdict(record)

    _save_store(store)

    return session_id, protection_token


def validate_token(
    session_id: str,
    protection_token: str,
    user_agent: str,
    ip_address: str | None = None,
    bind_ip: bool = False,
) -> bool:

    store = _load_store()
    record = store.get(session_id)

    if record is None:
        return False

    expires_at = datetime.fromisoformat(
        record["expires_at"]
    )

    if datetime.now(timezone.utc) >= expires_at:
        store.pop(session_id, None)
        _save_store(store)
        return False

    if not secrets.compare_digest(
        record["token_hash"],
        _hash(protection_token),
    ):
        return False

    if not secrets.compare_digest(
        record["user_agent_hash"],
        _hash(user_agent),
    ):
        return False

    if bind_ip and record["ip_address"] != ip_address:
        return False

    return True


def revoke_session(session_id: str) -> None:

    store = _load_store()

    if session_id in store:
        store.pop(session_id)
        _save_store(store)