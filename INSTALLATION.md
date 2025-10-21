# Installation and Setup Guide

## Directory Structure

Your Home Assistant custom components directory should look like this:

```
custom_components/
└── chiltrix_cx50/
    ├── __init__.py
    ├── binary_sensor.py
    ├── climate.py
    ├── config_flow.py
    ├── const.py
    ├── manifest.json
    ├── modbus_client.py
    ├── number.py
    ├── select.py
    ├── sensor.py
    ├── strings.json
    ├── switch.py
    └── translations/
        └── en.json
```

## Step-by-Step Installation

### 1. Create Directory Structure

SSH into your Home Assistant instance or use the File Editor add-on:

```bash
cd /config
mkdir -p custom_components/chiltrix_cx50/translations
```

### 2. Copy All Files

Copy each of the provided Python files into the `custom_components/chiltrix_cx50/` directory:

- `__init__.py`
- `binary_sensor.py`
- `climate.py`
- `config_flow.py`
- `const.py`
- `manifest.json`
- `modbus_client.py`
- `number.py`
- `select.py`
- `sensor.py`
- `strings.json`
- `switch.py`

Copy the translation file:
- `translations/en.json`

### 3. Install Dependencies

The integration requires `pymodbus`. Home Assistant will automatically install this when you add the integration, but you can also install it manually:

```bash
pip install pymodbus==3.5.4
```

### 4. Restart Home Assistant

After copying all files:
1. Go to **Settings** → **System**
2. Click **Restart** in the top right
3. Wait for Home Assistant to fully restart

### 5. Configure Your Waveshare Device

Before adding the integration, ensure your Waveshare RS485 to Modbus TCP device is properly configured:

#### Waveshare Configuration:
1. Connect to the Waveshare device's web interface (usually via its IP address)
2. Configure Modbus TCP settings:
   - **Protocol**: Modbus TCP
   - **Port**: 502 (default)
   - **Baud Rate**: 9600 or as specified by Chiltrix (check your manual)
   - **Data Bits**: 8
   - **Stop Bits**: 1
   - **Parity**: None (or as specified)
   - **Slave ID**: 1 (or your configured ID)

3. Save settings and reboot the Waveshare device

#### Network Configuration:
1. Assign a static IP to the Waveshare device, or
2. Create a DHCP reservation in your router for the device's MAC address
3. Ensure the device is on the same network as Home Assistant
4. Test connectivity: `ping <waveshare-ip>` from Home Assistant terminal

### 6. Verify RS485 Wiring

Ensure proper RS485 connections to the Chiltrix heat pump:

```
Waveshare RS485    →    Chiltrix CX50-2
─────────────────────────────────────────
A (or D+)          →    A/Data+ terminal
B (or D-)          →    B/Data- terminal
GND                →    Common GND (if available)
```

**Important Notes:**
- Do not connect A to B or B to A (this is a common mistake)
- Maintain proper polarity throughout the RS485 bus
- Use twisted pair cable for RS485 connections
- Keep RS485 cable length under 1200m (ideally much shorter)
- Add 120Ω termination resistors at both ends if required by your setup

### 7. Add the Integration in Home Assistant

1. Go to **Settings** → **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for "Chiltrix CX50-2"
4. Enter your configuration:
   - **IP Address**: The IP of your Waveshare device (e.g., `192.168.1.100`)
   - **Port**: `502` (Modbus TCP default)
   - **Slave ID**: `1` (or your configured Modbus slave ID)
   - **Scan Interval**: `30` seconds (recommended starting value)

5. Click **Submit**

If connection is successful, you'll see all entities appear!

### 8. Verify Operation

1. Go to **Settings** → **Devices & Services** → **Chiltrix CX50-2**
2. Click on the device to see all entities
3. Check that sensors are reporting values:
   - Water Inlet/Outlet Temperatures should show reasonable values
   - Operating State should reflect current status
   - Error Code should show "No Error" if system is healthy

### 9. Adjust Register Addresses (If Needed)

If sensors show no data or incorrect values, you may need to adjust register addresses:

1. Stop Home Assistant
2. Edit `custom_components/chiltrix_cx50/const.py`
3. Locate the register definitions (starting around line 20)
4. Adjust addresses based on your Chiltrix documentation:
   - Refer to "Cx34-1,2,3/Cx50-2/Cx35-1 Modbus Protocol" document
   - Check the Loxone library for CX50-2 registers
   - Consult Remote Gateway BACnet Guide

5. Common adjustments:
   ```python
   # Example: If water inlet temp is at register 100 instead of 1000:
   REGISTER_WATER_INLET_TEMP = 100
   
   # If setpoint is at register 50:
   REGISTER_SETPOINT_TEMP = 50
   ```

6. Save the file and restart Home Assistant

### 10. Testing Modbus Communication

If you're having issues, test Modbus communication manually:

#### Using modpoll (Linux/Mac):
```bash
# Install modpoll
sudo apt-get install modpoll

# Read register 1000 (adjust as needed)
modpoll -m tcp -a 1 -r 1000 -c 1 <waveshare-ip>
```

#### Using Python:
```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# Read input register 1000
result = client.read_input_registers(address=1000, count=1, slave=1)
print(f"Register 1000: {result.registers[0]}")

client.close()
```

## Common Issues and Solutions

### Issue: "Cannot Connect" Error

**Solutions:**
1. Verify Waveshare IP address: `ping <ip-address>`
2. Check port 502 is open: `telnet <ip-address> 502`
3. Verify Modbus TCP is enabled on Waveshare device
4. Check firewall rules on your network
5. Ensure Waveshare device is powered on
6. Try a different Ethernet cable

### Issue: Entities Show "Unknown" or "Unavailable"

**Solutions:**
1. Check Home Assistant logs: **Settings** → **System** → **Logs**
2. Look for Modbus errors or timeout messages
3. Increase scan interval to 60 seconds
4. Verify slave ID matches Chiltrix configuration
5. Check RS485 wiring and connections
6. Adjust register addresses in `const.py`

### Issue: Values Are Incorrect or Scaled Wrong

**Solutions:**
1. Temperature values should be in Celsius
2. Check if your registers use different scaling (e.g., ×100 instead of ×10)
3. Adjust TEMP_SCALE in `const.py` if needed
4. Verify register addresses match your Chiltrix model

### Issue: Can Read But Cannot Control

**Solutions:**
1. Verify you're using holding registers for writable values
2. Check that CX50-2 allows remote control (may need to enable)
3. Ensure Modbus write access is enabled on Waveshare device
4. Try writing values manually with modpoll to test

### Issue: Integration Not Showing in Add Integration

**Solutions:**
1. Verify all files are in correct directory structure
2. Check `manifest.json` is valid JSON (use JSON validator)
3. Clear Home Assistant cache: delete `custom_components/.storage`
4. Restart Home Assistant completely (not just reload)
5. Check logs for Python syntax errors

## Performance Optimization

### Scan Interval Recommendations:

- **30 seconds**: Good balance for most users
- **15 seconds**: More responsive, higher network load
- **60 seconds**: Lower network traffic, less responsive
- **5 seconds**: Use only for testing (may cause Modbus congestion)

### Network Optimization:

1. Use wired Ethernet for Waveshare device (not WiFi)
2. Place Waveshare device on same network segment as Home Assistant
3. Avoid long Ethernet cable runs (keep under 100m)
4. Use quality Ethernet cables (Cat5e or better)

## Advanced Configuration

### Custom Register Mapping

Create a file `custom_registers.py` to override defaults:

```python
# custom_components/chiltrix_cx50/custom_registers.py
CUSTOM_REGISTERS = {
    "REGISTER_WATER_INLET_TEMP": 100,
    "REGISTER_WATER_OUTLET_TEMP": 101,
    # Add your custom mappings
}
```

### Multiple Heat Pumps

To add multiple CX50-2 units:
1. Each needs its own Modbus slave ID (1, 2, 3, etc.)
2. Add the integration multiple times with different configurations
3. Each unit will appear as a separate device

## Getting Help

1. **Check Logs**: Settings → System → Logs (filter by "chiltrix")
2. **Enable Debug Logging**: Add to `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.chiltrix_cx50: debug
       pymodbus: debug
   ```
3. **Test Hardware**: Use modpoll or Python script to verify Modbus communication
4. **Consult Documentation**: Check Chiltrix manuals and Loxone library
5. **Community**: Home Assistant forums and GitHub issues

## Next Steps

After successful installation:
1. Create automation templates
2. Add entities to Lovelace dashboards
3. Set up alerts for error conditions
4. Create energy monitoring dashboards
5. Integrate with weather forecasts for optimization

Enjoy your Chiltrix CX50-2 integration!
