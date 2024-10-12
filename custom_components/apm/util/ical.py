from datetime import datetime, timezone

from apm_crewconnect import (
    Roster,
    Activity,
    FlightActivity,
    DeadheadActivity,
    HotelActivity,
    utils as apm_utils,
)

from homeassistant.util.dt import now


class iCal:
    user_id: str
    _timestamp: datetime = now().astimezone(timezone.utc)
    _contents: str = ""

    @classmethod
    def from_roster(cls, roster: Roster) -> str:
        instance = cls()

        instance.user_id = roster.user_id

        instance._write_header(roster.user_id)

        for activity in roster.activities:
            instance._write_event(activity)

        instance._write_footer()

        return instance

    def __str__(self) -> str:
        return self.to_str

    def to_str(self) -> str:
        return self._contents

    def to_file(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(self._contents)

    def _add_line(self, key: str = None, value: str = "") -> None:
        if key:
            self._contents += key + ":" + value

        self._contents += "\n"

    def _write_header(self, user_id: str) -> None:
        self._add_line("BEGIN", "VCALENDAR")
        self._add_line("VERSION", "2.0")
        self._add_line("METHOD", "PUBLISH")
        self._add_line("PRODID", "-//Apm Technologies//CrewWebPlus//EN")
        self._add_line("X-WR-RELCALID", "CrewWebPlusCalendar-" + user_id)

    def _write_event(self, activity: Activity) -> None:
        if isinstance(activity, HotelActivity):
            return

        self._add_line()
        self._add_line("BEGIN", "VEVENT")
        self._add_line(
            "UID",
            self.user_id
            + "#ActId:"
            + str(activity.pairing_id or -1)
            + "#CmpId:"
            + str(activity.id or -1),
        )
        self._add_line(
            "DTSTAMP",
            self._timestamp.strftime("%Y%m%dT%H%M%SZ"),
        )
        self._add_line(
            "DTSTART;VALUE=DATE-TIME",
            activity.start.strftime("%Y%m%dT%H%M%SZ"),
        )
        self._add_line(
            "DTEND;VALUE=DATE-TIME",
            activity.end.strftime("%Y%m%dT%H%M%SZ"),
        )
        # self._add_line("SEQUENCE", "372537477")
        self._add_line("STATUS", "CONFIRMED")
        self._add_line("CATEGORIES", activity.category)

        if isinstance(activity, FlightActivity):
            self._add_line(
                "SUMMARY",
                activity.flight_number
                + " "
                + activity.origin_iata_code
                + "-"
                + activity.destination_iata_code
                + "("
                + apm_utils.timezone_to_offset_str(activity.destination_timezone)
                + ")",
            )
        elif isinstance(activity, DeadheadActivity):
            self._add_line(
                "SUMMARY",
                activity.description
                + " "
                + activity.origin_iata_code
                + "*"
                + activity.destination_iata_code,
            )
        else:
            self._add_line("SUMMARY", " " + activity.details)

        if isinstance(activity, FlightActivity):
            self._add_line(
                "DESCRIPTION",
                "FCT : "
                + activity.role
                + r"\n"
                + "A/C : "
                + activity.aircraft_code
                + r"\n"
                + "BLK : "
                + activity.aircraft_code
                + r"\n"
                + "Crew Member : "
                + "T:"
                + "-".join(
                    [
                        crew_member.crew_code
                        for crew_member in activity.crew_members
                        if crew_member.role_code in ["IPL", "CDB", "OPL", "SUPT"]
                    ]
                )
                + r"\n"
                + "C:"
                + "-".join(
                    [
                        crew_member.crew_code
                        for crew_member in activity.crew_members
                        if crew_member.role_code in ["INS", "CC", "CA", "SUPC"]
                    ]
                )
                + r"\n"
                + (("Remark : " + activity.remarks) if activity.remarks else ""),
            )
        else:
            self._add_line(
                "DESCRIPTION",
                r"\n".join(
                    filter(
                        lambda item: item is not None,
                        [
                            (
                                (
                                    "BLK : "
                                    + apm_utils.timedelta_to_str(activity.block_time)
                                )
                                if hasattr(activity, "block_time")
                                else None
                            ),
                            (
                                ("Remark : " + activity.remarks)
                                if activity.remarks
                                else None
                            ),
                        ],
                    )
                ),
            )

        self._add_line("END", "VEVENT")

    def _write_footer(self) -> None:
        self._add_line()
        self._add_line("END", "VCALENDAR")
        self._add_line()
