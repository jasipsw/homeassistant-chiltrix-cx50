"""Sensor platform for Chiltrix CX50-2."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chiltrix sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        # Temperature sensors
        ChiltrixSensor(
            coordinator,
            entry,
            "water_outlet_temp",
            "Water Outlet Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "inlet_water_temp",
            "Inlet Water Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "ambient_temp",
            "Ambient Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "suction_temp",
            "Suction Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "plate_exchange_temp",
            "Plate Exchange Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "ipm_temp",
            "IPM Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        ),
        # Electrical sensors
        ChiltrixSensor(
            coordinator,
            entry,
            "input_voltage",
            "Input Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "input_current",
            "Input Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "compressor_current",
            "Compressor Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "compressor_phase_current",
            "Compressor Phase Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "bus_line_voltage",
            "Bus Line Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        # Performance sensors
        ChiltrixSensor(
            coordinator,
            entry,
            "pump_flow",
            "Pump Flow Rate",
            "L/min",
            None,
            SensorStateClass.MEASUREMENT,
            scale=0.1,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "compressor_frequency",
            "Compressor Frequency",
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "ec_fan_1_speed",
            "EC Fan 1 Speed",
            "%",
            None,
            SensorStateClass.MEASUREMENT,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "ec_fan_2_speed",
            "EC Fan 2 Speed",
            "%",
            None,
            SensorStateClass.MEASUREMENT,
        ),
        # Runtime sensors
        ChiltrixSensor(
            coordinator,
            entry,
            "compressor_run_hours",
            "Compressor Run Hours",
            UnitOfTime.HOURS,
            SensorDeviceClass.DURATION,
            SensorStateClass.TOTAL_INCREASING,
        ),
        ChiltrixSensor(
            coordinator,
            entry,
            "e_heater_power",
            "Electric Heater Power",
            "W",
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
    ]

    async_add_entities(sensors)


class ChiltrixSensor(CoordinatorEntity, SensorEntity):
    """Chiltrix sensor entity."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        scale: float = 1.0,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._scale = scale
        self._attr_name = f"Chiltrix {name}"
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def native_value(self) -> float | int | None:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._data_key)
        if value is None:
            return None
        return value * self._scale
