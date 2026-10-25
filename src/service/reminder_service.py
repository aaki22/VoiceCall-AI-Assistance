import datetime
from typing import List, Optional
from src.client.vobiz_adapter import VobizAdapter
from src.models.dtos.reminder_models import ReminderCreateDTO, ReminderResponseDTO
from src.repository.reminder_repository import ReminderRepository
from src.utils.logger import logger


class ReminderService:
    """Business logic service for voice reminder scheduling and outbound trigger dispatch."""

    def __init__(self, reminder_repo: ReminderRepository, vobiz_adapter: VobizAdapter):
        self.reminder_repo = reminder_repo
        self.vobiz_adapter = vobiz_adapter

    async def schedule_reminder(self, dto: ReminderCreateDTO) -> ReminderResponseDTO:
        """Schedules a new voice reminder."""
        reminder = await self.reminder_repo.create_reminder(
            recipient_phone=dto.recipient_phone,
            reminder_text=dto.reminder_text,
            scheduled_time_utc=dto.scheduled_time_utc,
            preferred_language=dto.preferred_language,
            session_id=dto.session_id,
        )
        return ReminderResponseDTO.model_validate(reminder)

    async def trigger_due_reminders(self) -> int:
        """Background worker evaluating and executing due voice reminders via Vobiz."""
        now = datetime.datetime.now(datetime.timezone.utc)
        due_list = await self.reminder_repo.get_due_reminders(now)
        dispatched_count = 0

        for reminder in due_list:
            try:
                # Trigger outbound call through Vobiz.ai carrier
                result = await self.vobiz_adapter.initiate_outbound_call(
                    to_phone=reminder.recipient_phone
                )
                call_sid = result.get("call_sid", "CA_outbound_dispatched")

                await self.reminder_repo.update_status(
                    reminder_id=str(reminder.id),
                    status="completed",
                    outbound_call_sid=call_sid,
                )
                dispatched_count += 1
                logger.info(
                    f"Dispatched reminder id={reminder.id} to {reminder.recipient_phone}"
                )
            except Exception as e:
                logger.error(f"Failed to dispatch reminder {reminder.id}: {e}")
                await self.reminder_repo.update_status(
                    reminder_id=str(reminder.id),
                    status="failed",
                )

        return dispatched_count
