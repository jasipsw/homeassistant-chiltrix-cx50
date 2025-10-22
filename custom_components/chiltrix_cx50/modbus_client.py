"""Modbus TCP client for Chiltrix CX50."""
import logging
import asyncio
from functools import partial
from typing import Any, Optional
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)


class ChiltrixModbusClient:
    """Modbus TCP client for Chiltrix CX50 heat pump."""

    def __init__(
        self,
        host: str,
        port: int = 502,
        slave_id: int = 1,
        timeout: int = 5,
        retries: int = 3,
    ):
        """Initialize the Modbus client.
        
        Args:
            host: IP address of the Modbus TCP device
            port: Modbus TCP port (default: 502)
            slave_id: Modbus slave/unit ID (default: 1)
            timeout: Connection timeout in seconds (default: 5)
            retries: Number of retry attempts (default: 3)
        """
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self.retries = retries
        self.client = None
        
        _LOGGER.info(
            f"Initializing Modbus client for {host}:{port}, slave_id={slave_id}"
        )

    async def connect(self) -> bool:
        """Connect to the Modbus device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Close any existing connection
            if self.client and self.client.connected:
                _LOGGER.debug("Closing existing connection before reconnecting")
                self.client.close()
                await asyncio.sleep(0.5)  # Give time for cleanup
            
            # Create new client instance
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout,
                retries=self.retries,
            )
            
            # Attempt connection
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.client.connect
            )
            
            if result:
                _LOGGER.info(f"Successfully connected to {self.host}:{self.port}")
            else:
                _LOGGER.error(f"Failed to connect to {self.host}:{self.port}")
                
            return result
            
        except Exception as e:
            _LOGGER.error(f"Connection error: {e}", exc_info=True)
            return False

    async def disconnect(self):
        """Disconnect from the Modbus device."""
        try:
            if self.client:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.client.close
                )
                _LOGGER.info("Disconnected from Modbus device")
        except Exception as e:
            _LOGGER.debug(f"Error during disconnect: {e}")

    def close(self):
        """Synchronous close method for compatibility."""
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            _LOGGER.debug(f"Error closing connection: {e}")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.client is not None and self.client.connected

    async def read_holding_registers(
        self, address: int, count: int = 1
    ) -> Optional[list[int]]:
        """Read holding registers from the device.
        
        Args:
            address: Starting register address
            count: Number of registers to read (default: 1)
            
        Returns:
            list[int]: Register values, or None if error
        """
        if not self.is_connected:
            _LOGGER.warning("Not connected, attempting to reconnect...")
            if not await self.connect():
                return None

        try:
            # Use keyword arguments for pymodbus 3.x compatibility
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                partial(
                    self.client.read_holding_registers,
                    address=address,
                    count=count,
                    slave_id=self.slave_id,
                ),
            )

            if result.isError():
                # Log detailed error information
                error_details = f"Function code: {getattr(result, 'function_code', 'N/A')}, "
                error_details += f"Exception code: {getattr(result, 'exception_code', 'N/A')}"
                _LOGGER.error(
                    f"Error reading registers at address 0x{address:X} ({address}): {error_details}"
                )
                return None

            return result.registers

        except ModbusException as e:
            _LOGGER.error(f"Modbus exception reading address {address}: {e}")
            return None
        except Exception as e:
            _LOGGER.error(
                f"Unexpected error reading address {address}: {e}", exc_info=True
            )
            return None

    async def write_register(self, address: int, value: int) -> bool:
        """Write a single register to the device.
        
        Args:
            address: Register address
            value: Value to write
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected:
            _LOGGER.warning("Not connected, attempting to reconnect...")
            if not await self.connect():
                return False

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                partial(
                    self.client.write_register,
                    address=address,
                    value=value,
                    slave_id=self.slave_id,
                ),
            )

            if result.isError():
                _LOGGER.error(f"Error writing register at address {address}: {result}")
                return False

            _LOGGER.debug(f"Successfully wrote {value} to register {address}")
            return True

        except ModbusException as e:
            _LOGGER.error(f"Modbus exception writing address {address}: {e}")
            return False
        except Exception as e:
            _LOGGER.error(
                f"Unexpected error writing address {address}: {e}", exc_info=True
            )
            return False

    async def write_registers(self, address: int, values: list[int]) -> bool:
        """Write multiple registers to the device.
        
        Args:
            address: Starting register address
            values: List of values to write
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected:
            _LOGGER.warning("Not connected, attempting to reconnect...")
            if not await self.connect():
                return False

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                partial(
                    self.client.write_registers,
                    address=address,
                    values=values,
                    slave_id=self.slave_id,
                ),
            )

            if result.isError():
                _LOGGER.error(
                    f"Error writing registers at address {address}: {result}"
                )
                return False

            _LOGGER.debug(
                f"Successfully wrote {len(values)} registers starting at {address}"
            )
            return True

        except ModbusException as e:
            _LOGGER.error(f"Modbus exception writing address {address}: {e}")
            return False
        except Exception as e:
            _LOGGER.error(
                f"Unexpected error writing address {address}: {e}", exc_info=True
            )
            return False

    async def read_coils(self, address: int, count: int = 1) -> Optional[list[bool]]:
        """Read coils from the device.
        
        Args:
            address: Starting coil address
            count: Number of coils to read (default: 1)
            
        Returns:
            list[bool]: Coil values, or None if error
        """
        if not self.is_connected:
            _LOGGER.warning("Not connected, attempting to reconnect...")
            if not await self.connect():
                return None

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                partial(
                    self.client.read_coils,
                    address=address,
                    count=count,
                    slave_id=self.slave_id,
                ),
            )

            if result.isError():
                _LOGGER.error(f"Error reading coils at address {address}: {result}")
                return None

            return result.bits[:count]

        except ModbusException as e:
            _LOGGER.error(f"Modbus exception reading coils at address {address}: {e}")
            return None
        except Exception as e:
            _LOGGER.error(
                f"Unexpected error reading coils at address {address}: {e}",
                exc_info=True,
            )
            return None

    async def write_coil(self, address: int, value: bool) -> bool:
        """Write a single coil to the device.
        
        Args:
            address: Coil address
            value: Value to write (True/False)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected:
            _LOGGER.warning("Not connected, attempting to reconnect...")
            if not await self.connect():
                return False

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                partial(
                    self.client.write_coil,
                    address=address,
                    value=value,
                    slave_id=self.slave_id,
                ),
            )

            if result.isError():
                _LOGGER.error(f"Error writing coil at address {address}: {result}")
                return False

            _LOGGER.debug(f"Successfully wrote {value} to coil {address}")
            return True

        except ModbusException as e:
            _LOGGER.error(f"Modbus exception writing coil at address {address}: {e}")
            return False
        except Exception as e:
            _LOGGER.error(
                f"Unexpected error writing coil at address {address}: {e}",
                exc_info=True,
            )
            return False
