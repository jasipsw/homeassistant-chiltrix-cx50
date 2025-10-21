"""Switch platform for Chiltrix CX50-2."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chiltrix switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = [
        ChiltrixSwitch(
            coordinator,
            client,
            entry,
            "power",
            "Power",
            "mdi:power",
            "set_power",
        ),
        ChiltrixSwitch(
            coordinator,
            client,
            entry,
            "dhw_mode_active",
            "DHW Priority Mode",
            "mdi:water-boiler",
            "set_dhw_mode",
        ),
        ChiltrixSwitch(
            coordinator,
            client,
            entry,
            "silent_mode",
            "Silent Mode",
            "mdi:volume-off",
            "set_silent_mode",
        ),
    ]

    async_add_entities(entities)


class ChiltrixSwitch(CoordinatorEntity, SwitchEntity):
    """Chiltrix switch entity."""

    def __init__(
        self,
        coordinator,
        client,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        control_method: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._client = client
        self._data_key = data_key
        self._control_method = control_method
        self._attr_name = f"Chiltrix {name}"
        self._attr_unique_id = f"{entry.entry_id}_{data_key}_switch"
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        return self.coordinator.data.get(self._data_key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        method = getattr(self._client, self._control_method)
        success = await self.hass.async_add_executor_job(method, True)
        
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        method = getattr(self._client, self._control_method)
        success = await self.hass.async_add_executor_job(method, False)
        
        if success:
            await self.coordinator.async_request_refresh()
