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
        self._roster = None
        self.data = hass.data[DOMAIN]

    @property
    def unique_id(self) -> str | None:
        """Return the unique ID of the calendar."""
        return "apm_roster_" + self.data.apm.user_id

    @property
    def name(self) -> str | None:
        """Return the name of the calendar."""
        return "APM Roster" + " [" + self.data.apm.user_id + "]"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        upcoming_activities = [
            activity
            for activity in (self._roster.activities if self._roster else [])
            if activity.start > now()
        ]

        return (
            self._parse_activity_to_event(upcoming_activities[0])
            if upcoming_activities
            else None
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        # Check if the events within the requested date range are already loaded
        if not self._range_loaded(start_date, end_date):
            # Fetch new events for the requested date range
            await hass.async_add_executor_job(
                self.fetch_roster, start_date.date(), end_date.date()
            )

        # Return events within the requested date range
        return [
            self._parse_activity_to_event(activity)
            for activity in self._activities_in_range(start_date, end_date)
        ]

    async def async_update(self) -> None:
        """Fetch the latest general calendar state."""
        # Set default date range
        start_date = now().date()
        end_date = start_date + timedelta(days=30)

        # Fetch roster
        await self._hass.async_add_executor_job(self.fetch_roster, start_date, end_date)

    def fetch_roster(self, start_date: date, end_date: date) -> None:
        """Fetch events from APM service (blocking)."""
        self._load_roster(self.data.apm.get_roster(start_date, end_date))

    def _parse_roster_to_events(self, roster: Roster) -> list[CalendarEvent]:
        """Convert roster into CalendarEvent objects."""
        return sorted(
            [self._parse_activity_to_event(activity) for activity in roster.activities],
            key=lambda event: event.start,
        )

    def _parse_activity_to_event(self, activity) -> CalendarEvent:
        return CalendarEvent(
            start=activity.start,
            end=activity.end,
            summary=activity.title,
            description=activity.details,
        )

    def _range_loaded(self, start_date: datetime, end_date: datetime) -> bool:
        """Check if we have the roster loaded for the specified date range."""
        if not self._roster:
            return False

        # Check if the specified range is within the loaded roster's bounds
        # and if there are any loaded activities within the specified range
        # This can result in more API calls than necessary but ensures nothing gets missed
        return (
            self._roster.start <= start_date.date()
            and end_date.date() <= self._roster.end
            and len(self._activities_in_range(start_date, end_date)) > 0
        )

    def _activities_in_range(self, start_date: datetime, end_date: datetime):
        return [
            activity
            for activity in self._roster.activities
            if activity.start >= start_date and activity.end <= end_date
        ]

    def _load_roster(self, new_roster: Roster) -> None:
        """Load a new roster into the existing one, overwriting the overlapping date range with activities from new_roster."""
        if not self._roster:
            self._roster = new_roster
            return

        activities = [
            activity
            for activity in self._roster.activities
            if (
                activity.end.date() < new_roster.start
                and activity.start.date() > new_roster.end
            )
        ]

        activities.extend(new_roster.activities)

        activities = sorted(
            activities,
            key=lambda activity: activity.start,
        )

        self._roster.activities = activities
        if new_roster.start < self._roster.start:
            self._roster.start = new_roster.start
        if self._roster.end < new_roster.end:
            self._roster.end = new_roster.end
