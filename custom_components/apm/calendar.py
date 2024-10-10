"""Calendar entity for APM CrewConnect."""

from datetime import date, datetime, timedelta

from apm_crewconnect import Roster

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import now

from .const import DOMAIN


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add calendar for passed config_entry in Home Assistant."""
    async_add_entities([ApmCalendar(hass)])


class ApmCalendar(CalendarEntity):
    """A calendar entity."""

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the calendar entity."""
        self._hass = hass
        self._events = []
        self.data = hass.data[DOMAIN]

    @property
    def name(self) -> str:
        """Return the name of the calendar."""
        return "APM Roster" + " [" + self.data.apm.user_id + "]"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        upcoming_events = [event for event in self._events if event.start > now()]

        return upcoming_events[0] if upcoming_events else None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        # Check if the events within the requested date range are already fetched
        if not self._is_events_in_range(start_date, end_date):
            # Fetch new events for the requested date range
            self.append_events_to_state(
                await hass.async_add_executor_job(
                    self.fetch_events, start_date.date(), end_date.date()
                )
            )

        # Return events within the requested date range
        return [
            event
            for event in self._events
            if event.start >= start_date and event.end <= end_date
        ]

    async def async_update(self) -> None:
        """Fetch the latest general calendar state."""
        # Set default date range
        start_date = now().date()
        end_date = start_date + timedelta(days=30)

        # Parse roster into events
        self.append_events_to_state(
            await self._hass.async_add_executor_job(
                self.fetch_events, start_date, end_date
            )
        )

    def fetch_events(self, start_date: date, end_date: date) -> list[CalendarEvent]:
        """Fetch events from APM service (blocking)."""
        roster = self.data.apm.get_roster(start_date, end_date)

        return self._parse_roster_to_events(roster)

    def append_events_to_state(self, events: list[CalendarEvent]) -> None:
        # Convert existing events to a dict
        unique_events = {self._event_key(event): event for event in self._events}

        # Add new events, automatically filtering duplicates
        unique_events.update({self._event_key(event): event for event in events})

        self._events = sorted(
            list(unique_events.values()),
            key=lambda event: event.start,
        )

    def _parse_roster_to_events(self, roster: Roster) -> list[CalendarEvent]:
        """Convert roster into CalendarEvent objects."""
        return sorted(
            [
                CalendarEvent(
                    start=activity.start,
                    end=activity.end,
                    summary=activity.title,
                    description=activity.details,
                )
                for activity in roster.activities
            ],
            key=lambda event: event.start,
        )

    def _is_events_in_range(self, start_date, end_date) -> bool:
        """Check if we have events within the specified date range."""
        if not self._events:
            return False

        # Assuming the events are sorted, check the range
        first_event = self._events[0].start
        last_event = self._events[-1].end
        return start_date >= first_event and end_date <= last_event

    def _event_key(self, event: CalendarEvent) -> str:
        return (
            str(event.start.timestamp())
            + "-"
            + str(event.end.timestamp())
            + "-"
            + event.summary
        )
