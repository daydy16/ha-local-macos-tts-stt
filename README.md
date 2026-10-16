# Home Assistant STT/TTS Bridge Integration 🏠🎤

> [!WARNING]
> **Deprecated, no longer maintained.**
> This was a personal experiment and is no longer in use.
> Native alternatives now exist for local Apple speech in
> Home Assistant, for example
> [wyoming-apple-speech](https://github.com/FI-153/wyoming-apple-speech)
> (Wyoming STT/TTS server for macOS) or the voice tools server
> of the Home Assistant Companion App for macOS.
> This repository is archived and read-only.

> ⚠️ **Experimental & AI-Generated** - This integration was developed with AI assistance and is in active development. Expect bugs and breaking changes!

Home Assistant Custom Integration for connecting to the [macOS STT/TTS Bridge Server](https://github.com/daydy16/macos-stt-tts-bridge).

Use Apple's high-quality, **100% local** Speech Recognition and Text-to-Speech directly in Home Assistant - no cloud, maximum privacy!

## ✨ Features

- 🎯 **Native macOS Speech Recognition** - High-precision voice recognition
- 🗣️ **Premium TTS Voices** - Natural-sounding Apple voices
- ⚡ **WebSocket Streaming** - Real-time STT with minimal latency
- 🔒 **100% Local** - All data stays on your Mac
- 🌍 **Multi-Language** - German, English, and many more
- 🎨 **Voice Assist Integration** - Seamless integration with HA Assist Pipeline

## 📋 Prerequisites

1. **macOS Device** with macOS 13.0+
2. **STT/TTS Bridge Server** running on the Mac
   - Download: [macos-stt-tts-bridge Releases](https://github.com/daydy16/macos-stt-tts-bridge/releases)
   - Or build from source
3. **Home Assistant** 2024.1.0+ 
4. (Optional) **HACS** for easy installation

## 🚀 Installation

### Method 1: HACS (Recommended)

1. **Open HACS** in Home Assistant
2. Click the **three dots** in the top right
3. Select **Custom repositories**
4. Add:
   - **Repository:** `https://github.com/daydy16/ha-local-macos-tts-stt`
   - **Category:** `Integration`
5. Click **Add**
6. Search for **"STT/TTS Bridge"**
7. Click **Download**
8. **Restart Home Assistant**

### Method 2: Manual

```bash
cd /config  # Your HA config directory
mkdir -p custom_components
cd custom_components
git clone https://github.com/daydy16/ha-local-macos-tts-stt.git sttbridge
```

Then restart Home Assistant.

## ⚙️ Configuration

### 1. Prepare Server

Make sure the macOS STT/TTS Bridge Server is running:

```bash
# Check if server is reachable
curl http://localhost:8787/voices

# Should return JSON with available voices
```

### 2. Add Integration

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **"STT/TTS Bridge"**
4. Enter:
   - **Host:** IP of your Mac (e.g., `192.168.1.100` or `localhost` if on same device)
   - **Port:** `8787` (default)
   - **(Optional) Token:** If you enabled auth on the server

### 3. Use in Assist Pipeline

#### For Voice Assistants:

1. **Settings → Voice Assistants → Assist**
2. Create new pipeline or edit existing:
   - **Speech-to-Text:** `STT/TTS Bridge STT`
   - **Text-to-Speech:** `STT/TTS Bridge TTS`
   - **Language:** `en-US` (or your language)
3. **Save**

#### Test:

Talk to your Voice Assistant:
- "Hey Assistant, what's the weather?"
- The response should come with Apple voice! 🎉

## 🎯 Usage

### In Automations (TTS)

```yaml
service: tts.speak
target:
  entity_id: tts.stt_tts_bridge
data:
  message: "The front door is open!"
  language: en-US
  media_player_entity_id: media_player.living_room
```

### STT Event Listener

```yaml
automation:
  - alias: "Voice Command Test"
    trigger:
      - platform: event
        event_type: stt_end
        event_data:
          text: "lights on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
```

## 🐛 Troubleshooting

### Server Not Reachable

```bash
# Check if server is running
ps aux | grep STTBridge

# Check network
curl http://<mac-ip>:8787/voices

# Check logs (if running as service)
tail -f /tmp/sttbridge.log
```

### STT Not Working

1. **Microphone Permission:** Ensure STTBridge.app has microphone access
2. **Audio Format:** Integration sends 16kHz, 16-bit, mono WAV
3. **Logs:** Check HA Logs: `Settings → System → Logs`

### TTS No Output

1. **Voice Available?** Check `/voices` endpoint
2. **Language Correct?** e.g., `en-US` not just `en`
3. **Audio Player:** Test with `curl` if server returns WAV

### Performance

If STT is slow:
- ✅ WebSocket Streaming is already used (v0.1.8+)
- ✅ In-Memory Processing (no temp files)
- ✅ Cached Recognizers

Expected times:
- **UI (direct):** ~0.06s
- **HA (via Integration):** ~0.5-1.5s (depends on audio length)

## 📊 Performance Optimizations (v0.1.8+)

This version uses:
- ✅ **WebSocket Streaming** instead of HTTP POST - Chunks processed immediately
- ✅ **In-Memory Audio Processing** - no disk I/O
- ✅ **Cached Speech Recognizers** - eliminates initialization overhead
- ✅ **Optimized Headers** - X-Sample-Rate & X-Channel-Count for direct processing

## 🤝 Contributing

Pull Requests are welcome! For major changes, please open an issue first.

## 📝 License

MIT License

## ⚠️ Disclaimer

**Experimental AI-Generated Project!**

This integration was developed with AI assistance (GitHub Copilot) and is a proof-of-concept.
It is provided "as-is" without warranties. Use at your own risk!

### Known Limitations

- ⚠️ Streaming works well, but not as fast as direct UI usage
- ⚠️ No batch processing
- ⚠️ Minimal error recovery
- ⚠️ No unit tests (yet)

## 🔗 Links

- **Backend Server:** [macos-stt-tts-bridge](https://github.com/daydy16/macos-stt-tts-bridge)
- **Home Assistant:** [home-assistant.io](https://www.home-assistant.io/)
- **Apple Speech Framework:** [developer.apple.com](https://developer.apple.com/documentation/speech)

---

**Found this helpful? Give it a star! ⭐**
