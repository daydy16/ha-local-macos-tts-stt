"""TTS platform for STT Bridge."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.components.tts import Provider, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up STT Bridge TTS platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    host = data["host"]
    port = data["port"]
    token = data.get("token")
    base_url = f"http://{host}:{port}"

    async_add_entities([STTBridgeProvider(hass, base_url, token, config_entry)])


class STTBridgeProvider(Provider):
    """The STT Bridge TTS provider."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        token: str | None,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the provider."""
        self.hass = hass
        self._base_url = base_url
        self._token = token
        self._config_entry = config_entry
        self.name = "STT Bridge"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the TTS platform."""
        return self._config_entry.entry_id

    @property
    def default_language(self) -> str:
        """Return the default language."""
        # TODO: Make configurable in options flow
        return "de-DE"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        # TODO: Get from /voices endpoint
        return ["de-DE", "en-US"]

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options like voice, speed."""
        return ["voice", "rate", "pitch"]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS audio."""
        session = async_get_clientsession(self.hass)
        payload = {"text": message, "language": language}
        if options:
            payload.update(options)

        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with session.post(
                f"{self._base_url}/tts", json=payload, headers=headers
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error(
                        "Error getting TTS audio: %s - %s",
                        resp.status,
                        await resp.text(),
                    )
                    return (None, None)
                data = await resp.read()
                return ("wav", data)
        except aiohttp.ClientError as e:
            _LOGGER.error("Error communicating with STT Bridge for TTS: %s", e)
            return (None, None)
