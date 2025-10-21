"""Constants for the Chiltrix CX50-2 integration."""

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
