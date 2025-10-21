"""Select platform for Chiltrix CX50-2."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_MODES,
    MODE_AUTO,
    MODE_COOL,
    MODE_DHW,
    MODE_HEAT,
    MODE_OFF,
    OPERATION_MODES,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chiltrix select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = [
        ChiltrixOperationModeSelect(coordinator, client, entry),
        ChiltrixFanModeSelect(coordinator, client, entry),
    ]

    async_add_entities(entities)


class ChiltrixOperationModeSelect(CoordinatorEntity, SelectEntity):
    """Operation mode select for Chiltrix."""

    _attr_options = list(OPERATION_MODES.values())

    def __init__(self, coordinator, client, entry: ConfigEntry) -> None:
        """Initialize the operation mode select."""
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Chiltrix Operation Mode"
        self._attr_unique_id = f"{entry.entry_id}_operation_mode_select"
        self._attr_icon = "mdi:format-list-bulleted"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current operation mode."""
        mode = self.coordinator.data.get("operation_mode")
        if mode is not None:
            return OPERATION_MODES.get(mode, "Off")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the operation mode."""
        # Reverse lookup to get mode code from name
        mode_code = None
        for code, name in OPERATION_MODES.items():
            if name == option:
                mode_code = code
                break

        if mode_code is not None:
            success = await self.hass.async_add_executor_job(
                self._client.set_operation_mode, mode_code
            )
            
            if success:
                await self.coordinator.async_request_refresh()


class ChiltrixFanModeSelect(CoordinatorEntity, SelectEntity):
    """Fan mode select for Chiltrix."""

    _attr_options = list(FAN_MODES.values())

    def __init__(self, coordinator, client, entry: ConfigEntry) -> None:
        """Initialize the fan mode select."""
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Chiltrix Fan Mode"
        self._attr_unique_id = f"{entry.entry_id}_fan_mode_select"
        self._attr_icon = "mdi:fan"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current fan mode."""
        mode = self.coordinator.data.get("fan_mode")
        if mode is not None:
            return FAN_MODES.get(mode, "Auto")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the fan mode."""
        # Reverse lookup to get mode code from name
        mode_code = None
        for code, name in FAN_MODES.items():
            if name == option:
                mode_code = code
                break

        if mode_code is not None:
            success = await self.hass.async_add_executor_job(
                self._client.set_fan_mode, mode_code
            )
            
            if success:
                await self.coordinator.async_request_refresh()
