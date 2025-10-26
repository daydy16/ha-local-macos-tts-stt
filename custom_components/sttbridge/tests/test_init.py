"""Test the STT Bridge integration."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.sttbridge.const import DOMAIN


async def test_setup_unload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test setting up and unloading the integration."""
    mock_config_entry.add_to_hass(hass)

    # Setup the integration
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    # Check that platforms were set up
    assert "stt" in hass.config.components
    assert "tts" in hass.config.components

    # Unload the integration
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]
