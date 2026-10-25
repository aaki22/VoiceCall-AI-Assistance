from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.session import Base
from src.repository.call_repository import CallRepository
from src.schema.call import CallSession, CallTurn


def test_call_repository_creates_session_and_turn():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    db = SessionLocal()
    repo = CallRepository(db)

    repo.create_call_session("session-1")
    repo.add_call_turn("session-1", "hello", "hi", "user.mp3", "ai.wav")

    session = db.query(CallSession).filter_by(session_id="session-1").one()
    turn = db.query(CallTurn).filter_by(session_id="session-1").one()

    assert session.total_turns == 1
    assert turn.user_text == "hello"
