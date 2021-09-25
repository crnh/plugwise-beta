"""Setup mocks for the Plugwise integration tests."""

import re
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import jsonpickle
import pytest
from tests.common import load_fixture
from tests.test_util.aiohttp import AiohttpClientMocker

from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    PlugwiseException,
    XMLDataMissingError,
)


class usb_node:

    mac = ""
    features = ()
    hardware_model = ""
    firmware_version = ""
    relay_state = False
    energy_consumption_today = 0
    ping = 0
    current_power_usage = 0
    current_power_usage_8_sec = 0
    power_consumption_current_hour = 0
    power_consumption_previous_hour = 0
    power_consumption_today = 0
    power_consumption_yesterday = 0
    power_production_current_hour = 0
    rssi_in = 0
    rssi_out = 0
    motion = False


def _read_json(environment, call):
    """Undecode the json data."""
    fixture = load_fixture(f"plugwise/{environment}/{call}.json")
    return jsonpickle.decode(fixture)


@pytest.fixture(name="mock_smile")
def mock_smile():
    """Create a Mock Smile for testing exceptions."""
    with patch(
        "homeassistant.components.plugwise.config_flow.Smile",
    ) as smile_mock:
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.return_value.connect.return_value = True
        yield smile_mock.return_value


@pytest.fixture(name="mock_smile_unauth")
def mock_smile_unauth(aioclient_mock: AiohttpClientMocker) -> None:
    """Mock the Plugwise Smile unauthorized for Home Assistant."""
    aioclient_mock.get(re.compile(".*"), status=401)
    aioclient_mock.put(re.compile(".*"), status=401)


@pytest.fixture(name="mock_smile_error")
def mock_smile_error(aioclient_mock: AiohttpClientMocker) -> None:
    """Mock the Plugwise Smile server failure for Home Assistant."""
    aioclient_mock.get(re.compile(".*"), status=500)
    aioclient_mock.put(re.compile(".*"), status=500)


@pytest.fixture(name="mock_smile_notconnect")
def mock_smile_notconnect():
    """Mock the Plugwise Smile general connection failure for Home Assistant."""
    with patch("homeassistant.components.plugwise.config_flow.Smile") as smile_mock:
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.PlugwiseException = PlugwiseException
        smile_mock.return_value.connect.side_effect = AsyncMock(return_value=False)
        yield smile_mock.return_value


@pytest.fixture(name="mock_smile_adam")
def mock_smile_adam():
    """Create a Mock Adam environment for testing exceptions."""
    chosen_env = "adam_multiple_devices_per_zone"
    with patch("homeassistant.components.plugwise.gateway.Smile") as smile_mock:
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.XMLDataMissingError = XMLDataMissingError

        smile_mock.return_value.gateway_id = "fe799307f1624099878210aa0b9f1475"
        smile_mock.return_value._active_device_present = False
        smile_mock.return_value.smile_version = "3.0.15"
        smile_mock.return_value.smile_type = "thermostat"
        smile_mock.return_value.smile_hostname = "smile98765"

        smile_mock.return_value.notifications = _read_json(chosen_env, "notifications")

        smile_mock.return_value.connect.side_effect = AsyncMock(return_value=True)
        smile_mock.return_value.async_update.side_effect = AsyncMock(
            return_value=_read_json(chosen_env, "all_data")
        )
        smile_mock.return_value.single_master_thermostat.side_effect = Mock(
            return_value=False
        )
        smile_mock.return_value.set_schedule_state.side_effect = AsyncMock(
            return_value=True
        )
        smile_mock.return_value.set_preset.side_effect = AsyncMock(return_value=True)
        smile_mock.return_value.set_temperature.side_effect = AsyncMock(
            return_value=True
        )
        smile_mock.return_value.set_switch_state.side_effect = AsyncMock(
            return_value=True
        )

        yield smile_mock.return_value


@pytest.fixture(name="mock_smile_anna")
def mock_smile_anna():
    """Create a Mock Anna environment for testing exceptions."""
    chosen_env = "anna_heatpump"
    with patch("homeassistant.components.plugwise.gateway.Smile") as smile_mock:
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.XMLDataMissingError = XMLDataMissingError

        smile_mock.return_value.gateway_id = "015ae9ea3f964e668e490fa39da3870b"
        smile_mock.return_value._heater_id = "1cbf783bb11e4a7c8a6843dee3a86927"
        smile_mock.return_value.smile_version = "4.0.15"
        smile_mock.return_value.smile_type = "thermostat"
        smile_mock.return_value.smile_hostname = "smile98765"

        smile_mock.return_value.notifications = _read_json(chosen_env, "notifications")

        smile_mock.return_value.connect.side_effect = AsyncMock(return_value=True)
        smile_mock.return_value.async_update.side_effect = AsyncMock(
            return_value=_read_json(chosen_env, "all_data")
        )
        smile_mock.return_value.single_master_thermostat.side_effect = Mock(
            return_value=True
        )
        smile_mock.return_value.set_schedule_state.side_effect = AsyncMock(
            return_value=True
        )
        smile_mock.return_value.set_preset.side_effect = AsyncMock(return_value=True)
        smile_mock.return_value.set_temperature.side_effect = AsyncMock(
            return_value=True
        )
        smile_mock.return_value.set_switch_state.side_effect = AsyncMock(
            return_value=True
        )

        yield smile_mock.return_value


@pytest.fixture(name="mock_smile_p1")
def mock_smile_p1():
    """Create a Mock P1 DSMR environment for testing exceptions."""
    chosen_env = "p1v3_full_option"
    with patch("homeassistant.components.plugwise.gateway.Smile") as smile_mock:
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.XMLDataMissingError = XMLDataMissingError

        smile_mock.return_value.gateway_id = "e950c7d5e1ee407a858e2a8b5016c8b3"
        smile_mock.return_value._heater_id = None
        smile_mock.return_value.smile_version = "3.3.9"
        smile_mock.return_value.smile_type = "power"
        smile_mock.return_value.smile_hostname = "smile98765"

        smile_mock.return_value.notifications = _read_json(chosen_env, "notifications")

        smile_mock.return_value.connect.side_effect = AsyncMock(return_value=True)
        smile_mock.return_value.async_update.side_effect = AsyncMock(
            return_value=_read_json(chosen_env, "all_data")
        )

        smile_mock.return_value.single_master_thermostat.side_effect = Mock(
            return_value=None
        )

        yield smile_mock.return_value


@pytest.fixture(name="mock_stretch")
def mock_stretch():
    """Create a Mock Stretch environment for testing exceptions."""
    chosen_env = "stretch_v31"
    with patch("homeassistant.components.plugwise.gateway.Smile") as smile_mock:
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.XMLDataMissingError = XMLDataMissingError

        smile_mock.return_value.gateway_id = "259882df3c05415b99c2d962534ce820"
        smile_mock.return_value._heater_id = None
        smile_mock.return_value.smile_version = "3.1.11"
        smile_mock.return_value.smile_type = "stretch"
        smile_mock.return_value.smile_hostname = "stretch98765"

        smile_mock.return_value.connect.side_effect = AsyncMock(return_value=True)
        smile_mock.return_value.async_update.side_effect = AsyncMock(
            return_value=_read_json(chosen_env, "all_data")
        )
        smile_mock.return_value.set_switch_state.side_effect = AsyncMock(
            return_value=True
        )

        yield smile_mock.return_value


@pytest.fixture(name="mock_stick")
def mock_stick():
    """Create a Stick environment for testing"""
    chosen_env = "stick"

    def stick_scan_side_effect(callback_function):
        callback_function()

    with patch("homeassistant.components.plugwise.usb.Stick") as stick_mock:
        stick_mock.return_value.connect = MagicMock(return_value=None)
        stick_mock.return_value.initialize_stick = MagicMock(return_value=None)
        stick_mock.return_value.initialize_circle_plus = MagicMock(return_value=None)
        stick_mock.return_value.scan.side_effect = stick_scan_side_effect
        stick_mock.return_value.devices = _read_json(chosen_env, "devices")
        stick_mock.return_value.joined_nodes = 4
        stick_mock.return_value.auto_update = MagicMock(return_value=None)
        stick_mock.return_value.allow_join_requests = MagicMock(return_value=None)
        stick_mock.return_value.subscribe_stick_callback = MagicMock(return_value=None)
        stick_mock.return_value.node_join = MagicMock(return_value=None)
        stick_mock.return_value.node_unjoin = MagicMock(return_value=None)
        stick_mock.return_value.disconnect = MagicMock(return_value=None)

        yield stick_mock.return_value
