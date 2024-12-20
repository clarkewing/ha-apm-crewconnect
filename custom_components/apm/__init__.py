"""The APM CrewConnect integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from apm_crewconnect import Apm

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, callback

from .calendar import ApmCalendar
from .const import CONF_APM_TOKEN, CONF_OKTA_TOKEN, DOMAIN
from .services import async_register_services

PLATFORMS: list[Platform] = [Platform.CALENDAR]
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)


async def async_setup(hass, config):
    """Track states and offer events for sensors."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up APM CrewConnect from a config entry."""
    host = entry.data[CONF_HOST]

    # Initialize ApmData
    data = ApmData(hass, entry, host)
    await data.setup()

    # Store ApmData for future use
    hass.data[DOMAIN] = data

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register other services
    await async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data.pop(DOMAIN)
    return unload_ok


class ApmData:
    """Handle getting the latest data from APM so platforms can use it.

    Also handle refreshing tokens and updating config entry with refreshed tokens.
    """

    apm: Apm | None = None

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        host: str,
    ) -> None:
        """Initialize the APM data object."""
        self._hass = hass
        self.entry = entry
        self.host = host

    async def setup(self) -> None:
        """Ensure the ApmData object is set up."""
        self.apm = await self._hass.async_add_executor_job(
            lambda: Apm(
                host=self.host,
                token_manager=TokenManager(self._hass, self.entry),
            )
        )

    # @Throttle(MIN_TIME_BETWEEN_UPDATES)
    # async def update(self):
    #     """Get the latest data from APM."""
    #     assert isinstance(self.apm, Apm)
    #     await self._hass.async_add_executor_job(self.apm.update)


class TokenManager:
    """Token Manager implementation for APM CrewConnect."""

    _tokens: dict[str, dict[str, Any]] = {}

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the Token Manager."""
        self.hass = hass
        self.config_entry = config_entry
        self._retrieve()

    def set(self, **kwargs) -> None:
        """Set a token."""
        if "key" in kwargs:
            self._tokens[kwargs["key"]] = kwargs["value"]
        else:
            self._tokens = kwargs["value"]

        self._store()

    def get(
        self, key: str | None = None
    ) -> dict[str, Any] | dict[str, dict[str, Any]] | None:
        """Get a token."""
        if key is None:
            return self._tokens

        return self._tokens.get(key)

    def has(self, key: str) -> bool:
        """Determine if a specific token is held."""
        return self.get(key) is not None

    def _store(self) -> None:
        data = dict(self.config_entry.data)
        data[CONF_APM_TOKEN] = self._tokens["apm"]
        data[CONF_OKTA_TOKEN] = self._tokens["okta"]

        self.hass.add_job(self._update_config_entry, data)

    def _retrieve(self) -> None:
        self._tokens = {}

        if self.config_entry.data.get(CONF_APM_TOKEN):
            self._tokens["apm"] = self.config_entry.data[CONF_APM_TOKEN]

        if self.config_entry.data.get(CONF_OKTA_TOKEN):
            self._tokens["okta"] = self.config_entry.data[CONF_OKTA_TOKEN]

    @callback
    def _update_config_entry(self, data):
        self.hass.config_entries.async_update_entry(self.config_entry, data=data)
