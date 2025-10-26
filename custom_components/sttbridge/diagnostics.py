"""Diagnostics support for STT Bridge."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    host = data["host"]
    port = data["port"]
    base_url = f"http://{host}:{port}"

    # Redact token
    config_data = {**entry.data}
    if "token" in config_data:
        config_data["token"] = "REDACTED"

    diagnostics_data = {
        "config": config_data,
        "options": {**entry.options},
    }

    # Try to get health and voices
    session = async_get_clientsession(hass)
    try:
        async with session.get(f"{base_url}/healthz") as resp:
            diagnostics_data["health"] = {
                "status": resp.status,
                "body": await resp.text(),
            }
    except Exception as e:
        diagnostics_data["health"] = {"error": str(e)}

    try:
        async with session.get(f"{base_url}/voices") as resp:
            diagnostics_data["voices"] = {
                "status": resp.status,
                "body": await resp.json() if resp.content_type == 'application/json' else await resp.text(),
            }
    except Exception as e:
        diagnostics_data["voices"] = {"error": str(e)}

    return diagnostics_data
