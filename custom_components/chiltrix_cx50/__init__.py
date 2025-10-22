"""The Chiltrix CX50 integration."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, PLATFORMS
from .modbus_client import ChiltrixModbusClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chiltrix CX50 from a config entry."""
    host = entry.data["host"]
    port = entry.data.get("port", 502)
    slave_id = entry.data.get("slave_id", 1)
    scan_interval = entry.data.get("scan_interval", 30)
    
    # Create Modbus client
    client = ChiltrixModbusClient(
        host=host,
        port=port,
        slave_id=slave_id,
    )
    
    # Connect to device
    if not await client.connect():
        _LOGGER.error("Failed to connect to Chiltrix CX50 at %s:%s", host, port)
        return False
    
    # Create data update coordinator
    async def async_update_data():
        """Fetch data from Chiltrix."""
        try:
            data = {}
            
            # Define all registers we need to read - based on working YAML config
            registers_to_read = [
                # Operating mode and setpoints (141-144)
                141, 142, 143, 144,
                
                # Temperature sensors C00-C06 (200-206)
                200, 201, 202, 203, 204, 205, 206,
                
                # Performance registers (209, 213-246)
                209, 213, 214, 215, 216, 217, 218, 219, 220,
                221, 222, 223, 224, 225, 226, 227, 228, 229, 230,
                231, 232, 233, 234, 235, 236, 237, 238, 239, 240,
                241, 242, 243, 244, 245, 246,
                
                # Electrical and system status (255-264)
                255, 256, 257, 258, 259, 260, 261, 262, 263, 264,
                
                # Inlet water temp (281)
                281,
            ]
            
            # Read each register and map to named keys
            register_map = {
                141: "operating_mode",
                142: "cooling_target",
                143: "heating_target",
                144: "dhw_target",
                200: "c00_temp",
                201: "c01_temp",
                202: "ambient_temp",
                203: "suction_temp",
                204: "plate_exchange_temp",
                205: "water_outlet_temp",
                206: "c06_temp",
                209: "compressor_current",
                213: "pump_flow",
                227: "compressor_frequency",
                244: "fan_type",
                245: "ec_fan_1_speed",
                246: "ec_fan_2_speed",
                255: "input_voltage",
                256: "input_current",
                257: "compressor_phase_current",
                258: "bus_line_voltage",
                259: "fan_shutdown_code",
                260: "ipm_temp",
                261: "compressor_run_hours",
                262: "e_heater_power",
                263: "din6_switch",
                264: "din7_switch",
                281: "inlet_water_temp",
            }

            for address in registers_to_read:
                try:
                    result = await client.read_holding_registers(address, 1)
                    if result and len(result) > 0:
                        # Store with both numeric address and named key
                        data[address] = result[0]
                        if address in register_map:
                            data[register_map[address]] = result[0]
                except Exception as err:
                    _LOGGER.debug("Error reading register %s: %s", address, err)
                    # Continue reading other registers even if one fails
                    continue

            if not data:
                raise UpdateFailed("No data received from device")

            return data
            
        except Exception as err:
            _LOGGER.error("Error communicating with Chiltrix: %s", err)
            raise UpdateFailed(f"Error communicating with device: {err}")
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Chiltrix CX50 {host}",
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
        # Close Modbus connection
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await client.disconnect()
        
        # Remove data
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
