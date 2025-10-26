"""Config flow for STT Bridge."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host", default="127.0.0.1"): str,
        vol.Required("port", default=8787): int,
        vol.Optional("token"): str,
    }
)


async def validate_input(hass, data):
    """Validate the user input allows us to connect."""
    host = data["host"]
    port = data["port"]
    base_url = f"http://{host}:{port}"
    session = aiohttp_client.async_get_clientsession(hass)
    try:
        async with session.get(f"{base_url}/healthz") as resp:
            if resp.status == 200:
                return {"title": "STT Bridge"}
            return {"base": "cannot_connect"}
    except Exception:
        _LOGGER.exception("Could not connect to STT Bridge")
        return {"base": "cannot_connect"}


class STTBridgeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STT Bridge."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            info, errors = await self._validate_and_create(user_input)
            if not errors:
                await self.async_set_unique_id(f'{user_input["host"]}:{user_input["port"]}')
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _validate_and_create(self, data):
        """Validate the user input and create the entry."""
        errors = {}
        info = await validate_input(self.hass, data)
        if "base" in info:
            errors["base"] = info["base"]

        return info, errors
