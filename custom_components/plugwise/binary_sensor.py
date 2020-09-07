"""Plugwise Binary Sensor component for Home Assistant."""

import logging

from homeassistant.components import persistent_notification
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback

from .const import (
    COORDINATOR,
    DOMAIN,
    FLAME_ICON,
    FLOW_OFF_ICON,
    FLOW_ON_ICON,
    IDLE_ICON,
    NO_NOTIFICATION_ICON,
    NOTIFICATION_ICON,
)

from .sensor import SmileSensor

BINARY_SENSOR_MAP = {
    "dhw_state": ["Domestic Hot Water State", None],
    "slave_boiler_state": ["Secondary Heater Device State", None],
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []

    all_devices = api.get_all_devices()
    for dev_id, device_properties in all_devices.items():
        if device_properties["class"] == "heater_central":
            _LOGGER.debug("Plugwise device_class %s found", device_properties["class"])
            data = api.get_device_data(dev_id)
            for binary_sensor, b_s_type in BINARY_SENSOR_MAP.items():
                _LOGGER.debug("Binary_sensor: %s", binary_sensor)
                if binary_sensor not in data:
                    continue

                _LOGGER.debug(
                    "Plugwise binary_sensor Dev %s", device_properties["name"]
                )
                entities.append(
                    PwBinarySensor(
                        api,
                        coordinator,
                        device_properties["name"],
                        dev_id,
                        binary_sensor,
                        device_properties["class"],
                    )
                )
                _LOGGER.info("Added binary_sensor.%s", f"{device_properties['name']}_{binary_sensor}")

        if device_properties["class"] == "gateway":
            _LOGGER.debug("Plugwise device_class %s found", device_properties["class"])
            entities.append(
                PwNotifySensor(
                    hass,
                    api,
                    coordinator,
                    device_properties["name"],
                    dev_id,
                    "plugwise_notification",
                    device_properties["class"],
                )
            )
            _LOGGER.info("Added binary_sensor.%s", f"{device_properties['name']}_{'plugwise_notification'}")

    async_add_entities(entities, True)


class PwBinarySensor(SmileSensor, BinarySensorEntity):
    """Representation of a Plugwise binary_sensor."""

    def __init__(self, api, coordinator, name, dev_id, binary_sensor, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator, name, dev_id, binary_sensor)

        self._binary_sensor = binary_sensor

        self._is_on = False
        self._icon = None

        self._unique_id = f"bs-{dev_id}-{self._entity_name}-{binary_sensor}"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._is_on

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update binary_sensor called")
        data = self._api.get_device_data(self._dev_id)

        if not data:
            _LOGGER.error("Received no data for device %s", self._binary_sensor)
            self.async_write_ha_state()
            return

        if self._binary_sensor not in data:
            self.async_write_ha_state()
            return

        self._is_on = data[self._binary_sensor]

        self._state = STATE_ON if self._is_on else STATE_OFF
        if self._binary_sensor == "dhw_state":
            self._icon = FLOW_ON_ICON if self._is_on else FLOW_OFF_ICON
        if self._binary_sensor == "slave_boiler_state":
            self._icon = FLAME_ICON if self._is_on else IDLE_ICON

        self.async_write_ha_state()


class PwNotifySensor(PwBinarySensor, BinarySensorEntity):
    """Representation of a Plugwise Notification binary_sensor."""

    def __init__(self, hass, api, coordinator, name, dev_id, binary_sensor, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator, name, dev_id, binary_sensor, model)
        
        self._binary_sensor = binary_sensor
        self._hass = hass

        self._is_on = False
        self._icon = None

        self._unique_id = f"bs-{dev_id}-{self._entity_name}-{binary_sensor}"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update notification-binary_sensor called")
        
        notify = self._api.notifications
        self._is_on = False if notify == {} else True
        self._state = STATE_OFF if notify == {} else STATE_ON
        self._icon = NO_NOTIFICATION_ICON if notify == {} else NOTIFICATION_ICON
        self._attributes = {} 
        if notify != {}: 
            for id, details in notify.items():
                for msg_type, msg in details.items():
                    self._attributes[msg_type.upper()] = msg
                    self._hass.components.persistent_notification.async_create(
                        f"{msg_type.upper()}: {msg}",
                        "Plugwise Notification:",
                        f"{DOMAIN}.{id}",
                    )

        self.async_write_ha_state()
