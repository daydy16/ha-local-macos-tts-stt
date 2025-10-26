"""Test the STT Bridge TTS platform."""
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.sttbridge.const import DOMAIN

from .conftest import mock_config_entry  # Import the fixture

MOCK_CONFIG = {
    "host": "1.2.3.4",
    "port": 8787,
    "token": "test-token",
}

async def test_get_tts_audio(hass: HomeAssistant, aioclient_mock) -> None:
    """Test getting TTS audio."""
    entry = mock_config_entry()
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    aioclient_mock.post(
        f"http://{MOCK_CONFIG['host']}:{MOCK_CONFIG['port']}/tts",
        content=b"fake_wav_data",
        headers={"Content-Type": "audio/wav"},
    )

    response = await hass.services.async_call(
        "tts",
        "speak",
        {
            "entity_id": "tts.stt_bridge",
            "message": "Hello",
            "language": "en-US",
        },
        blocking=True,
        return_response=True,
    )
    
    assert response
