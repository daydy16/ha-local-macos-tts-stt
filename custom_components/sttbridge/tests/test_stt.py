"""Test the STT Bridge STT platform."""
from unittest.mock import AsyncMock

import pytest
from homeassistant.components import stt
from homeassistant.core import HomeAssistant

from custom_components.sttbridge.const import DOMAIN

from .conftest import mock_config_entry

MOCK_CONFIG = {
    "host": "1.2.3.4",
    "port": 8787,
    "token": "test-token",
}

async def test_process_audio_stream(hass: HomeAssistant, aioclient_mock) -> None:
    """Test processing an audio stream."""
    entry = mock_config_entry()
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    aioclient_mock.post(
        f"http://{MOCK_CONFIG['host']}:{MOCK_CONFIG['port']}/stt",
        json={"text": "This is a test"},
    )

    provider = stt.get_provider(hass, DOMAIN)
    assert provider is not None

    async def mock_audio_stream():
        yield b"fake_audio_chunk_1"
        yield b"fake_audio_chunk_2"

    result = await provider.async_process_audio_stream(
        stt.SpeechMetadata(
            language="en-US",
            format=stt.AudioFormats.WAV,
            codec=stt.AudioCodecs.PCM,
            bit_rate=stt.AudioBitRates.BIT_16,
            sample_rate=stt.AudioSampleRates.KHZ_16,
            channel=stt.AudioChannels.MONO,
        ),
        mock_audio_stream(),
    )

    assert result.result == stt.SpeechResultState.SUCCESS
    assert result.text == "This is a test"
