from typing import List, Optional
from fastapi import APIRouter, Depends, status

from src.dependencies.dependencies import get_reminder_repository, get_reminder_service
from src.models.dtos.reminder_models import (
    ReminderCreateDTO,
    ReminderResponseDTO,
    ReminderUpdateDTO,
)
from src.models.responses.response_models import ResponseBuilder, StandardResponse
from src.repository.reminder_repository import ReminderRepository
from src.service.reminder_service import ReminderService

router = APIRouter(prefix="/api/v1/reminders", tags=["Voice Reminders"])


@router.post("", response_model=StandardResponse[ReminderResponseDTO], status_code=status.HTTP_200_OK)
async def schedule_voice_reminder(
    dto: ReminderCreateDTO,
    service: ReminderService = Depends(get_reminder_service),
):
    """Schedules a new voice reminder for an automated outbound phone call."""
    reminder = await service.schedule_reminder(dto)
    return ResponseBuilder.success(data=reminder, message="Voice reminder scheduled successfully")


@router.get("", response_model=StandardResponse[List[ReminderResponseDTO]])
async def list_voice_reminders(
    status: Optional[str] = None,
    recipient_phone: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    repo: ReminderRepository = Depends(get_reminder_repository),
):
    """Lists voice reminders with optional filters."""
    reminders = await repo.list_reminders(
        status=status, recipient_phone=recipient_phone, limit=limit, offset=offset
    )
    dtos = [ReminderResponseDTO.model_validate(r) for r in reminders]
    return ResponseBuilder.success(data=dtos, message="Voice reminders retrieved")


@router.get("/{reminder_id}", response_model=StandardResponse[ReminderResponseDTO])
async def get_voice_reminder(
    reminder_id: str,
    repo: ReminderRepository = Depends(get_reminder_repository),
):
    """Retrieves metadata for a specific voice reminder."""
    reminder = await repo.get_by_id(reminder_id)
    if not reminder:
        return ResponseBuilder.success(data=None, message="Reminder not found", code=404)
    return ResponseBuilder.success(data=ReminderResponseDTO.model_validate(reminder))


@router.patch("/{reminder_id}", response_model=StandardResponse[dict])
async def cancel_voice_reminder(
    reminder_id: str,
    dto: ReminderUpdateDTO,
    repo: ReminderRepository = Depends(get_reminder_repository),
):
    """Cancels or updates a scheduled voice reminder."""
    if dto.status == "cancelled":
        success = await repo.cancel_reminder(reminder_id)
        return ResponseBuilder.success(
            data={"cancelled": success},
            message="Reminder cancelled successfully" if success else "Reminder not found",
        )
    return ResponseBuilder.success(data={"updated": True}, message="Reminder updated")


@router.post("/{reminder_id}/trigger", response_model=StandardResponse[dict])
async def trigger_outbound_reminder(
    reminder_id: str,
    service: ReminderService = Depends(get_reminder_service),
):
    """Manually triggers the outbound reminder call via Vobiz."""
    dispatched = await service.trigger_due_reminders()
    return ResponseBuilder.success(
        data={"dispatched_count": dispatched},
        message="Outbound reminder trigger evaluated",
    )
