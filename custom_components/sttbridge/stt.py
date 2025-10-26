"""STT platform for STT Bridge."""
from __future__ import annotations

import logging

import aiohttp
from homeassistant.components import stt
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
    """Set up STT Bridge STT platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    host = data["host"]
    port = data["port"]
    token = data.get("token")
    base_url = f"http://{host}:{port}"

    async_add_entities([STTBridgeSTTProvider(hass, base_url, token, config_entry)])


class STTBridgeSTTProvider(stt.SpeechToTextEntity):
    """The STT Bridge STT provider."""

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
        self._attr_name = "STT Bridge"
        self._attr_unique_id = config_entry.entry_id

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        # TODO: Get from /voices endpoint
        return ["de-DE", "en-US"]

    @property
    def supported_formats(self) -> list[stt.AudioFormats]:
        """Return a list of supported audio formats."""
        return [stt.AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[stt.AudioCodecs]:
        """Return a list of supported audio codecs."""
        return [stt.AudioCodecs.PCM]

    @property
    def supported_sample_rates(self) -> list[stt.AudioSampleRates]:
        """Return a list of supported audio sample rates."""
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_bit_rates(self) -> list[stt.AudioBitRates]:
        """Return a list of supported audio bit rates."""
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_channels(self) -> list[stt.AudioChannels]:
        """Return a list of supported audio channels."""
        return [stt.AudioChannels.MONO]

    async def async_process_audio_stream(
        self, metadata: stt.SpeechMetadata, stream: stt.AudioStream
    ) -> stt.SpeechResult:
        """Process an audio stream."""
        session = async_get_clientsession(self.hass)
        headers = {
            "Content-Type": "audio/wav",
            "X-Language": metadata.language,
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with session.post(
                f"{self._base_url}/stt", data=stream, headers=headers
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error(
                        "Error getting STT result: %s - %s",
                        resp.status,
                        await resp.text(),
                    )
                    return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

                result = await resp.json()
                text = result.get("text")
                if text:
                    return stt.SpeechResult(text, stt.SpeechResultState.SUCCESS)

                _LOGGER.warning("STT result from server did not contain text: %s", result)
                return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
        except aiohttp.ClientError as e:
            _LOGGER.error("Error communicating with STT Bridge for STT: %s", e)
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
