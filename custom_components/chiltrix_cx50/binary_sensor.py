"""Binary sensor platform for Chiltrix CX50-2."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chiltrix binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        ChiltrixBinarySensor(
            coordinator,
            entry,
            "power",
            "Power",
            "mdi:power",
            BinarySensorDeviceClass.RUNNING,
        ),
        ChiltrixBinarySensor(
            coordinator,
            entry,
            "heating_mode",
            "Heating Mode",
            "mdi:radiator",
            BinarySensorDeviceClass.HEAT,
        ),
        ChiltrixBinarySensor(
            coordinator,
            entry,
            "cooling_mode",
            "Cooling Mode",
            "mdi:snowflake",
            BinarySensorDeviceClass.COLD,
        ),
        ChiltrixBinarySensor(
            coordinator,
            entry,
            "dhw_mode_active",
            "DHW Mode Active",
            "mdi:water-boiler",
            None,
        ),
        ChiltrixBinarySensor(
            coordinator,
            entry,
            "silent_mode",
            "Silent Mode",
            "mdi:volume-off",
            None,
        ),
        ChiltrixBinarySensor(
            coordinator,
            entry,
            "defrost_active",
            "Defrost Active",
            "mdi:snowflake-melt",
            None,
        ),
        ChiltrixBinarySensor(
            coordinator,
            entry,
            "pump_enabled",
            "Pump Enabled",
            "mdi:water-pump",
            BinarySensorDeviceClass.RUNNING,
        ),
        ChiltrixErrorBinarySensor(coordinator, entry),
    ]

    async_add_entities(entities)


class ChiltrixBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base Chiltrix binary sensor."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = f"Chiltrix {name}"
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self._data_key)


class ChiltrixErrorBinarySensor(ChiltrixBinarySensor):
    """Error binary sensor for Chiltrix."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the error binary sensor."""
        super().__init__(
            coordinator,
            entry,
            "error_code",
            "Error",
            "mdi:alert-circle",
            BinarySensorDeviceClass.PROBLEM,
        )
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool | None:
        """Return true if there is an error."""
        error_code = self.coordinator.data.get("error_code", 0)
        return error_code != 0
