import datetime
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.reminder import VoiceReminder


class ReminderRepository:
    """Data access repository for VoiceReminder entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reminder(
        self,
        recipient_phone: str,
        reminder_text: str,
        scheduled_time_utc: datetime.datetime,
        preferred_language: str = "ta",
        session_id: Optional[str] = None,
    ) -> VoiceReminder:
        """Schedules and persists a new voice reminder."""
        reminder = VoiceReminder(
            session_id=session_id,
            recipient_phone=recipient_phone,
            reminder_text=reminder_text,
            scheduled_time_utc=scheduled_time_utc,
            preferred_language=preferred_language,
            status="pending",
        )
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def get_by_id(self, reminder_id: str) -> Optional[VoiceReminder]:
        """Finds active reminder by primary key UUID string."""
        stmt = select(VoiceReminder).where(
            VoiceReminder.id == reminder_id,
            VoiceReminder.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_reminders(
        self,
        status: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[VoiceReminder]:
        """Lists reminders with optional status and phone filtering."""
        stmt = select(VoiceReminder).where(VoiceReminder.deleted_at.is_(None))

        if status:
            stmt = stmt.where(VoiceReminder.status == status)
        if recipient_phone:
            stmt = stmt.where(VoiceReminder.recipient_phone == recipient_phone)

        stmt = stmt.order_by(desc(VoiceReminder.scheduled_time_utc)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_due_reminders(self, current_time: datetime.datetime) -> List[VoiceReminder]:
        """Queries pending reminders whose scheduled time has arrived."""
        stmt = select(VoiceReminder).where(
            VoiceReminder.status == "pending",
            VoiceReminder.scheduled_time_utc <= current_time,
            VoiceReminder.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        reminder_id: str,
        status: str,
        outbound_call_sid: Optional[str] = None,
    ) -> Optional[VoiceReminder]:
        """Updates reminder status (completed, failed, cancelled)."""
        reminder = await self.get_by_id(reminder_id)
        if not reminder:
            return None

        reminder.status = status
        if outbound_call_sid:
            reminder.outbound_call_sid = outbound_call_sid

        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancels a pending reminder."""
        reminder = await self.get_by_id(reminder_id)
        if not reminder:
            return False

        reminder.status = "cancelled"
        await self.session.commit()
        return True
