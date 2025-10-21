"""The Chiltrix CX50 integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_SLAVE_ID
from .modbus_client import ChiltrixModbusClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chiltrix CX50 from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    slave_id = entry.data[CONF_SLAVE_ID]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    # Create Modbus client
    client = ChiltrixModbusClient(host=host, port=port, slave_id=slave_id)

    # Test connection
    if not await client.connect():
        raise ConfigEntryNotReady(
            f"Failed to connect to Chiltrix CX50 at {host}:{port}"
        )

    async def async_update_data():
        """Fetch data from the device."""
        try:
            # Read all registers needed for sensors
            # This is a placeholder - adjust based on your actual register map
            data = {}
            
            # Example: Read various registers
            # You'll need to adjust these based on your const.py register definitions
            for register_name, register_addr in [
                ("water_inlet_temp", 0xCA),
                ("water_outlet_temp", 0xCB),
                ("ambient_temp", 0xCC),
                ("operating_state", 0xF3),
            ]:
                result = await client.read_holding_registers(register_addr, 1)
                if result is not None:
                    data[register_name] = result[0]
                else:
                    _LOGGER.warning(f"Failed to read {register_name} at {register_addr}")

            return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    # Create update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Chiltrix CX50 {host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator and client
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Close Modbus connection
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await client.disconnect()

        # Remove entry from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
