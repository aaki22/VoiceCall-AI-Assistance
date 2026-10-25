import datetime
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.call_session import CallSession
from src.schema.conversation_turn import ConversationTurn


class CallSessionRepository:
    """Data access repository for CallSession and ConversationTurn entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(
        self,
        session_id: str,
        call_sid: str,
        caller_phone: str,
        virtual_did: str,
        correlation_id: str,
        detected_language: str = "ta",
    ) -> CallSession:
        """Creates and persists a new telephony call session."""
        call_session = CallSession(
            session_id=session_id,
            call_sid=call_sid,
            caller_phone=caller_phone,
            virtual_did=virtual_did,
            status="active",
            detected_language=detected_language,
            playback_state="idle",
            turns_count=0,
            correlation_id=correlation_id,
        )
        self.session.add(call_session)
        await self.session.commit()
        await self.session.refresh(call_session)
        return call_session

    async def get_by_session_id(self, session_id: str) -> Optional[CallSession]:
        """Finds active (non-soft-deleted) call session by session_id."""
        stmt = select(CallSession).where(
            CallSession.session_id == session_id,
            CallSession.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_call_sid(self, call_sid: str) -> Optional[CallSession]:
        """Finds call session by Vobiz carrier CallSid."""
        stmt = select(CallSession).where(
            CallSession.call_sid == call_sid,
            CallSession.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_session_state(
        self,
        session_id: str,
        status: Optional[str] = None,
        detected_language: Optional[str] = None,
        playback_state: Optional[str] = None,
        increment_turns: bool = False,
        langsmith_run_id: Optional[str] = None,
    ) -> Optional[CallSession]:
        """Updates session state and persists changes."""
        call_session = await self.get_by_session_id(session_id)
        if not call_session:
            return None

        if status is not None:
            call_session.status = status
        if detected_language is not None:
            call_session.detected_language = detected_language
        if playback_state is not None:
            call_session.playback_state = playback_state
        if increment_turns:
            call_session.turns_count += 1
        if langsmith_run_id is not None:
            call_session.langsmith_run_id = langsmith_run_id

        await self.session.commit()
        await self.session.refresh(call_session)
        return call_session

    async def soft_delete_session(self, session_id: str) -> bool:
        """Marks a call session as soft-deleted."""
        call_session = await self.get_by_session_id(session_id)
        if not call_session:
            return False

        call_session.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        call_session.status = "completed"
        await self.session.commit()
        return True

    async def list_sessions(
        self,
        status: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[CallSession]:
        """Lists call sessions with optional status and language filters."""
        stmt = select(CallSession).where(CallSession.deleted_at.is_(None))

        if status:
            stmt = stmt.where(CallSession.status == status)
        if language:
            stmt = stmt.where(CallSession.detected_language == language)

        stmt = stmt.order_by(desc(CallSession.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_turn(
        self,
        session_id: str,
        turn_index: int,
        speaker: str,
        utterance: str,
        detected_language: str,
        tool_called: Optional[str] = None,
        grounding_metadata: Optional[dict] = None,
        latencies: Optional[dict] = None,
        barge_in_occurred: bool = False,
        langsmith_run_id: Optional[str] = None,
    ) -> ConversationTurn:
        """Persists a new conversational turn."""
        turn = ConversationTurn(
            session_id=session_id,
            turn_index=turn_index,
            speaker=speaker,
            utterance=utterance,
            detected_language=detected_language,
            tool_called=tool_called,
            grounding_metadata=grounding_metadata,
            latencies=latencies,
            barge_in_occurred=barge_in_occurred,
            langsmith_run_id=langsmith_run_id,
        )
        self.session.add(turn)
        await self.session.commit()
        await self.session.refresh(turn)
        return turn

    async def get_turns_by_session_id(self, session_id: str) -> List[ConversationTurn]:
        """Fetches all turns for a session ordered chronologically."""
        stmt = (
            select(ConversationTurn)
            .where(
                ConversationTurn.session_id == session_id,
                ConversationTurn.deleted_at.is_(None),
            )
            .order_by(ConversationTurn.turn_index.asc(), ConversationTurn.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
