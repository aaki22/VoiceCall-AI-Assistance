from sqlalchemy.orm import Session

from src.repository.call_repository import CallRepository


def create_call_session(db: Session, session_id: str):
    return CallRepository(db).create_call_session(session_id)


def end_call_session(db: Session, session_id: str):
    return CallRepository(db).end_call_session(session_id)


def add_call_turn(
    db: Session,
    session_id: str,
    user_text: str,
    ai_text: str,
    user_audio: str,
    ai_audio: str,
):
    return CallRepository(db).add_call_turn(session_id, user_text, ai_text, user_audio, ai_audio)
