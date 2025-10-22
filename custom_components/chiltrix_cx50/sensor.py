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

    # Add COP sensor (calculated)
    sensors.append(ChiltrixCOPSensor(coordinator, entry))

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


class ChiltrixCOPSensor(CoordinatorEntity, SensorEntity):
    """Chiltrix COP (Coefficient of Performance) sensor."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the COP sensor."""
        super().__init__(coordinator)
        self._attr_name = "Chiltrix COP"
        self._attr_unique_id = f"{entry.entry_id}_cop"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:gauge"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Chiltrix CX50-2 Heat Pump",
            "manufacturer": "Chiltrix",
            "model": "CX50-2",
        }

    @property
    def native_value(self) -> float | None:
        """Calculate and return the COP."""
        # COP = Thermal Power Output / Electrical Power Input
        # Thermal Power (W) = Flow Rate (L/min) × Specific Heat (4.186 kJ/kg·K) × Temp Difference (K) × Density (kg/L)
        # For water: Thermal Power (W) = Flow Rate (L/min) × 4.186 × ΔT × (1000/60) = Flow × 69.77 × ΔT

        flow_rate = self.coordinator.data.get("pump_flow")  # Raw value, needs 0.1 scale
        inlet_temp = self.coordinator.data.get("inlet_water_temp")
        outlet_temp = self.coordinator.data.get("water_outlet_temp")
        input_voltage = self.coordinator.data.get("input_voltage")
        input_current = self.coordinator.data.get("input_current")

        if None in (flow_rate, inlet_temp, outlet_temp, input_voltage, input_current):
            return None

        # Avoid division by zero
        if input_voltage == 0 or input_current == 0:
            return None

        # Calculate values
        flow_lpm = flow_rate * 0.1  # Scale flow rate
        temp_diff = abs(outlet_temp - inlet_temp)

        # Thermal power in watts
        # Flow (L/min) × 4186 (J/kg·K) × ΔT (K) × (1 kg/L) / 60 (s/min)
        thermal_power = flow_lpm * 4186 * temp_diff / 60

        # Electrical power in watts
        electrical_power = input_voltage * input_current

        # Avoid division by zero and unrealistic values
        if electrical_power < 10:  # Less than 10W doesn't make sense
            return None

        cop = thermal_power / electrical_power

        # Sanity check: COP should be between 0.5 and 10 for a heat pump
        if 0.5 <= cop <= 10:
            return round(cop, 2)

        return None
