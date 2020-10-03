"""Plugwise Switch component for HomeAssistant."""

import logging

from Plugwise_Smile.Smile import Smile

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback

from .gateway import SmileGateway
from .const import API, COORDINATOR, DOMAIN, SWITCH_CLASSES, SWITCH_ICON

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile switches from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    all_devices = api.get_all_devices()
    for dev_id, device_properties in all_devices.items():
        members = None
        model = None
        if any(dummy in device_properties["types"] for dummy in SWITCH_CLASSES):
            if "plug" in device_properties["types"]:
                model = "Metered Switch"
            if "switch_group" in device_properties["types"]:
                members = device_properties["members"]
                model = "Switch Group"
            _LOGGER.debug("Plugwise switch Dev %s", device_properties["name"])
            entities.append(
                PwSwitch(
                    api,
                    coordinator,
                    device_properties["name"],
                    dev_id,
                    members,
                    model,
                )
            )
            _LOGGER.info("Added switch.%s", "{}".format(device_properties["name"]))

    async_add_entities(entities, True)


class PwSwitch(SmileGateway, SwitchEntity):
    """Representation of a Plugwise plug."""

    def __init__(self, api, coordinator, name, dev_id, members, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator, name, dev_id)

        self._members = members
        self._model = model

        self._is_on = False

        self._unique_id = f"{dev_id}-plug"

    @property
    def icon(self):
        """Return the icon of the entity."""
        return SWITCH_ICON

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.debug("Turn switch.%s on.", self._name)
        try:
            state_on = await self._api.set_relay_state(
                self._dev_id, self._members, STATE_ON
            )
            if state_on:
                self._is_on = True
                self.async_write_ha_state()
        except Smile.PlugwiseError:
            _LOGGER.error("Error while communicating to device")

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turn switch.%s off.", self._name)
        try:
            state_off = await self._api.set_relay_state(
                self._dev_id, self._members, STATE_OFF
            )
            if state_off:
                self._is_on = False
                self.async_write_ha_state()
        except Smile.PlugwiseError:
            _LOGGER.error("Error while communicating to device")

    @callback
    def _async_process_data(self):
        """Update the data from the Plugs."""
        _LOGGER.debug("Update switch called")

        data = self._api.get_device_data(self._dev_id)

        if "relay" not in data:
            self.async_write_ha_state()
            return

        self._is_on = data["relay"]
        _LOGGER.debug("Switch is ON is %s.", self._is_on)

        self.async_write_ha_state()
