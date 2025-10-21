"""Number platform for Chiltrix CX50-2."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TEMP_SCALE


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chiltrix number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = [
        ChiltrixTemperatureNumber(
            coordinator,
            client,
            entry,
            "setpoint_temp",
            "Setpoint Temperature",
            "mdi:thermometer-auto",
            15.0,
            60.0,
            0.5,
            "REGISTER_SETPOINT_TEMP",
        ),
        ChiltrixTemperatureNumber(
            coordinator,
            client,
            entry,
            "dhw_setpoint",
            "DHW Setpoint",
            "mdi:water-boiler",
            35.0,
            65.0,
            0.5,
            "REGISTER_DHW_SETPOINT",
        ),
        ChiltrixTemperatureNumber(
            coordinator,
            client,
            entry,
            "max_outlet_temp",
            "Max Outlet Temperature",
            "mdi:thermometer-high",
            20.0,
            65.0,
            0.5,
            "REGISTER_MAX_OUTLET_TEMP",
            EntityCategory.CONFIG,
        ),
        ChiltrixTemperatureNumber(
            coordinator,
            client,
            entry,
            "min_outlet_temp",
            "Min Outlet Temperature",
            "mdi:thermometer-low",
            10.0,
            40.0,
            0.5,
            "REGISTER_MIN_OUTLET_TEMP",
            EntityCategory.CONFIG,
        ),
        ChiltrixTemperatureNumber(
            coordinator,
            client,
            entry,
            "antifreeze_temp",
            "Antifreeze Temperature",
            "mdi:snowflake-alert",
            -10.0,
            10.0,
            0.5,
            "REGISTER_ANTIFREEZE_TEMP",
            EntityCategory.CONFIG,
        ),
        ChiltrixPercentageNumber(
            coordinator,
            client,
            entry,
            "min_pump_speed",
            "Min Pump Speed",
            "mdi:water-pump",
            20,
            100,
            5,
            "REGISTER_MIN_PUMP_SPEED",
            EntityCategory.CONFIG,
        ),
        ChiltrixPercentageNumber(
            coordinator,
            client,
            entry,
            "max_pump_speed",
            "Max Pump Speed",
            "mdi:water-pump",
            30,
            100,
            5,
            "REGISTER_MAX_PUMP_SPEED",
            EntityCategory.CONFIG,
        ),
    ]

    async_add_entities(entities)


class ChiltrixNumber(CoordinatorEntity, NumberEntity):
    """Base Chiltrix number entity."""

    def __init__(
        self,
        coordinator,
        client,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        min_value: float,
        max_value: float,
        step: float,
        register_name: str,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._client = client
        self._data_key = data_key
        self._register_name = register_name
        self._attr_name = f"Chiltrix {name}"
        self._attr_unique_id = f"{entry.entry_id}_{data_key}_number"
        self._attr_icon = icon
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_entity_category = entity_category
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._data_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        # This will be overridden in subclasses
        pass


class ChiltrixTemperatureNumber(ChiltrixNumber):
    """Temperature number entity for Chiltrix."""

    def __init__(
        self,
        coordinator,
        client,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        min_value: float,
        max_value: float,
        step: float,
        register_name: str,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the temperature number entity."""
        super().__init__(
            coordinator,
            client,
            entry,
            data_key,
            name,
            icon,
            min_value,
            max_value,
            step,
            register_name,
            entity_category,
        )
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    async def async_set_native_value(self, value: float) -> None:
        """Set new temperature value."""
        # Import the register address from const
        from .const import REGISTER_SETPOINT_TEMP, REGISTER_DHW_SETPOINT, REGISTER_MAX_OUTLET_TEMP, REGISTER_MIN_OUTLET_TEMP, REGISTER_ANTIFREEZE_TEMP
        
        register_map = {
            "REGISTER_SETPOINT_TEMP": REGISTER_SETPOINT_TEMP,
            "REGISTER_DHW_SETPOINT": REGISTER_DHW_SETPOINT,
            "REGISTER_MAX_OUTLET_TEMP": REGISTER_MAX_OUTLET_TEMP,
            "REGISTER_MIN_OUTLET_TEMP": REGISTER_MIN_OUTLET_TEMP,
            "REGISTER_ANTIFREEZE_TEMP": REGISTER_ANTIFREEZE_TEMP,
        }
        
        register_address = register_map.get(self._register_name)
        if register_address is not None:
            int_value = int(value * TEMP_SCALE)
            success = await self.hass.async_add_executor_job(
                self._client.write_holding_register, register_address, int_value
            )
            
            if success:
                await self.coordinator.async_request_refresh()


class ChiltrixPercentageNumber(ChiltrixNumber):
    """Percentage number entity for Chiltrix."""

    def __init__(
        self,
        coordinator,
        client,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        min_value: float,
        max_value: float,
        step: float,
        register_name: str,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the percentage number entity."""
        super().__init__(
            coordinator,
            client,
            entry,
            data_key,
            name,
            icon,
            min_value,
            max_value,
            step,
            register_name,
            entity_category,
        )
        self._attr_native_unit_of_measurement = PERCENTAGE

    async def async_set_native_value(self, value: float) -> None:
        """Set new percentage value."""
        # Import the register address from const
        from .const import REGISTER_MIN_PUMP_SPEED, REGISTER_MAX_PUMP_SPEED
        
        register_map = {
            "REGISTER_MIN_PUMP_SPEED": REGISTER_MIN_PUMP_SPEED,
            "REGISTER_MAX_PUMP_SPEED": REGISTER_MAX_PUMP_SPEED,
        }
        
        register_address = register_map.get(self._register_name)
        if register_address is not None:
            int_value = int(value)
            success = await self.hass.async_add_executor_job(
                self._client.write_holding_register, register_address, int_value
            )
            
            if success:
                await self.coordinator.async_request_refresh()
