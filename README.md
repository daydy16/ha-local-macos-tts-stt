# Home Assistant Local macOS TTS/STT Bridge

A custom component for Home Assistant that acts as a bridge to a local server on macOS for Text-to-Speech (TTS) and Speech-to-Text (STT).

## Overview

This integration allows you to use the native speech capabilities of macOS (like Siri voices and dictation) directly in Home Assistant, without relying on cloud services. Communication happens locally between Home Assistant and a separate server running on your Mac.

**Important Note:** This repository only contains the Home Assistant integration (`sttbridge`). You need a compatible server running on your macOS device. A reference implementation for the server can be found in a separate project.

## Features

-   **Text-to-Speech (TTS):** Convert text into spoken language using the voices installed on your Mac.
-   **Speech-to-Text (STT):** Convert spoken language from the Home Assistant Assist microphone into text.
-   **Local & Private:** All data remains within your local network. No data is sent to external cloud services.
-   **Simple Configuration:** Set up via the Home Assistant UI.

## Prerequisites

-   Home Assistant (Version 2023.5 or newer).
-   A macOS device running the companion server.
-   Network access from Home Assistant to the macOS device.

## Installation

### Method 1: HACS (Recommended)

1.  Ensure you have [HACS](https://hacs.xyz/) installed.
2.  Go to HACS > Integrations.
3.  Add this repository as a "Custom repository":
    -   URL: `https://github.com/david-ha-local-macos-tts-stt`
    -   Category: `Integration`
4.  Search for "STT Bridge" and install the integration.
5.  Restart Home Assistant.

### Method 2: Manual Installation

1.  Download the latest version from the [Releases Tab](https://github.com/david-ha-local-macos-tts-stt/releases).
2.  Unzip the downloaded file.
3.  Copy the `custom_components/sttbridge` folder into your Home Assistant `config` directory.
4.  Restart Home Assistant.

## Configuration

After installation, you need to configure the integration.

1.  Go to **Settings > Devices & Services**.
2.  Click **Add Integration**.
3.  Search for "STT Bridge" and select it.
4.  Enter the following information:
    -   **Host:** The IP address of your Mac (e.g., `192.168.1.10`).
    -   **Port:** The port the server is running on (Default: `8787`).
    -   **Token (optional):** If your server requires authentication, enter the bearer token here.
5.  Click "Submit". The integration will verify the connection to the server.

## Usage

### Text-to-Speech (TTS)

The integration creates a `tts.stt_bridge` service. You can use it in your automations or scripts.

**Example: Service Call**

```yaml
service: tts.speak
target:
  entity_id: media_player.your_speaker
data:
  message: "Hello world! This is a test."
  cache: false
  language: "en-US"
  options:
    voice: "Alex" # Optional: select a voice
```

### Speech-to-Text (STT)

You can set "STT Bridge" as the default STT processor for Assist.

1.  Open the Home Assistant Companion App or a Lovelace view with the Assist microphone.
2.  Press and hold the microphone icon to open the settings.
3.  Under "Speech-to-text", select the "STT Bridge" option.

## Server API Requirements

Your macOS server must provide the following endpoints:

-   `GET /healthz`: A simple endpoint that returns a `200 OK` status code if the server is ready.
-   `POST /tts`:
    -   Accepts a JSON payload: `{"text": "...", "language": "...", "voice": "..."}`.
    -   Returns an `audio/wav` file in the response body.
-   `POST /stt`:
    -   Accepts `audio/wav` data in the request body.
    -   Returns a JSON response: `{"text": "recognized text"}`.
-   `GET /voices` (Optional):
    -   Gives a JSON list of available voices.

## Testing

To run the tests for this custom component, you will need a Python environment with `pytest` and `pytest-homeassistant-custom-component` installed.

### Prerequisites

1.  **Python 3.9+**: Ensure you have a compatible Python version.
2.  **Install `pytest` and `pytest-homeassistant-custom-component`**:

    ```bash
    pip install pytest pytest-homeassistant-custom-component
    ```

### Running Tests

Navigate to the root directory of this repository and execute `pytest`:

```bash
pytest
```

This will discover and run all tests within the `custom_components/sttbridge/tests/` directory.

## License

This project is licensed under the Apache 2.0 License.