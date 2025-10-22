"""Config flow for Chiltrix CX50 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

from .const import DOMAIN, CONF_SLAVE_ID, DEFAULT_PORT, DEFAULT_SLAVE_ID, DEFAULT_SCAN_INTERVAL
from .modbus_client import ChiltrixModbusClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    client = ChiltrixModbusClient(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        slave_id=data[CONF_SLAVE_ID],
    )

    try:
        if not await client.connect():
            raise CannotConnect("Failed to connect to the device")

        # Try to read test registers to verify communication
        # Try multiple addresses that appear in device logs as working
        test_addresses = [0xF3, 0xF4, 0x100, 0x119]  # Operating state, error code, power, run hours
        test_success = False
        
        for address in test_addresses:
            test_result = await client.read_holding_registers(address=address, count=1)
            if test_result is not None:
                _LOGGER.info(f"Successfully read test register at address 0x{address:X}")
                test_success = True
                break
            _LOGGER.debug(f"Failed to read test register at address 0x{address:X}, trying next...")
        
        if not test_success:
            raise CannotConnect("Connected but unable to read data from device. Register addresses may need adjustment.")

        await client.disconnect()

    except Exception as err:
        _LOGGER.error("Error validating connection: %s", err)
        raise CannotConnect(f"Failed to connect: {err}") from err

    # Return info that you want to store in the config entry.
    return {"title": f"Chiltrix CX50 ({data[CONF_HOST]})"}


class ChiltrixCX50ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chiltrix CX50."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors[CONF_HOST] = "invalid_host"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(HomeAssistantError):
    """Error to indicate there is invalid host."""
