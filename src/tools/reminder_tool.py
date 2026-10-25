import datetime
import re
from typing import Any, Dict, Optional
from src.repository.reminder_repository import ReminderRepository


class ReminderTool:
    """Tool for parsing conversational reminder requests and persisting them in PostgreSQL."""

    def __init__(self, reminder_repo: ReminderRepository):
        self.reminder_repo = reminder_repo

    async def execute(
        self,
        caller_phone: str,
        query: str,
        language: str = "ta",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parses temporal expressions from query and schedules reminder."""
        # Simple heuristic parser for common temporal offsets
        now = datetime.datetime.now(datetime.timezone.utc)
        target_time = now + datetime.timedelta(hours=2)  # Default: 2 hours from now

        # Look for explicit minutes/hours
        mins_match = re.search(r"(\d+)\s*(mins?|minutes?|நிமிடங்கள்)", query, re.IGNORECASE)
        hours_match = re.search(r"(\d+)\s*(hours?|மணி)", query, re.IGNORECASE)

        if mins_match:
            offset_mins = int(mins_match.group(1))
            target_time = now + datetime.timedelta(minutes=offset_mins)
        elif hours_match:
            offset_hours = int(hours_match.group(1))
            target_time = now + datetime.timedelta(hours=offset_hours)

        reminder_text = (
            query.replace("remind me to", "")
            .replace("remind me", "")
            .replace("நினைவூட்டல்", "")
            .strip()
        )
        if not reminder_text:
            reminder_text = "Scheduled voice reminder from Theodore"

        reminder = await self.reminder_repo.create_reminder(
            recipient_phone=caller_phone,
            reminder_text=reminder_text,
            scheduled_time_utc=target_time,
            preferred_language=language,
            session_id=session_id,
        )

        spoken_time = target_time.strftime("%I:%M %p UTC")
        if language == "ta":
            spoken_ack = f"நிச்சயமாக, உங்கள் நினைவூட்டல் {spoken_time}-க்கு பதிவு செய்யப்பட்டுள்ளது."
        else:
            spoken_ack = f"Certainly, I have scheduled your reminder for {spoken_time}."

        return {
            "tool_name": "reminder_tool",
            "reminder_id": str(reminder.id),
            "scheduled_time_utc": target_time.isoformat(),
            "spoken_output": spoken_ack,
        }
