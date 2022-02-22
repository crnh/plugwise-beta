"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    COORDINATOR,
    DOMAIN,
    MASTER_THERMOSTATS,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile Thermostats from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    async_add_entities(
        PlugwiseSelectEntity(coordinator, device_id)
        for device_id, device in coordinator.data.devices.items()
        if device["class"] in MASTER_THERMOSTATS
    )


class PlugwiseSelectEntity(PlugwiseEntity, SelectEntity):
    """Representation of a Plugwise schedule selector."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Set up the Plugwise API."""
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}-select"
        self._attr_name = self.device.get("name")

    @property
    def options(self) -> list[str] | None:
        """Return the available schedules."""
        return self.device.get("available_schedules")

    @property
    def current_option(self) -> str | None:
        """Return the currently selected schedule."""
        return self.device.get("selected_schedule")

    @plugwise_command
    async def async_select_option(self, option: str) -> None:
        """Change the selected schedule."""
        await self.coordinator.api.set_schedule_state(loc_id=self.device["location"], name=option, state="on")
