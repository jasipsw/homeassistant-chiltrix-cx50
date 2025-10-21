# Chiltrix CX50-2 Heat Pump Integration for Home Assistant

A custom integration for Home Assistant to control and monitor the Chiltrix CX50-2 heat pump via Modbus TCP using a Waveshare RS485 to Ethernet device.

## Features

- **Comprehensive Monitoring**: All key sensors including temperatures, flow rates, power consumption, and system status
- **Climate Control**: Full HVAC control with heating, cooling, and auto modes
- **Configuration UI**: Easy setup through Home Assistant's configuration flow
- **Multiple Control Options**: Switches, numbers, and selects for fine-grained control
- **Diagnostic Information**: Run hours, error codes, compressor starts, and defrost counts

## Hardware Requirements

- Chiltrix CX50-2 heat pump
- Waveshare RS485 to Modbus TCP device (or similar) connected via wired Ethernet
- RS485 connection from Waveshare device to Chiltrix heat pump

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL
6. Select "Integration" as the category
7. Click "Add"
8. Search for "Chiltrix CX50-2" and install

### Manual Installation

1. Copy the `custom_components/chiltrix_cx50` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Chiltrix CX50-2**
4. Enter the required information:
   - **IP Address**: The IP address of your Waveshare RS485 device
   - **Port**: Modbus TCP port (default: 502)
   - **Slave ID**: Modbus slave ID (default: 1)
   - **Scan Interval**: How often to poll the device in seconds (default: 30)

## Entities Created

### Sensors

**Temperature Sensors:**
- Water Inlet Temperature
- Water Outlet Temperature
- Ambient Temperature
- Coil Temperature
- Discharge Temperature
- Suction Temperature
- Setpoint Temperature
- DHW Setpoint
- Antifreeze Temperature

**Performance Sensors:**
- Current Power (W)
- Flow Rate (L/min)
- Compressor Speed (%)
- Fan Speed (%)
- Pump Speed (%)
- System Pressure (bar)
- Coefficient of Performance (COP)
- Heating Capacity (kW)
- Cooling Capacity (kW)

**Status Sensors:**
- Operating State
- Error Code
- Total Run Hours
- Compressor Starts
- Defrost Count

### Binary Sensors

- Power
- Heating Mode
- Cooling Mode
- DHW Mode Active
- Silent Mode
- Defrost Active
- Pump Enabled
- Error Status

### Climate Entity

Full climate control with:
- HVAC modes: Off, Heat, Cool, Auto
- Current and target temperature
- Turn on/off capability

### Switches

- Power
- DHW Priority Mode
- Silent Mode

### Number Entities

- Setpoint Temperature (15-60°C)
- DHW Setpoint (35-65°C)
- Max Outlet Temperature (20-65°C)
- Min Outlet Temperature (10-40°C)
- Antifreeze Temperature (-10-10°C)
- Min Pump Speed (20-100%)
- Max Pump Speed (30-100%)

### Select Entities

- Operation Mode (Off, Heating, Cooling, Auto, DHW)
- Fan Mode (Auto, Low, Medium, High)

## Modbus Register Information

The integration uses Modbus TCP to communicate with the Chiltrix CX50-2. The register definitions are based on:

- Chiltrix CX34/CX35 projects (similar architecture)
- Remote Gateway BACnet Guide
- Cx34-1,2,3/Cx50-2/Cx35-1 Modbus Protocol documentation

**Note**: The register addresses in this integration are based on typical heat pump implementations and CX34/CX35 references. You may need to adjust register addresses in `const.py` based on your specific CX50-2 firmware version. Consult your Chiltrix documentation or the Loxone library for exact register mappings.

## Wiring

Connect your Waveshare RS485 device:

1. **RS485 Connections to Chiltrix:**
   - A/D+ → Chiltrix RS485 A/D+
   - B/D- → Chiltrix RS485 B/D-
   - GND → Common ground (if available)

2. **Ethernet Connection:**
   - Connect Waveshare device to your network via Ethernet cable
   - Assign a static IP or use DHCP reservation

3. **Power:**
   - Power the Waveshare device according to manufacturer specifications

## Troubleshooting

### Cannot Connect

1. Verify the Waveshare device IP address is correct and reachable
2. Check that port 502 is open and not blocked by firewall
3. Ensure RS485 wiring is correct (A to A, B to B)
4. Verify the Modbus slave ID matches your heat pump configuration
5. Check that the Chiltrix unit is powered on

### No Data or Incorrect Values

1. The register addresses may need adjustment for your specific CX50-2 model
2. Check Home Assistant logs for Modbus communication errors
3. Try adjusting the scan interval (increase if seeing timeout errors)
4. Verify RS485 termination resistors if required

### Adjusting Register Addresses

If sensors show incorrect values or no data:

1. Edit `custom_components/chiltrix_cx50/const.py`
2. Adjust register addresses based on your Chiltrix documentation
3. Restart Home Assistant
4. Test individual registers using a Modbus testing tool

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the Chiltrix documentation for your specific model
- Consult the gonzojive/heatpump GitHub project for CX34 register references

## Credits

- Register definitions inspired by [gonzojive/heatpump](https://github.com/gonzojive/heatpump) (CX34 project)
- Based on Chiltrix CX34/CX35 Modbus implementations
- Uses pymodbus library for Modbus TCP communication

## License

MIT License - See LICENSE file for details

## Disclaimer

This integration is not officially supported by Chiltrix. Use at your own risk. Always refer to official Chiltrix documentation for your specific model.
