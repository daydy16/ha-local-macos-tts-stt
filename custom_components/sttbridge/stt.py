"""STT platform for STT Bridge."""
from __future__ import annotations

import asyncio
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
        self._attr_name = "STT/TTS Bridge STT"
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
        return [stt.AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: stt.SpeechMetadata, stream: stt.AudioStream
    ) -> stt.SpeechResult:
        """Process an audio stream using WebSocket for real-time streaming."""
        # Use WebSocket URL for streaming
        ws_url = self._base_url.replace("http://", "ws://") + "/stt/stream"
        
        # Add language parameter
        ws_url += f"?lang={metadata.language}"
        
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        session = async_get_clientsession(self.hass)
        
        try:
            _LOGGER.debug("Connecting to WebSocket: %s", ws_url)
            async with session.ws_connect(ws_url, headers=headers) as ws:
                # Start metadata message
                await ws.send_json({
                    "type": "start",
                    "sampleRate": metadata.sample_rate.value,
                    "channels": metadata.channel.value,
                    "language": metadata.language
                })
                
                # Stream audio chunks in real-time
                chunk_count = 0
                total_bytes = 0
                
                async for chunk in stream:
                    if chunk:
                        await ws.send_bytes(chunk)
                        chunk_count += 1
                        total_bytes += len(chunk)
                        _LOGGER.debug("Sent chunk %d (%d bytes)", chunk_count, len(chunk))
                
                # End stream
                await ws.send_json({"type": "end"})
                _LOGGER.info("Sent %d chunks (%d bytes total)", chunk_count, total_bytes)
                
                # Wait for final result
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = msg.json()
                        _LOGGER.debug("Received WebSocket message: %s", data)
                        
                        msg_type = data.get("type")
                        if msg_type == "partial":
                            # Log partial results but don't return yet
                            _LOGGER.debug("Partial: %s", data.get("text", ""))
                        elif msg_type == "final":
                            text = data.get("text", "")
                            _LOGGER.info("Final STT result: '%s'", text)
                            return stt.SpeechResult(text, stt.SpeechResultState.SUCCESS)
                        elif msg_type == "error":
                            error = data.get("error", "Unknown error")
                            _LOGGER.error("STT error: %s", error)
                            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        _LOGGER.error("WebSocket error: %s", ws.exception())
                        return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        _LOGGER.warning("WebSocket closed unexpectedly")
                        break
                
                # If we reach here without a final result, it's an error
                _LOGGER.error("WebSocket closed without final result")
                return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
                
        except aiohttp.ClientError as e:
            _LOGGER.error("WebSocket connection error: %s", e)
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
        except Exception as e:
            _LOGGER.error("Unexpected STT error: %s", e, exc_info=True)
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
