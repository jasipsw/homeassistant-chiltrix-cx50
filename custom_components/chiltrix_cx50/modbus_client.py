"""Modbus client for Chiltrix CX50-2 heat pump."""
import logging
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    REGISTER_AMBIENT_TEMP,
    REGISTER_COIL_TEMP,
    REGISTER_COMPRESSOR_SPEED,
    REGISTER_COMPRESSOR_STARTS,
    REGISTER_COOLING_CAPACITY,
    REGISTER_COP,
    REGISTER_CURRENT_POWER,
    REGISTER_DEFROST_COUNT,
    REGISTER_DISCHARGE_TEMP,
    REGISTER_ERROR_CODE,
    REGISTER_FAN_SPEED,
    REGISTER_FLOW_RATE,retry
    REGISTER_HEATING_CAPACITY,
    REGISTER_OPERATING_STATE,
    REGISTER_PUMP_SPEED,
    REGISTER_RUN_HOURS,
    REGISTER_RUN_HOURS_LOW,
    REGISTER_SUCTION_TEMP,
    REGISTER_SYSTEM_PRESSURE,
    REGISTER_WATER_INLET_TEMP,
    REGISTER_WATER_OUTLET_TEMP,
    REGISTER_SETPOINT_TEMP,
    REGISTER_OPERATION_MODE,
    REGISTER_FAN_MODE,
    REGISTER_MIN_PUMP_SPEED,
    REGISTER_MAX_PUMP_SPEED,
    REGISTER_DHW_SETPOINT,
    REGISTER_DHW_MODE,
    REGISTER_ANTIFREEZE_TEMP,
    REGISTER_MAX_OUTLET_TEMP,
    REGISTER_MIN_OUTLET_TEMP,
    COIL_POWER,
    COIL_HEATING_MODE,
    COIL_COOLING_MODE,
    COIL_DHW_MODE,
    COIL_SILENT_MODE,
    COIL_DEFROST_MODE,
    COIL_PUMP_ENABLE,
    TEMP_SCALE,
    MODE_HEAT,
    MODE_COOL,
    STATE_DEFROST,
)

_LOGGER = logging.getLogger(__name__)


class ChiltrixModbusClient:
    """Modbus client for Chiltrix heat pump."""

    def __init__(self, host: str, port: int, slave_id: int):
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.client = None
        self._lock = None

    def connect(self) -> bool:
        """Connect to the Modbus device."""
        try:
            import threading
            self._lock = threading.Lock()
            
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=5,
                retries=1,
                close_comm_on_error=False,
                strict=False,
            )
            result = self.client.connect()
            if result:
                _LOGGER.info("Connected to Chiltrix at %s:%s", self.host, self.port)
            return result
        except Exception as err:
            _LOGGER.error("Connection failed: %s", err)
            return False

    def close(self):
        """Close the Modbus connection."""
        if self.client:
            self.client.close()

    def read_input_register(self, address: int) -> int | None:
        """Read a single input register."""
        if self._lock:
            with self._lock:
                return self._read_input_register_internal(address)
        return self._read_input_register_internal(address)
    
    def _read_input_register_internal(self, address: int) -> int | None:
        """Internal method to read input register."""
        try:
            import time
            time.sleep(0.05)  # Small delay between requests
            result = self.client.read_input_registers(
                address=address, count=1, slave=self.slave_id
            )
            if not result.isError():
                return result.registers[0]
        except (ModbusException, AttributeError) as err:
            _LOGGER.debug("Error reading register %s: %s", address, err)
        except Exception as err:
            _LOGGER.debug("Unexpected error reading register %s: %s", address, err)
        return None

    def read_holding_register(self, address: int) -> int | None:
        """Read a single holding register."""
        if self._lock:
            with self._lock:
                return self._read_holding_register_internal(address)
        return self._read_holding_register_internal(address)
    
    def _read_holding_register_internal(self, address: int) -> int | None:
        """Internal method to read holding register."""
        try:
            import time
            time.sleep(0.05)  # Small delay between requests
            result = self.client.read_holding_registers(
                address=address, count=1, slave=self.slave_id
            )
            if not result.isError():
                return result.registers[0]
        except (ModbusException, AttributeError) as err:
            _LOGGER.debug("Error reading holding register %s: %s", address, err)
        except Exception as err:
            _LOGGER.debug("Unexpected error reading holding register %s: %s", address, err)
        return None

    def write_holding_register(self, address: int, value: int) -> bool:
        """Write a single holding register."""
        try:
            result = self.client.write_register(
                address=address, value=value, slave=self.slave_id
            )
            return not result.isError()
        except (ModbusException, AttributeError) as err:
            _LOGGER.error("Error writing register %s: %s", address, err)
            return False

    def read_coil(self, address: int) -> bool | None:
        """Read a single coil."""
        try:
            result = self.client.read_coils(
                address=address, count=1, slave=self.slave_id
            )
            if not result.isError():
                return result.bits[0]
        except (ModbusException, AttributeError) as err:
            _LOGGER.error("Error reading coil %s: %s", address, err)
        return None

    def write_coil(self, address: int, value: bool) -> bool:
        """Write a single coil."""
        try:
            result = self.client.write_coil(
                address=address, value=value, slave=self.slave_id
            )
            return not result.isError()
        except (ModbusException, AttributeError) as err:
            _LOGGER.error("Error writing coil %s: %s", address, err)
            return False

    def read_all_registers(self) -> dict[str, Any]:
        """Read all registers and return as dictionary."""
        data = {}
        
        if self._lock:
            with self._lock:
                return self._read_all_registers_internal()
        return self._read_all_registers_internal()
    
    def _read_all_registers_internal(self) -> dict[str, Any]:
        """Internal method to read all registers."""
        import time
        data = {}

        # Try to read input registers in bulk first (more efficient)
        try:
            time.sleep(0.1)
            result = self.client.read_input_registers(
                address=REGISTER_WATER_INLET_TEMP, count=23, slave=self.slave_id
            )
            if not result.isError() and len(result.registers) >= 23:
                registers = result.registers
                # Parse temperature values (stored as value * 10)
                data["water_inlet_temp"] = self._convert_temp(registers[0])
                data["water_outlet_temp"] = self._convert_temp(registers[1])
                data["ambient_temp"] = self._convert_temp(registers[2])
                data["coil_temp"] = self._convert_temp(registers[3])
                data["discharge_temp"] = self._convert_temp(registers[4])
                data["suction_temp"] = self._convert_temp(registers[5])
                # Parse other values
                data["current_power"] = registers[10]
                data["flow_rate"] = registers[11]
                data["compressor_speed"] = registers[12]
                data["fan_speed"] = registers[13]
                data["pump_speed"] = registers[14]
                data["system_pressure"] = registers[15]
                data["error_code"] = registers[20]
                data["operating_state"] = registers[21]
                data["run_hours_high"] = registers[22]
        except Exception as err:
            _LOGGER.debug("Bulk read failed, falling back to individual reads: %s", err)
            # Fallback to individual reads
            registers_to_read = {
                "water_inlet_temp": REGISTER_WATER_INLET_TEMP,
                "water_outlet_temp": REGISTER_WATER_OUTLET_TEMP,
                "ambient_temp": REGISTER_AMBIENT_TEMP,
                "coil_temp": REGISTER_COIL_TEMP,
                "discharge_temp": REGISTER_DISCHARGE_TEMP,
                "suction_temp": REGISTER_SUCTION_TEMP,
                "current_power": REGISTER_CURRENT_POWER,
                "flow_rate": REGISTER_FLOW_RATE,
                "compressor_speed": REGISTER_COMPRESSOR_SPEED,
                "fan_speed": REGISTER_FAN_SPEED,
                "pump_speed": REGISTER_PUMP_SPEED,
                "system_pressure": REGISTER_SYSTEM_PRESSURE,
                "error_code": REGISTER_ERROR_CODE,
                "operating_state": REGISTER_OPERATING_STATE,
                "run_hours_high": REGISTER_RUN_HOURS,
            }

            for key, register in registers_to_read.items():
                value = self._read_input_register_internal(register)
                if value is not None:
                    if "temp" in key:
                        data[key] = self._convert_temp(value)
                    else:
                        data[key] = value

        # Read additional registers individually
        time.sleep(0.1)
        value = self._read_input_register_internal(REGISTER_RUN_HOURS_LOW)
        if value is not None:
            data["run_hours_low"] = value

        time.sleep(0.05)
        value = self._read_input_register_internal(REGISTER_COMPRESSOR_STARTS)
        if value is not None:
            data["compressor_starts"] = value

        time.sleep(0.05)
        value = self._read_input_register_internal(REGISTER_DEFROST_COUNT)
        if value is not None:
            data["defrost_count"] = value

        time.sleep(0.05)
        value = self._read_input_register_internal(REGISTER_COP)
        if value is not None:
            data["cop"] = value / 10

        time.sleep(0.05)
        value = self._read_input_register_internal(REGISTER_HEATING_CAPACITY)
        if value is not None:
            data["heating_capacity"] = value / 10

        time.sleep(0.05)
        value = self._read_input_register_internal(REGISTER_COOLING_CAPACITY)
        if value is not None:
            data["cooling_capacity"] = value / 10

        # Calculate total run hours
        if "run_hours_high" in data and "run_hours_low" in data:
            data["run_hours"] = (data["run_hours_high"] << 16) | data["run_hours_low"]

        # Read holding registers (control values)
        holding_registers = {
            "setpoint_temp": REGISTER_SETPOINT_TEMP,
            "operation_mode": REGISTER_OPERATION_MODE,
            "fan_mode": REGISTER_FAN_MODE,
            "min_pump_speed": REGISTER_MIN_PUMP_SPEED,
            "max_pump_speed": REGISTER_MAX_PUMP_SPEED,
            "dhw_setpoint": REGISTER_DHW_SETPOINT,
            "dhw_mode": REGISTER_DHW_MODE,
            "antifreeze_temp": REGISTER_ANTIFREEZE_TEMP,
            "max_outlet_temp": REGISTER_MAX_OUTLET_TEMP,
            "min_outlet_temp": REGISTER_MIN_OUTLET_TEMP,
        }

        for key, register in holding_registers.items():
            time.sleep(0.05)
            value = self._read_holding_register_internal(register)
            if value is not None:
                if "temp" in key:
                    data[key] = self._convert_temp(value)
                else:
                    data[key] = value

        # Read coils (binary values) - skip for now to reduce errors
        # Can be enabled later once transaction ID issues are resolved
        data["power"] = True  # Assume on if we're getting data
        data["heating_mode"] = data.get("operation_mode") == MODE_HEAT
        data["cooling_mode"] = data.get("operation_mode") == MODE_COOL
        data["dhw_mode_active"] = False
        data["silent_mode"] = False
        data["defrost_active"] = data.get("operating_state") == STATE_DEFROST
        data["pump_enabled"] = True

        return data
    
    def _convert_temp(self, value: int) -> float:
        """Convert temperature value from register."""
        if value > 32767:
            value = value - 65536
        return value / TEMP_SCALE

    def set_setpoint(self, temperature: float) -> bool:
        """Set the target water temperature."""
        value = int(temperature * TEMP_SCALE)
        return self.write_holding_register(REGISTER_SETPOINT_TEMP, value)

    def set_operation_mode(self, mode: int) -> bool:
        """Set the operation mode."""
        return self.write_holding_register(REGISTER_OPERATION_MODE, mode)

    def set_fan_mode(self, mode: int) -> bool:
        """Set the fan mode."""
        return self.write_holding_register(REGISTER_FAN_MODE, mode)

    def set_power(self, state: bool) -> bool:
        """Turn the heat pump on or off."""
        return self.write_coil(COIL_POWER, state)

    def set_dhw_mode(self, state: bool) -> bool:
        """Enable or disable DHW priority mode."""
        return self.write_coil(COIL_DHW_MODE, state)

    def set_silent_mode(self, state: bool) -> bool:
        """Enable or disable silent mode."""
        return self.write_coil(COIL_SILENT_MODE, state)
