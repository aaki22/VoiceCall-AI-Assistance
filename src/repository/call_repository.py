import logging
from datetime import datetime

from sqlalchemy.orm import Session

from src.exception.exceptions import PersistenceException
from src.schema.call import CallSession, CallTurn


logger = logging.getLogger(__name__)


class CallRepository:
    def __init__(self, db: Session):
        self._db = db

    def create_call_session(self, session_id: str) -> CallSession:
        try:
            session = CallSession(session_id=session_id)
            self._db.add(session)
            self._db.commit()
            self._db.refresh(session)
            logger.info("Call session created session_id=%s", session_id)
            return session
        except Exception as exc:
            self._db.rollback()
            logger.exception("Failed to create call session session_id=%s", session_id)
            raise PersistenceException("Failed to create call session") from exc

    def end_call_session(self, session_id: str) -> None:
        try:
            session = self._db.query(CallSession).filter_by(session_id=session_id).first()
            if session:
                session.ended_at = datetime.utcnow()
                self._db.commit()
                logger.info("Call session ended session_id=%s", session_id)
        except Exception as exc:
            self._db.rollback()
            logger.exception("Failed to end call session session_id=%s", session_id)
            raise PersistenceException("Failed to end call session") from exc

    def add_call_turn(
        self,
        session_id: str,
        user_text: str,
        ai_text: str,
        user_audio: str,
        ai_audio: str,
    ) -> None:
        try:
            turn = CallTurn(
                session_id=session_id,
                user_text=user_text,
                ai_text=ai_text,
                user_audio=user_audio,
                ai_audio=ai_audio,
            )
            self._db.add(turn)

            session = self._db.query(CallSession).filter_by(session_id=session_id).first()
            if session:
                session.total_turns += 1

            self._db.commit()
            logger.info("Call turn added session_id=%s", session_id)
        except Exception as exc:
            self._db.rollback()
            logger.exception("Failed to add call turn session_id=%s", session_id)
            raise PersistenceException("Failed to add call turn") from exc
