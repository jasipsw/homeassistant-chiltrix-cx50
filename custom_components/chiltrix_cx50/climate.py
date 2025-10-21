"""Climate platform for Chiltrix CX50-2."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_AUTO, MODE_COOL, MODE_HEAT, MODE_OFF


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chiltrix climate entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    async_add_entities([ChiltrixClimate(coordinator, client, entry)])


class ChiltrixClimate(CoordinatorEntity, ClimateEntity):
    """Chiltrix climate entity."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.AUTO,
    ]
    _attr_min_temp = 15.0
    _attr_max_temp = 60.0
    _attr_target_temperature_step = 0.5

    def __init__(self, coordinator, client, entry: ConfigEntry) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Chiltrix CX50-2"
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("water_outlet_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self.coordinator.data.get("setpoint_temp")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        power = self.coordinator.data.get("power", False)
        if not power:
            return HVACMode.OFF

        mode = self.coordinator.data.get("operation_mode", MODE_OFF)
        
        if mode == MODE_HEAT:
            return HVACMode.HEAT
        elif mode == MODE_COOL:
            return HVACMode.COOL
        elif mode == MODE_AUTO:
            return HVACMode.AUTO
        
        return HVACMode.OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        success = await self.hass.async_add_executor_job(
            self._client.set_setpoint, temperature
        )
        
        if success:
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            success = await self.hass.async_add_executor_job(
                self._client.set_power, False
            )
        else:
            # Turn on if off
            power = self.coordinator.data.get("power", False)
            if not power:
                await self.hass.async_add_executor_job(self._client.set_power, True)

            # Set mode
            mode_map = {
                HVACMode.HEAT: MODE_HEAT,
                HVACMode.COOL: MODE_COOL,
                HVACMode.AUTO: MODE_AUTO,
            }
            
            if hvac_mode in mode_map:
                success = await self.hass.async_add_executor_job(
                    self._client.set_operation_mode, mode_map[hvac_mode]
                )
            else:
                success = False

        if success:
            await self.coordinator.async_request_refresh()
