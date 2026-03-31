from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.constants import UserRole
from app.core.dependencies import get_current_user, require_teacher_or_admin
from app.models import CalendarEvent
from app.schemas import CalendarEventCreate, CalendarEventRead, CalendarEventUpdate

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.post(
    "/events", response_model=CalendarEventRead, status_code=status.HTTP_201_CREATED
)
async def create_event(
    event_data: CalendarEventCreate,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Create a new calendar event."""
    # Validate dates
    if event_data.end_date < event_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    new_event = CalendarEvent(
        title=event_data.title,
        description=event_data.description,
        event_type=event_data.event_type,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        all_day=event_data.all_day,
        course_id=event_data.course_id,
        department_id=event_data.department_id,
    )

    # Set creator based on user role
    if current_user["role"] == UserRole.TEACHER.value:
        new_event.created_by_teacher_id = current_user["id"]
    else:
        new_event.created_by_admin_id = current_user["id"]

    await new_event.insert()
    return new_event


@router.get("/events", response_model=list[CalendarEventRead])
async def list_events(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    event_type: Optional[str] = None,
    course_id: Optional[int] = None,
    department_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """List calendar events with optional filters."""
    query = CalendarEvent.find_all()

    # Filter by date range
    if start_date:
        query = query.find(CalendarEvent.start_date >= start_date)
    if end_date:
        query = query.find(CalendarEvent.end_date <= end_date)

    # Other filters
    if event_type:
        query = query.find(CalendarEvent.event_type == event_type)
    if course_id:
        query = query.find(CalendarEvent.course_id == course_id)
    if department_id:
        query = query.find(CalendarEvent.department_id == department_id)

    events = await query.sort(+CalendarEvent.start_date).skip(skip).limit(limit).to_list()
    return events


@router.get("/events/{event_id}", response_model=CalendarEventRead)
async def get_event(
    event_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific calendar event."""
    event = await CalendarEvent.get(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    return event


@router.put("/events/{event_id}", response_model=CalendarEventRead)
async def update_event(
    event_id: str,
    event_data: CalendarEventUpdate,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Update a calendar event."""
    event = await CalendarEvent.get(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    # Teachers can only update their own events
    if current_user["role"] == UserRole.TEACHER.value:
        if event.created_by_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this event",
            )

    update_data = event_data.model_dump(exclude_unset=True)

    # Validate dates if both are being updated
    start = update_data.get("start_date", event.start_date)
    end = update_data.get("end_date", event.end_date)
    if end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    for key, value in update_data.items():
        setattr(event, key, value)

    await event.save()
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Delete a calendar event."""
    event = await CalendarEvent.get(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    # Teachers can only delete their own events
    if current_user["role"] == UserRole.TEACHER.value:
        if event.created_by_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this event",
            )

    await event.delete()
    return None
