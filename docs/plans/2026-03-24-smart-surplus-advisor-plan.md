# Smart Surplus Advisor — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Notify the user when solar surplus is high (>4kW), battery full (≥95%), and 2+ hours of sun remain — proposing sauna, Tesla, or appliance use.

**Architecture:** Standalone automation in HA, separate from existing Abundance system. Template sensor for forecast hours. Python script for dynamic Gemini TTS. Mobile notification with actionable buttons + Sonos announcement.

**Tech Stack:** Home Assistant YAML (automations, template sensors, input_boolean), Python 3.12 + google-genai (Gemini TTS), HA REST API

---

### Task 1: Add `input_boolean.smart_surplus_notified` and `sensor.solar_forecast_hours_remaining`

**Files:**
- Modify: `homeassistant/configuration.yaml` (input_boolean section ~line 40, template section ~line 111)

**Step 1: Add input_boolean for cooldown**

In `configuration.yaml`, add under `input_boolean:` (after `abundance_lavatrice_enabled`):

```yaml
  smart_surplus_notified:
    name: "Smart Surplus: Notificato"
    initial: off
    icon: mdi:bell-check
```

**Step 2: Add template sensor for forecast hours remaining**

In `configuration.yaml`, add a new template sensor block after the Abundance section (~line 167):

```yaml
  # --- Smart Surplus Advisor ---
  - sensor:
      - name: "Solar Forecast Hours Remaining"
        unique_id: solar_forecast_hours_remaining
        state: >
          {% set now_ts = now().timestamp() %}
          {% set sunset_ts = as_timestamp(state_attr('sun.sun', 'next_setting')) %}
          {% if sun_is_up() %}
            {{ ((sunset_ts - now_ts) / 3600) | round(1) }}
          {% else %}
            0
          {% endif %}
        unit_of_measurement: "h"
        icon: mdi:weather-sunset-down
```

**Step 3: Push both changes to HA via API**

The config file is on HA server (submodule). After editing locally, we must reload via API:

```bash
source .env
# Reload input_boolean
curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/input_boolean/reload" -d '{}'
# For template sensors, need full HA config check + reload
curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/homeassistant/reload_all" -d '{}'
```

NOTE: Since configuration.yaml is on the HA server (submodule), the actual config lives at `/config/configuration.yaml` on HA. We edit locally, commit to submodule, then the user syncs. Alternatively, create the input_boolean via websocket API.

**Step 4: Verify entities exist**

```bash
source .env
curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/input_boolean.smart_surplus_notified"
curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/sensor.solar_forecast_hours_remaining"
```

**Step 5: Commit**

```bash
cd homeassistant && git add configuration.yaml && git commit -m "feat: add smart surplus advisor helpers (input_boolean + forecast sensor)"
```

---

### Task 2: Create dynamic TTS script `scripts/generate_surplus_announcement.py`

**Files:**
- Create: `scripts/generate_surplus_announcement.py`

**Step 1: Write the script**

The script takes surplus_kw, hours_remaining, and a comma-separated list of suggested loads as CLI args. It generates a British train station announcement via Gemini TTS, saves as mp3, and uploads to HA media library.

```python
#!/usr/bin/env python3.12
"""
Generate dynamic Smart Surplus Advisor announcement via Gemini TTS.
Usage: python3.12 scripts/generate_surplus_announcement.py <surplus_kw> <hours_remaining> <suggestions>
Example: python3.12 scripts/generate_surplus_announcement.py 5.2 3.1 "sauna,washing machine,dishwasher"
"""

import os
import sys
import wave
import subprocess
import urllib.request
import json
from pathlib import Path


def load_env():
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

from google import genai
from google.genai import types


def save_wav(filename: str, pcm_data: bytes, rate: int = 24000):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def wav_to_mp3(wav_path: str, mp3_path: str):
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-b:a", "192k", mp3_path],
        capture_output=True, check=True,
    )
    os.remove(wav_path)


def upload_to_ha(mp3_path: str, filename: str):
    ha_url = os.environ.get("HA_URL", "http://homeassistant.local:8123")
    ha_token = os.environ.get("HA_TOKEN", "")
    url = f"{ha_url}/api/media_source/local_source/upload"

    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    file_data = Path(mp3_path).read_bytes()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="media_content_id"\r\n\r\n'
        f"media-source://media_source/local/.\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: audio/mpeg\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {ha_token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    urllib.request.urlopen(req)


def build_announcement_text(surplus_kw: float, hours_remaining: float, suggestions: list[str]) -> str:
    surplus_str = f"{surplus_kw:.1f}" if surplus_kw % 1 else f"{int(surplus_kw)}"
    hours_str = f"{hours_remaining:.0f}"

    suggestion_text = ""
    if len(suggestions) == 1:
        suggestion_text = f"run your {suggestions[0]}"
    elif len(suggestions) == 2:
        suggestion_text = f"run your {suggestions[0]} or {suggestions[1]}"
    else:
        suggestion_text = f"run your {', '.join(suggestions[:-1])}, or {suggestions[-1]}"

    return (
        "Say this as a calm, professional British train station announcement, "
        "with measured pacing and a warm, cheerful tone. Add a brief pause after 'Good afternoon': "
        f"Good afternoon, ladies and gentlemen. "
        f"We are pleased to announce an abundance of solar energy. "
        f"{surplus_str} kilowatts of surplus power available, "
        f"battery fully charged, "
        f"with approximately {hours_str} hours of sunshine remaining. "
        f"This would be an excellent time to {suggestion_text}. "
        f"Thank you for choosing solar energy."
    )


def main():
    if len(sys.argv) < 4:
        print("Usage: generate_surplus_announcement.py <surplus_kw> <hours_remaining> <suggestions>")
        print('Example: generate_surplus_announcement.py 5.2 3.1 "sauna,washing machine,dishwasher"')
        sys.exit(1)

    surplus_kw = float(sys.argv[1])
    hours_remaining = float(sys.argv[2])
    suggestions = [s.strip() for s in sys.argv[3].split(",")]

    text = build_announcement_text(surplus_kw, hours_remaining, suggestions)

    output_dir = Path(__file__).parent.parent / "audio"
    output_dir.mkdir(exist_ok=True)
    mp3_path = str(output_dir / "smart_surplus_announcement.mp3")

    generate_announcement(text, mp3_path)
    upload_to_ha(mp3_path, "smart_surplus_announcement.mp3")
    print("Done: generated and uploaded to HA media library")


def generate_announcement(text: str, output: str, voice: str = "Kore"):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice,
                    )
                )
            ),
        ),
    )

    pcm_data = response.candidates[0].content.parts[0].inline_data.data
    wav_path = output.replace(".mp3", ".wav")
    save_wav(wav_path, pcm_data)
    wav_to_mp3(wav_path, output)


if __name__ == "__main__":
    main()
```

**Step 2: Test the script locally**

```bash
/usr/local/bin/python3.12 scripts/generate_surplus_announcement.py 5.2 3.0 "washing machine,dishwasher"
```

Expected: generates `audio/smart_surplus_announcement.mp3` and uploads to HA.

**Step 3: Commit**

```bash
git add scripts/generate_surplus_announcement.py && git commit -m "feat: add dynamic surplus TTS announcement script"
```

---

### Task 3: Add shell_command in HA configuration

**Files:**
- Modify: `homeassistant/configuration.yaml`

**Step 1: Add shell_command**

Add at root level of `configuration.yaml` (check if `shell_command:` section exists, if not create it):

```yaml
shell_command:
  generate_surplus_announcement: '/usr/local/bin/python3.12 /config/scripts/deye_cloud_sensor.py'
```

Wait — the scripts directory is NOT in /config/ on HA. The TTS script lives in the parent repo. We need a different approach: the script runs on the HA server. Since `scripts/` is not part of the submodule, we'll use a shell_command that calls python3.12 with the script path relative to HA config.

Alternative approach: copy the script into `homeassistant/scripts/` (which IS in the submodule and available on HA as `/config/scripts/`).

**Revised Step 1: Copy script to submodule**

Create `homeassistant/scripts/generate_surplus_announcement.py` (same content as Task 2, but adjusted paths for running inside HA at `/config/scripts/`).

**Step 2: Add shell_command to configuration.yaml**

```yaml
shell_command:
  generate_surplus_announcement: '/usr/local/bin/python3.12 /config/scripts/generate_surplus_announcement.py {{ surplus_kw }} {{ hours_remaining }} "{{ suggestions }}"'
```

If `shell_command:` already exists, add this entry to it.

**Step 3: Commit**

```bash
cd homeassistant && git add scripts/generate_surplus_announcement.py configuration.yaml && git commit -m "feat: add surplus TTS shell_command for HA"
```

---

### Task 4: Create automation `smart_surplus_advisor`

**Files:**
- Modify: `homeassistant/automations.yaml`

**Step 1: Write the automation**

Append to `automations.yaml`:

```yaml
- id: smart_surplus_advisor
  alias: Smart Surplus Advisor
  description: >
    Notifica quando c'è surplus solare >4kW, batteria ≥95%, e almeno 2h di sole.
    Propone sauna, Tesla, o elettrodomestici.
  trigger:
    - platform: numeric_state
      entity_id: sensor.abundance_surplus_kw
      above: 4.0
      for:
        minutes: 5
  condition:
    - condition: numeric_state
      entity_id: sensor.deye_battery_soc
      above: 94
    - condition: numeric_state
      entity_id: sensor.solar_forecast_hours_remaining
      above: 1.9
    - condition: time
      after: "09:00:00"
      before: "18:00:00"
    - condition: state
      entity_id: input_boolean.smart_surplus_notified
      state: "off"
  action:
    # Build suggestions list
    - variables:
        surplus: "{{ states('sensor.abundance_surplus_kw') | float(0) }}"
        hours_left: "{{ states('sensor.solar_forecast_hours_remaining') | float(0) }}"
        is_sauna_time: "{{ now().hour >= 14 and now().hour < 22 }}"
        tesla_needs_charge: >
          {{ states('sensor.biancaneve_battery') | float(100) < 80
             or states('sensor.little_rascal_battery') | float(100) < 80 }}
        tesla_home: >
          {{ states('device_tracker.biancaneve_location_tracker') == 'home'
             or states('device_tracker.little_rascal_location_tracker') == 'home' }}
        suggest_tesla: "{{ tesla_needs_charge and tesla_home }}"
        suggest_sauna: "{{ is_sauna_time }}"
        # Build suggestions string for TTS
        tts_suggestions: >
          {% set items = [] %}
          {% if suggest_sauna %}{% set items = items + ['sauna'] %}{% endif %}
          {% if suggest_tesla %}{% set items = items + ['Tesla charger'] %}{% endif %}
          {% set items = items + ['washing machine', 'dishwasher', 'tumble dryer'] %}
          {{ items | join(',') }}
        # Build mobile notification message
        mobile_message: >
          ☀️ Surplus {{ surplus }} kW, batteria piena, ancora {{ hours_left | round(0) | int }}h di sole.
          {% if suggest_sauna %}🔥 Sauna disponibile. {% endif %}
          {% if suggest_tesla %}🚗 Tesla da caricare. {% endif %}
          Buon momento per lavatrice, lavastoviglie o asciugatrice.
    # Mobile notification with dynamic buttons
    - service: notify.mobile_app_clancy
      data:
        title: "☀️ Smart Surplus Advisor"
        message: "{{ mobile_message }}"
        data:
          actions: >
            {% set buttons = [] %}
            {% if suggest_sauna %}
              {% set buttons = buttons + [{"action": "SMART_SURPLUS_SAUNA", "title": "🔥 Accendi Sauna"}] %}
            {% endif %}
            {% if suggest_tesla %}
              {% set buttons = buttons + [{"action": "SMART_SURPLUS_TESLA", "title": "🚗 Collega Tesla"}] %}
            {% endif %}
            {% set buttons = buttons + [{"action": "SMART_SURPLUS_OK", "title": "OK, grazie"}] %}
            {{ buttons }}
    # Sonos announcement: ding + TTS
    - service: media_player.play_media
      target:
        entity_id: media_player.family_room
      data:
        media_content_id: "media-source://media_source/local/Ding Sound 123107.mp3"
        media_content_type: audio/mpeg
        announce: true
    - delay:
        seconds: 3
    # Generate and play dynamic TTS
    - service: shell_command.generate_surplus_announcement
      data:
        surplus_kw: "{{ surplus }}"
        hours_remaining: "{{ hours_left }}"
        suggestions: "{{ tts_suggestions }}"
    - delay:
        seconds: 10
    - service: media_player.play_media
      target:
        entity_id: media_player.family_room
      data:
        media_content_id: "media-source://media_source/local/smart_surplus_announcement.mp3"
        media_content_type: audio/mpeg
        announce: true
    # Set cooldown
    - service: input_boolean.turn_on
      target:
        entity_id: input_boolean.smart_surplus_notified
  mode: single

# Handle Sauna button press
- id: smart_surplus_sauna_action
  alias: Smart Surplus - Accendi Sauna
  trigger:
    - platform: event
      event_type: mobile_app_notification_action
      event_data:
        action: SMART_SURPLUS_SAUNA
  action:
    - service: switch.turn_on
      target:
        entity_id: switch.sauna_switch_switch

# Reset cooldown at midnight or when surplus drops
- id: smart_surplus_reset_cooldown
  alias: Smart Surplus - Reset Cooldown
  trigger:
    - platform: time
      at: "00:00:00"
    - platform: numeric_state
      entity_id: sensor.abundance_surplus_kw
      below: 2.0
      for:
        minutes: 10
  action:
    - service: input_boolean.turn_off
      target:
        entity_id: input_boolean.smart_surplus_notified
```

**Step 2: Push automation to HA via API**

Since automations.yaml is on HA server, push each automation via REST API:

```bash
source .env
# Push smart_surplus_advisor
curl -X POST -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" \
  "$HA_URL/api/config/automation/config/smart_surplus_advisor" -d '<json>'
# Push smart_surplus_sauna_action
curl -X POST -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" \
  "$HA_URL/api/config/automation/config/smart_surplus_sauna_action" -d '<json>'
# Push smart_surplus_reset_cooldown
curl -X POST -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" \
  "$HA_URL/api/config/automation/config/smart_surplus_reset_cooldown" -d '<json>'
```

**Step 3: Reload automations**

```bash
curl -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/automation/reload" -d '{}'
```

**Step 4: Verify all entities exist**

```bash
curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/automation.smart_surplus_advisor"
curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/automation.smart_surplus_sauna_action"
curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/automation.smart_surplus_reset_cooldown"
```

**Step 5: Commit locally**

```bash
cd homeassistant && git add automations.yaml && git commit -m "feat: add Smart Surplus Advisor automation with Sonos + mobile notifications"
```

---

### Task 5: End-to-end test

**Step 1: Manually trigger the automation**

```bash
source .env
curl -X POST -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" \
  "$HA_URL/api/services/automation/trigger" \
  -d '{"entity_id": "automation.smart_surplus_advisor"}'
```

**Step 2: Verify**

- Check mobile phone for notification with buttons
- Check Sonos plays ding + announcement
- Check `input_boolean.smart_surplus_notified` is on

**Step 3: Test cooldown reset**

```bash
curl -X POST -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" \
  "$HA_URL/api/services/automation/trigger" \
  -d '{"entity_id": "automation.smart_surplus_reset_cooldown"}'
# Verify notified is off
curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/input_boolean.smart_surplus_notified"
```

**Step 4: Test sauna button action**

Tap "Accendi Sauna" on mobile notification, verify `switch.sauna_switch_switch` turns on.

**Step 5: Final commit (submodule update in parent)**

```bash
cd .. && git add homeassistant && git commit -m "feat: Smart Surplus Advisor - solar surplus notification system"
```
