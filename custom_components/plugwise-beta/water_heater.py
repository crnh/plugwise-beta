"""Plugwise Water Heater component for Home Assistant."""

import logging
from typing import Dict, Optional

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback
#from homeassistant.helpers.entity import Entity

from homeassistant.const import TEMP_CELSIUS
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
)

from homeassistant.components.water_heater import (
    SUPPORT_OPERATION_MODE,
    WaterHeaterDevice,
)

from .const import (
    CURRENT_HVAC_DHW, 
    DOMAIN, 
    FLAME_ICON,
    IDLE_ICON,
    WATER_HEATER_ICON,
)

SUPPORT_FLAGS_HEATER = SUPPORT_OPERATION_MODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    updater = hass.data[DOMAIN][config_entry.entry_id]["updater"]

    devices = []
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():
        if device["class"] == "heater_central":
            data = api.get_device_data(dev_id)
            if "boiler_temperature" in data:
                _LOGGER.debug("Plugwise water_heater Dev %s", device["name"])
                water_heater = PwWaterHeater(api, updater, device["name"], dev_id)
                devices.append(water_heater)
                _LOGGER.info("Added water_heater.%s", "{}".format(device["name"]))

    async_add_entities(devices, True)


class PwWaterHeater(WaterHeaterDevice):
    """Representation of a Plugwise water_heater."""

    def __init__(self, api, updater, name, dev_id):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._boiler_state = False
        self._boiler_temp = None
        self._central_heating_state =  False
        self._domestic_hot_water_state = False
        self._unique_id = f"{dev_id}-water_heater"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._updater.async_add_listener(self._update_callback)

    async def async_will_remove_from_hass(self):
        """Disconnect callbacks."""
        self._updater.async_remove_listener(self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.update()
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "via_device": (DOMAIN, self._api._gateway_id),
        }

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return 1

    @property
    def current_operation(self):
        """Return the state of the water_heater."""
        if self._central_heating_state or self._boiler_state:
            return CURRENT_HVAC_HEAT
        elif self._domestic_hot_water_state:
            return CURRENT_HVAC_DHW
        else:
            return CURRENT_HVAC_IDLE
        #if self._domestic_hot_water_state:

    @property
    def current_temperature(self) -> float:
        """Return the current water temperature."""
        return self._boiler_temp

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self._central_heating_state or self._boiler_state:
            return FLAME_ICON
        elif self._domestic_hot_water_state:
            return WATER_HEATER_ICON
        else:
            return IDLE_ICON

    @property
    def min_temp(self) -> float:
        """Return max valid temperature that can be set."""
        return 80.0

    @property
    def max_temp(self) -> float:
        """Return max valid temperature that can be set."""
        return 30.0

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    def update(self):
        """Update the entity."""
        _LOGGER.debug("Update water_heater called")
        data = self._api.get_device_data(self._dev_id)
        _LOGGER.debug("Water_heater: %s", data)

        if data is None:
            _LOGGER.error("Received no data for device %s.", self._name)
        else:
            #ToDo: add central_heater_water_pressure
            if "boiler_temperature" in data:
                self._boiler_temp = data["boiler_temperature"]
            if "boiler_state" in data:
                if data["boiler_state"] is not None:
                    self._boiler_state = (data["boiler_state"] == "on")
            if "central_heating_state" in data:
                if data["central_heating_state"] is not None:
                    self._central_heating_state = (
                        data["central_heating_state"] == "on"
                    )
            if "domestic_hot_water_state" in data:
                self._domestic_hot_water_state = (
                    data["domestic_hot_water_state"] == "on"
                )
