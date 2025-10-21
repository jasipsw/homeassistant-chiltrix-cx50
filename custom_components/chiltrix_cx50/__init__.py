"""The Chiltrix CX50-2 Heat Pump integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .modbus_client import ChiltrixModbusClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.CLIMATE,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chiltrix CX50-2 from a config entry."""
    host = entry.data["host"]
    port = entry.data["port"]
    slave_id = entry.data.get("slave_id", 1)
    scan_interval = entry.data.get("scan_interval", 30)

    # Initialize Modbus client
    client = ChiltrixModbusClient(host, port, slave_id)
    
    # Test connection
    try:
        await hass.async_add_executor_job(client.connect)
    except Exception as err:
        _LOGGER.error("Failed to connect to Chiltrix at %s:%s - %s", host, port, err)
        raise ConfigEntryNotReady(f"Cannot connect to device: {err}") from err

    async def async_update_data():
        """Fetch data from Chiltrix."""
        try:
            return await hass.async_add_executor_job(client.read_all_registers)
        except Exception as err:
            _LOGGER.error("Error communicating with Chiltrix: %s", err)
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    # Create data update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Chiltrix CX50-2 {host}",
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

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await hass.async_add_executor_job(client.close)
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
