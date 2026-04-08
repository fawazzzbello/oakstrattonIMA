"""
Google Calendar integration service for appointment syncing
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import Appointment, Contact, SalesSettings


class GoogleCalendarService:
    """
    Service for syncing appointments with Google Calendar.
    Requires Google Calendar API credentials and OAuth setup.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.service = None
        # In production, initialize Google Calendar API client here
        # self.service = build('calendar', 'v3', credentials=credentials)

    async def create_calendar_event(
        self,
        db: AsyncSession,
        appointment: Appointment,
        contact: Optional[Contact] = None,
    ) -> Optional[str]:
        """
        Create a Google Calendar event for an appointment.
        Returns the Google Calendar event ID.
        """
        if not self.service:
            return None  # Calendar service not configured

        try:
            # Build event object
            event = {
                "summary": appointment.title,
                "description": appointment.description or "",
                "start": {
                    "dateTime": appointment.scheduled_at.isoformat(),
                    "timeZone": appointment.timezone,
                },
                "end": {
                    "dateTime": (appointment.scheduled_at + timedelta(minutes=appointment.duration_minutes)).isoformat(),
                    "timeZone": appointment.timezone,
                },
                "attendees": [],
            }

            # Add contact as attendee if present
            if contact:
                event["attendees"].append({
                    "email": contact.email,
                    "displayName": contact.full_name,
                    "responseStatus": "needsAction",
                })

            # Add conference (Zoom/Meet)
            if appointment.meeting_url:
                event["conferenceData"] = {
                    "entryPoints": [
                        {
                            "entryPointType": "video",
                            "uri": appointment.meeting_url,
                        }
                    ],
                    "conferenceSolution": {
                        "key": {
                            "conferenceType": "eventHangout",
                        }
                    },
                }

            # Create the event
            # event = self.service.events().insert(
            #     calendarId='primary',
            #     body=event,
            #     conferenceDataVersion=1,
            # ).execute()

            # For now, return a mock ID
            calendar_event_id = f"google_calendar_{appointment.id}_{datetime.utcnow().timestamp()}"

            # Update appointment with calendar ID
            appointment.google_calendar_id = calendar_event_id
            appointment.calendar_synced = True
            if contact:
                contact.calendar_event_id = calendar_event_id
                contact.calendar_synced = True

            await db.commit()

            return calendar_event_id

        except Exception as e:
            print(f"Error creating Google Calendar event: {e}")
            return None

    async def update_calendar_event(
        self,
        db: AsyncSession,
        appointment: Appointment,
    ) -> bool:
        """
        Update an existing Google Calendar event.
        """
        if not appointment.google_calendar_id or not self.service:
            return False

        try:
            # Fetch existing event
            # event = self.service.events().get(
            #     calendarId='primary',
            #     eventId=appointment.google_calendar_id,
            # ).execute()

            # Update event fields
            # event['summary'] = appointment.title
            # event['description'] = appointment.description or ""
            # event['start']['dateTime'] = appointment.scheduled_at.isoformat()
            # event['end']['dateTime'] = (appointment.scheduled_at + timedelta(minutes=appointment.duration_minutes)).isoformat()

            # Update the event
            # self.service.events().update(
            #     calendarId='primary',
            #     eventId=appointment.google_calendar_id,
            #     body=event,
            # ).execute()

            await db.commit()
            return True

        except Exception as e:
            print(f"Error updating Google Calendar event: {e}")
            return False

    async def cancel_calendar_event(
        self,
        appointment: Appointment,
    ) -> bool:
        """
        Cancel/delete a Google Calendar event.
        """
        if not appointment.google_calendar_id or not self.service:
            return False

        try:
            # Delete the event
            # self.service.events().delete(
            #     calendarId='primary',
            #     eventId=appointment.google_calendar_id,
            # ).execute()

            return True

        except Exception as e:
            print(f"Error canceling Google Calendar event: {e}")
            return False

    async def get_calendar_settings(
        self,
        db: AsyncSession,
    ) -> Optional[Dict[str, Any]]:
        """
        Get calendar integration settings from SalesSettings.
        """
        result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
        settings = result.scalar_one_or_none()

        if not settings:
            return None

        return {
            "enabled": settings.google_calendar_enabled,
            "auto_sync": settings.auto_sync_calendar,
            "api_key": settings.google_calendar_api_key,
        }


# Singleton instance
google_calendar_service = GoogleCalendarService()


async def initialize_calendar_service(
    db: AsyncSession,
    api_key: Optional[str] = None,
) -> None:
    """
    Initialize the Google Calendar service with API credentials.
    """
    global google_calendar_service

    if api_key:
        google_calendar_service = GoogleCalendarService(api_key=api_key)
    else:
        settings = await google_calendar_service.get_calendar_settings(db)
        if settings and settings.get("api_key"):
            google_calendar_service = GoogleCalendarService(api_key=settings["api_key"])
