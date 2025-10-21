#!/usr/bin/env python3
"""
Chiltrix CX50-2 Integration Installer
Run this script in your Home Assistant config directory to install the integration.
Usage: python3 install_chiltrix.py
"""

import os
import sys

# Base directory
BASE_DIR = "custom_components/chiltrix_cx50"
TRANSLATIONS_DIR = f"{BASE_DIR}/translations"

# File contents as dictionary
FILES = {
    f"{BASE_DIR}/__init__.py": '''"""The Chiltrix CX50-2 Heat Pump integration."""
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
''',

    f"{BASE_DIR}/const.py": '''"""Constants for the Chiltrix CX50-2 integration."""

DOMAIN = "chiltrix_cx50"

# Configuration
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30

# Modbus Register Definitions (based on CX34/CX35 and typical heat pump registers)
# These addresses may need adjustment based on actual CX50-2 documentation

# Input Registers (Read-only sensor values)
REGISTER_WATER_INLET_TEMP = 1000  # Water inlet temperature
REGISTER_WATER_OUTLET_TEMP = 1001  # Water outlet temperature
REGISTER_AMBIENT_TEMP = 1002  # Outdoor ambient temperature
REGISTER_COIL_TEMP = 1003  # Evaporator/condenser coil temperature
REGISTER_DISCHARGE_TEMP = 1004  # Compressor discharge temperature
REGISTER_SUCTION_TEMP = 1005  # Compressor suction temperature
REGISTER_CURRENT_POWER = 1010  # Current power consumption (W)
REGISTER_FLOW_RATE = 1011  # Water flow rate (L/min)
REGISTER_COMPRESSOR_SPEED = 1012  # Compressor speed (%)
REGISTER_FAN_SPEED = 1013  # Fan speed (%)
REGISTER_PUMP_SPEED = 1014  # Pump speed (%)
REGISTER_SYSTEM_PRESSURE = 1015  # System pressure
REGISTER_ERROR_CODE = 1020  # Current error code
REGISTER_OPERATING_STATE = 1021  # Operating state
REGISTER_RUN_HOURS = 1030  # Total run hours (high word)
REGISTER_RUN_HOURS_LOW = 1031  # Total run hours (low word)
REGISTER_COMPRESSOR_STARTS = 1032  # Compressor start count
REGISTER_DEFROST_COUNT = 1033  # Defrost cycle count
REGISTER_COP = 1040  # Coefficient of Performance
REGISTER_HEATING_CAPACITY = 1041  # Current heating capacity (kW)
REGISTER_COOLING_CAPACITY = 1042  # Current cooling capacity (kW)

# Holding Registers (Read/Write control values)
REGISTER_SETPOINT_TEMP = 2000  # Target water temperature setpoint
REGISTER_OPERATION_MODE = 2001  # Operation mode (0=Off, 1=Heat, 2=Cool, 3=Auto)
REGISTER_FAN_MODE = 2002  # Fan mode (0=Auto, 1=Low, 2=Med, 3=High)
REGISTER_MIN_PUMP_SPEED = 2003  # Minimum pump speed (%)
REGISTER_MAX_PUMP_SPEED = 2004  # Maximum pump speed (%)
REGISTER_DHW_SETPOINT = 2005  # Domestic hot water setpoint
REGISTER_DHW_MODE = 2006  # DHW mode enable/disable
REGISTER_ANTIFREEZE_TEMP = 2007  # Antifreeze protection temperature
REGISTER_MAX_OUTLET_TEMP = 2008  # Maximum outlet temperature limit
REGISTER_MIN_OUTLET_TEMP = 2009  # Minimum outlet temperature limit

# Coil Registers (Read/Write binary values)
COIL_POWER = 0  # Power on/off
COIL_HEATING_MODE = 1  # Heating mode enable
COIL_COOLING_MODE = 2  # Cooling mode enable
COIL_DHW_MODE = 3  # DHW priority mode
COIL_SILENT_MODE = 4  # Silent/quiet mode
COIL_DEFROST_MODE = 5  # Manual defrost trigger
COIL_PUMP_ENABLE = 6  # Pump enable/disable

# Operation modes
MODE_OFF = 0
MODE_HEAT = 1
MODE_COOL = 2
MODE_AUTO = 3
MODE_DHW = 4

OPERATION_MODES = {
    MODE_OFF: "Off",
    MODE_HEAT: "Heating",
    MODE_COOL: "Cooling",
    MODE_AUTO: "Auto",
    MODE_DHW: "DHW",
}

# Operating states
STATE_IDLE = 0
STATE_HEATING = 1
STATE_COOLING = 2
STATE_DEFROST = 3
STATE_DHW = 4
STATE_STANDBY = 5
STATE_ERROR = 99

OPERATING_STATES = {
    STATE_IDLE: "Idle",
    STATE_HEATING: "Heating",
    STATE_COOLING: "Cooling",
    STATE_DEFROST: "Defrost",
    STATE_DHW: "DHW",
    STATE_STANDBY: "Standby",
    STATE_ERROR: "Error",
}

# Temperature conversion (registers store value * 10)
TEMP_SCALE = 10

# Fan modes
FAN_AUTO = 0
FAN_LOW = 1
FAN_MEDIUM = 2
FAN_HIGH = 3

FAN_MODES = {
    FAN_AUTO: "Auto",
    FAN_LOW: "Low",
    FAN_MEDIUM: "Medium",
    FAN_HIGH: "High",
}
''',

    f"{BASE_DIR}/manifest.json": '''{
  "domain": "chiltrix_cx50",
  "name": "Chiltrix CX50-2 Heat Pump",
  "codeowners": [],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/yourusername/chiltrix_cx50",
  "integration_type": "device",
  "iot_class": "local_polling",
  "requirements": ["pymodbus==3.5.4"],
  "version": "1.0.0"
}
''',

    f"{BASE_DIR}/strings.json": '''{
  "config": {
    "step": {
      "user": {
        "title": "Connect to Chiltrix CX50-2",
        "description": "Enter the connection details for your Chiltrix CX50-2 heat pump connected via Waveshare RS485 to Modbus TCP device.",
        "data": {
          "host": "IP Address",
          "port": "Port",
          "slave_id": "Modbus Slave ID",
          "scan_interval": "Scan Interval (seconds)"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect to the device. Please check the IP address, port, and ensure the Waveshare RS485 device is powered on and connected.",
      "unknown": "Unexpected error occurred"
    },
    "abort": {
      "already_configured": "This device is already configured"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Chiltrix CX50-2 Options",
        "description": "Configure options for your Chiltrix CX50-2 heat pump.",
        "data": {
          "slave_id": "Modbus Slave ID",
          "scan_interval": "Scan Interval (seconds)"
        }
      }
    }
  }
}
''',

    f"{TRANSLATIONS_DIR}/en.json": '''{
  "config": {
    "step": {
      "user": {
        "title": "Connect to Chiltrix CX50-2",
        "description": "Enter the connection details for your Chiltrix CX50-2 heat pump connected via Waveshare RS485 to Modbus TCP device.",
        "data": {
          "host": "IP Address",
          "port": "Port",
          "slave_id": "Modbus Slave ID",
          "scan_interval": "Scan Interval (seconds)"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect to the device. Please check the IP address, port, and ensure the Waveshare RS485 device is powered on and connected.",
      "unknown": "Unexpected error occurred"
    },
    "abort": {
      "already_configured": "This device is already configured"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Chiltrix CX50-2 Options",
        "description": "Configure options for your Chiltrix CX50-2 heat pump.",
        "data": {
          "slave_id": "Modbus Slave ID",
          "scan_interval": "Scan Interval (seconds)"
        }
      }
    }
  }
}
'''
}

# Note: Due to length constraints, the remaining files (modbus_client.py, config_flow.py, 
# sensor.py, binary_sensor.py, climate.py, switch.py, number.py, select.py) 
# should be copied manually from the artifacts above.

def create_directories():
    """Create necessary directories."""
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(TRANSLATIONS_DIR, exist_ok=True)
    print(f"✓ Created directory: {BASE_DIR}")
    print(f"✓ Created directory: {TRANSLATIONS_DIR}")

def write_files():
    """Write all files."""
    for filepath, content in FILES.items():
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Created file: {filepath}")

def main():
    """Main installer function."""
    print("=" * 60)
    print("Chiltrix CX50-2 Integration Installer")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("configuration.yaml"):
        print("ERROR: Please run this script from your Home Assistant config directory")
        print("(the directory containing configuration.yaml)")
        sys.exit(1)
    
    print("Installing Chiltrix CX50-2 integration...")
    print()
    
    create_directories()
    print()
    write_files()
    
    print()
    print("=" * 60)
    print("Installation Complete!")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: You still need to manually copy these files:")
    print("   - modbus_client.py")
    print("   - config_flow.py")
    print("   - sensor.py")
    print("   - binary_sensor.py")
    print("   - climate.py")
    print("   - switch.py")
    print("   - number.py")
    print("   - select.py")
    print()
    print("Copy them from the artifacts provided into:")
    print(f"   {BASE_DIR}/")
    print()
    print("Next steps:")
    print("1. Copy the remaining Python files")
    print("2. Restart Home Assistant")
    print("3. Go to Settings → Devices & Services")
    print("4. Click 'Add Integration' and search for 'Chiltrix CX50-2'")
    print()

if __name__ == "__main__":
    main()
