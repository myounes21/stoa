import uuid

_active_sessions: dict[str, dict] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _active_sessions[session_id] = {"status": "active"}
    return session_id


def close_session(session_id: str) -> None:
    _active_sessions.pop(session_id, None)


def get_active_count() -> int:
    return len(_active_sessions)