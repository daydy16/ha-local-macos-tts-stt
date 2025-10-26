# Home Assistant STTBridge Integration Plan

## Ziel

Ein HACS-kompatibles Custom Integration Plugin (`sttbridge`) für Home Assistant, das **lokales Speech-to-Text (STT)** und **Text-to-Speech (TTS)** über deinen bestehenden macOS-Endpunkt (`http://127.0.0.1:8787`) ermöglicht.

Ziel ist es, kein Add-on oder Wyoming-Daemon zu nutzen, sondern direkt via HTTP/WS an deinen lokalen Server zu kommunizieren.

---

## Architekturüberblick

**Home Assistant (Core)** ↔️ **Custom Integration (`sttbridge`)** ↔️ **macOS SwiftNIO-Server**

### Pfade
- **TTS:** `POST /tts` → liefert `audio/wav`
- **STT:** `POST /stt` oder `WS /stt/stream` → liefert Text
- **Voices:** `GET /voices`
- **Healthcheck:** `GET /healthz`

Optional: Authentifizierung per `Authorization: Bearer <TOKEN>`.

---

## Funktionsweise

### Text-to-Speech (TTS)
- Home Assistant sendet Text an `/tts`.
- Integration erhält WAV-Audio und gibt es an Home Assistant zurück.
- Optional: Auswahl von Stimme, Rate, Pitch.

### Speech-to-Text (STT)
- Mikrofoneingabe in Home Assistant wird an `/stt` gesendet.
- Integration empfängt JSON mit Text und liefert ihn an Assist zurück.

---

## Projektstruktur

```
custom_components/sttbridge/
├── __init__.py
├── manifest.json
├── hacs.json
├── const.py
├── config_flow.py
├── tts.py
├── stt.py
├── diagnostics.py
└── translations/de.json
```

---

## Implementierungsschritte

### 1. Grundstruktur
- `manifest.json` mit Domain `sttbridge` erstellen.
- HACS-Metadatei `hacs.json` hinzufügen.
- `__init__.py` minimal mit Setup-Funktion.

### 2. TTS-Provider
Implementiert `async_get_tts_audio`:
```python
async def async_get_tts_audio(self, message, language, options):
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}
    async with session.post(f"{self._base}/tts", json=payload, headers=headers) as resp:
        data = await resp.read()
        return ("wav", data)
```

### 3. STT-Provider
Implementiert `async_process_audio_stream`:
```python
async def async_process_audio_stream(self, metadata, stream):
    headers = {"Content-Type": "audio/l16", "X-Sample-Rate": "16000", "X-Channel-Count": "1"}
    async with session.post(f"{self._base}/stt", data=stream, headers=headers) as resp:
        result = await resp.json()
        return stt.SpeechResult(result["text"], stt.SpeechResultState.SUCCESS)
```

### 4. Config Flow
- Host, Port, Sprache, Stimme, Token konfigurierbar.
- Prüft Erreichbarkeit per `GET /healthz`.

### 5. Tests
- `tts.speak` → Media Player spielt WAV.
- `assist` → erkennt Sprache korrekt.

---

## Beispielkonfiguration

```yaml
tts:
  - platform: sttbridge
    base_url: "http://127.0.0.1:8787"
    voice: "Anna"
stt:
  - platform: sttbridge
    base_url: "http://127.0.0.1:8787"
```

---

## Referenzen / Beispiele

- [HA ElevenLabs Custom TTS](https://github.com/loryanstrant/HA-ElevenLabs-Custom-TTS)
- [Wyoming Microsoft STT](https://github.com/hugobloem/wyoming-microsoft-stt)
- [Home Assistant TTS Docs](https://www.home-assistant.io/integrations/tts/)
- [Home Assistant STT Docs](https://www.home-assistant.io/integrations/stt/)

---

## Erweiterungen (optional)
- WebSocket-STT mit Partials.
- Voice-List Caching (`/voices`).
- Health Diagnostics in UI.
- Streaming-TTS (HA 2025+ Feature).

---

## Ziel: MVP in 2 Phasen

1. **Phase 1:** TTS-Funktionalität (Text → WAV)
2. **Phase 2:** STT (Audio → Text) mit Assist-Anbindung

Nach erfolgreichem Test kann HACS-Unterstützung hinzugefügt werden, um einfache Installation zu ermöglichen.
