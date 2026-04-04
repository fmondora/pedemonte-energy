# Agent House — Design Document

Data: 2026-04-04
Branch: `agent-house`

## Visione

Sostituire Home Assistant con un sistema di agenti AI autonomi che parlano direttamente con i device della casa, ragionano sullo stato, agiscono, e si espongono via internet attraverso un'interfaccia adattiva. Nessun intermediario — ogni agente conosce i suoi device e comunica con gli altri via MQTT.

---

## Architettura

```
                         Internet
                            │
                    ┌───────▼────────┐
                    │  Cloudflare    │
                    │  Tunnel +      │
                    │  Workers +     │
                    │  Access        │
                    └───────┬────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                     Mini PC N100 16GB                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Mosquitto (MQTT)                      │ │
│  │              Bus di comunicazione tra agenti             │ │
│  └──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───┘ │
│     │      │      │      │      │      │      │      │      │
│  ┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐ │
│  │Shell││Deye ││Netat││Solar││Zigbe││Ring ││Tesla││Push │ │
│  │Agent││Agent││Agent││Edge ││Agent││Agent││Agent││Agent│ │
│  └─────┘└─────┘└─────┘│Agent│└─────┘└─────┘└─────┘└─────┘ │
│                        └─────┘                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Orchestratore (cervello)                  │  │
│  │                                                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │  │
│  │  │ Ollama   │  │ Claude   │  │  Frontend Server  │   │  │
│  │  │ (locale) │  │ API      │  │  (API JSON +      │   │  │
│  │  │ frequent │  │ (heavy)  │  │   WebSocket)      │   │  │
│  │  └──────────┘  └──────────┘  └───────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  InfluxDB    │  │  SQLite      │                         │
│  │  (time-series│  │  (config,    │                         │
│  │   storico)   │  │   utenti,    │                         │
│  └──────────────┘  │   ruoli)     │                         │
│                     └──────────────┘                         │
└──────────────────────────────────────────────────────────────┘
```

### Tre layer

1. **Device Agents** — ogni agente parla con una famiglia di device, pubblica stato su MQTT, esegue comandi ricevuti via MQTT
2. **Orchestratore** — consuma tutti i topic MQTT, ragiona (LLM ibrido locale+cloud), genera il feed UI, serve il frontend via JSON API + WebSocket
3. **Push Agents** — consumano decisioni dall'orchestratore e le traducono in notifiche (mobile, Sonos, Telegram)

### Due database

- **InfluxDB** — serie temporali: surplus, SOC, temperature, consumi. Query tipo "media surplus alle 14 negli ultimi 30 giorni"
- **SQLite** — configurazione: utenti, ruoli, permessi safe/critical, preferenze

---

## Device Agents

Ogni device agent è un processo Python indipendente che:
1. Scansiona i device a intervalli regolari (o ascolta eventi)
2. Pubblica lo stato su topic MQTT standardizzati
3. Ascolta comandi su topic MQTT dedicati
4. Scrive metriche in InfluxDB

### Shelly Agent

- **Protocollo**: HTTP REST locale (`/rpc/` per Gen2, `/settings/` per Gen1)
- **Device gestiti**:
  - Shelly Pro DM 2PM ×4 (192.168.86.24, .46, .73, .74) — dimmer con power metering
  - Shelly Plus 2PM ×2 (192.168.86.37, .42) — switch doppio con power metering
  - Shelly Plus 1PM (192.168.86.39) — switch singolo con power metering
  - Shelly 1PM Mini G3 (192.168.86.35) — switch compatto con power metering
  - ESP8266/Shelly Gen1 (192.168.86.55) — switch legacy
- **Scan**: ogni 10 secondi, polling HTTP su ogni device
- **Logica interna**:
  - Timer spegnimento luci scale (5 min per ogni luce)
  - Timer spegnimento luci accese da >1 ora
  - Cron spegnimento zanzare alle 6:00
- **Topic MQTT**:
  - `device/shelly/{device_id}/state` — stato (on/off, power, brightness, temperature)
  - `device/shelly/{device_id}/command` — comandi (turn_on, turn_off, set_brightness)
  - `device/shelly/{device_id}/energy` — metriche energetiche
- **InfluxDB**: power per ogni switch ogni 30 secondi

### Deye Agent

- **Protocollo**: Deye Cloud API REST (EU endpoint)
- **Script base**: `scripts/deye_cloud.py` (già funzionante)
- **Credenziali**: appId, appSecret, email, password in config
- **Polling**: ogni 5 minuti (rate limit API)
- **Dati**: SOC, battery_power, grid_power, pv_power, load_power (L1/L2/L3), grid_import/export, battery_charge/discharge, tensioni, temperature
- **Topic MQTT**:
  - `device/deye/battery/state` — {soc, power, voltage, charge_energy, discharge_energy}
  - `device/deye/grid/state` — {power, import_energy, export_energy, daily_import, daily_export}
  - `device/deye/load/state` — {power_total, power_l1, power_l2, power_l3}
  - `device/deye/pv/state` — {power}
- **InfluxDB**: tutti i datapoint ogni 5 minuti

### SolarEdge Agent

- **Protocollo**: SolarEdge Monitoring API REST
- **Credenziali**: API key + site ID
- **Polling**: ogni 15 secondi (produzione PV), ogni 15 minuti (EV charger)
- **Dati**: produzione corrente, energia giornaliera/lifetime, stato EV charger
- **Topic MQTT**:
  - `device/solaredge/inverter/state` — {current_power, daily_energy, lifetime_energy}
  - `device/solaredge/evcharger/state` — {status, power, session_energy}
- **InfluxDB**: produzione PV ogni 15 secondi

### Netatmo Agent

- **Protocollo**: Netatmo API OAuth2
- **Credenziali**: client_id, client_secret, refresh_token (da dev portal Netatmo)
- **Polling**: ogni 5 minuti
- **Stazioni**:
  - "Michele" — modulo esterno (temp, umidità, pressione, pioggia, vento)
  - "Via Pedemonte 425 berbenno" — modulo interno (temp, umidità, pressione, CO2)
- **Topic MQTT**:
  - `device/netatmo/{station}/state` — {temperature, humidity, pressure, co2, rain, wind_speed}
- **InfluxDB**: tutti i sensori ogni 5 minuti

### Zigbee Agent

- **Protocollo**: zigbee2mqtt (coordinator USB → MQTT)
- **Coordinator**: SONOFF ZBDongle-E o Conbee III
- **Device gestiti**: valvole termostatiche, sensori porta/finestra, sensori temperatura, button
- **Topic MQTT**: zigbee2mqtt pubblica direttamente su MQTT — l'agent traduce i topic in formato standard:
  - `device/zigbee/{device_id}/state` — dati sensore
  - `device/zigbee/{device_id}/command` — comandi attuatori
- **InfluxDB**: temperatura per stanza ogni 5 minuti

### Ring Agent

- **Protocollo**: Ring API non ufficiale (ring-client-api)
- **Device**: Ring Doorbell (front door)
- **Polling**: event-driven (webhook o polling eventi ogni 30 sec)
- **Logica interna**:
  - Motion detection → snapshot → analisi Gemini Vision (garage aperto?)
  - Cooldown 10 minuti tra detection
  - Solo 07:00-23:00
- **Topic MQTT**:
  - `device/ring/front_door/motion` — evento motion con timestamp
  - `device/ring/front_door/snapshot` — path immagine salvata
  - `device/ring/garage/state` — {open: true/false, confidence: 0.0-1.0}
- **InfluxDB**: eventi motion

### Tesla Agent

- **Protocollo**: Tesla Fleet API
- **Device**: Tesla "Biancaneve"
- **Polling**: ogni 15 minuti (per non svegliare l'auto inutilmente)
- **Logica interna**:
  - Regolazione ricarica solare: legge produzione da SolarEdge (via MQTT), calcola ampere (produzione / 690), applica soglie (avvio 4200W / stop 3500W)
- **Topic MQTT**:
  - `device/tesla/biancaneve/state` — {soc, charging_state, charge_amps, range_km, is_home}
  - `device/tesla/biancaneve/command` — {set_charge_amps, start_charging, stop_charging}
- **InfluxDB**: SOC e stato ricarica ogni 15 minuti

### Velux Agent

- **Protocollo**: pyvlx (libreria Python, comunicazione LAN con KLF 200)
- **Device**: finestre/tapparelle Velux
- **Topic MQTT**:
  - `device/velux/{window_id}/state` — {position: 0-100, rain_sensor}
  - `device/velux/{window_id}/command` — {set_position, open, close}

---

## Orchestratore

Il cervello del sistema. È un processo Python che:

### 1. Consuma stato da MQTT

Si iscrive a `device/#` e mantiene un **state store in memoria** con lo stato corrente di tutti i device. Ogni cambiamento di stato viene valutato.

### 2. Ragiona con LLM ibrido

**Ollama locale (Qwen3-30B-A3B)** — decisioni frequenti e leggere:
- Ogni 10 secondi: "lo stato è cambiato? devo aggiornare il feed?"
- Pattern matching rapido: surplus salito, luce accesa da troppo, temperatura anomala
- Latenza: <2 secondi

**Claude API (Haiku/Sonnet)** — ragionamento pesante e raro:
- Una volta al giorno (mattina): "strategia energetica per oggi" basata su forecast meteo, storico consumi, prezzi energia
- Su eventi significativi: "il garage è aperto da 2 ore, piove, e nessuno è in casa — che faccio?"
- Analisi anomalie: "consumo notturno 800W quando di solito sono 200W"

### 3. Genera il feed UI

L'orchestratore produce un **array JSON di componenti** ordinati per priorità. Il frontend li renderizza.

Tipi di componente:

```json
[
  {
    "type": "alert",
    "severity": "high",
    "title": "Garage aperto",
    "body": "Da 32 minuti. Piove.",
    "actions": [
      {"label": "Chiudi garage", "action": "garage_close", "level": "critical"}
    ],
    "icon": "garage-open",
    "timestamp": "2026-04-04T18:30:00Z"
  },
  {
    "type": "energy_card",
    "surplus_kw": 4.2,
    "soc": 98,
    "grid_power": -3100,
    "pv_power": 5200,
    "load_power": 2100,
    "suggestion": "Ottimo momento per la lavatrice",
    "actions": [
      {"label": "Accendi sauna", "action": "sauna_on", "level": "critical"}
    ]
  },
  {
    "type": "climate_card",
    "rooms": [
      {"name": "Soggiorno", "temp": 21.5, "humidity": 45, "target": 22},
      {"name": "Camera", "temp": 19.8, "humidity": 50, "target": 20}
    ]
  },
  {
    "type": "status",
    "severity": "ok",
    "title": "Casa tutto ok",
    "body": "Nessun problema rilevato",
    "icon": "home-check"
  },
  {
    "type": "insight",
    "title": "Oggi hai risparmiato €2.40",
    "body": "Autoconsumo al 87%. Ieri era 72%.",
    "chart_ref": "daily_savings"
  }
]
```

### 4. Gestisce azioni

Quando l'utente preme un bottone nel feed:

```
Frontend → WebSocket → Orchestratore
    │
    ├─ Verifica ruolo utente (SQLite)
    ├─ Verifica livello azione (safe/critical)
    │   ├─ safe → esegue subito via MQTT command
    │   └─ critical →
    │       ├─ utente admin (Francesco) → esegue subito
    │       └─ altri utenti → push conferma, aspetta risposta
    └─ Log azione in InfluxDB
```

### 5. Serve il frontend

- **HTTP server** (FastAPI o simile) per API JSON + file statici frontend
- **WebSocket** per aggiornamenti real-time del feed
- Endpoint:
  - `GET /api/feed` — feed corrente per l'utente autenticato
  - `WS /api/ws` — stream aggiornamenti feed
  - `POST /api/action` — esegui azione
  - `GET /api/history/{metric}` — dati storici da InfluxDB
  - `GET /api/config` — configurazione utente (ruolo, permessi)

---

## Push Agent

Processo Python che ascolta topic MQTT dall'orchestratore e traduce in notifiche.

### Canali

| Canale | Libreria/Protocollo | Uso |
|---|---|---|
| **ntfy** | HTTP POST a ntfy.sh (o self-hosted) | Push mobile iOS/Android, azioni |
| **Sonos** | SoCo (HTTP locale) | Annunci vocali (ding + TTS) |
| **Telegram** | Bot API | Messaggi testo + foto (snapshot Ring) |
| **Alexa** | Alexa Smart Home Skill (futuro) | Annunci multi-room |

### Topic MQTT consumati

- `orchestrator/push/notify` — {channel, user, title, body, actions, priority}
- `orchestrator/push/announce` — {speaker, text, audio_file}

### Gemini TTS

Lo script `generate_surplus_announcement.py` viene riutilizzato dal push-agent per generare annunci vocali dinamici. Il push-agent:
1. Riceve richiesta annuncio dall'orchestratore
2. Chiama Gemini TTS per generare mp3
3. Invia mp3 al Sonos via SoCo

---

## Utenti e Ruoli

### Tabella utenti (SQLite)

| Utente | Ruolo | Push channels | Critical senza conferma | Zone luci |
|---|---|---|---|---|
| Francesco | admin | ntfy (Clancy), Telegram | Sì, tutte | Tutte |
| Lucia | family | ntfy (iPhone Lucia) | No | Tutte |
| Anna | limited | — | No | Camera Anna, bagno, scale |
| Vicki | limited | — | No | Camera Vicki, bagno, scale |

### Autenticazione

- **Cloudflare Access** gestisce l'auth: email OTP o Google login
- L'email autenticata viene mappata al ruolo in SQLite
- Il WebSocket riceve il token Cloudflare e identifica l'utente
- Nessuna gestione password nel sistema

### Livelli azione

| Livello | Comportamento | Esempi |
|---|---|---|
| **safe** | Esecuzione immediata, nessuna notifica | Spegni luce, regola dimmer, cambia temperatura |
| **critical** | Admin: esegue subito. Altri: push conferma con timeout | Garage open/close, sauna on, azioni costose |

Timeout e default per azioni critical:
- Garage aperto da >2h senza risposta → chiude (default sicuro)
- Sauna senza risposta in 10 min → non accende (default sicuro)
- La classificazione safe/critical è configurabile per utente in SQLite

---

## Frontend

### Stack

- **React** (o Preact per leggerezza) + TypeScript
- **WebSocket** per aggiornamenti real-time
- **PWA** — installabile su iOS/Android come app
- Build statico servito da FastAPI o Cloudflare Workers

### Componenti UI (set fisso, ben progettati)

| Componente | Uso |
|---|---|
| `AlertCard` | Situazioni urgenti (garage aperto, anomalia consumo) |
| `EnergyCard` | Stato energetico: surplus, SOC, grid, PV, con gauge/grafici |
| `ClimateCard` | Temperature per stanza con target |
| `ActionButton` | Bottone contestuale (accendi sauna, chiudi garage) |
| `StatusBadge` | "Casa tutto ok" o indicatore stato |
| `InsightCard` | Consigli e statistiche dall'LLM |
| `ChartCard` | Grafici storici (produzione, consumi, SOC) |
| `DeviceCard` | Stato singolo device con controllo diretto |

L'orchestratore compone il feed come un array ordinato di questi componenti. Il frontend li renderizza in un layout verticale (mobile-first) o grid (desktop).

### Responsive

- **Mobile** (via Cloudflare, PWA): layout verticale, feed scrollabile
- **Desktop**: grid 2-3 colonne, feed + pannello laterale con dettagli
- **Atom Echo / terminali vocali**: nessun frontend visuale, solo push-agent

---

## Esposizione Internet

### Cloudflare Tunnel

- Il mini PC N100 esegue `cloudflared` che apre un tunnel persistente
- Nessuna porta aperta sul router, nessun port forwarding
- Dominio: `casa.pedemonte.it` (o simile)

### Cloudflare Access

- Policy per email: francesco@*, lucia@*, anna@*, vicki@*
- Auth via email OTP (zero password da gestire)
- Token JWT passato al backend per identificare l'utente

### Cloudflare Workers

- **Cache**: il feed JSON viene cachato per 5 secondi sull'edge (riduce latenza per utenti fuori casa)
- **Rate limiting**: protezione contro abusi
- **Asset serving**: file statici frontend serviti dall'edge Cloudflare (velocissimo)
- **Fallback page**: se il tunnel è down, mostra "casa offline" invece di un errore

---

## Migrazione da HA

### Fase 1 — Coesistenza (MVP)

HA resta attivo. Gli agent girano in parallelo e leggono gli stessi device. Il frontend Agent House è accessibile via Cloudflare. Si valida che gli agent leggano correttamente e che il feed sia utile.

### Fase 2 — Migrazione automazioni

Le automazioni vengono migrate una alla volta da HA agli agent. Ogni automazione migrata viene disattivata in HA. Si parte dalle più semplici (timer luci) e si arriva alle più complesse (surplus advisor).

### Fase 3 — Spegnimento HA

Quando tutte le automazioni sono migrate e validate, HA viene spento. Il coordinator Zigbee USB viene spostato dal Green al mini PC N100. Il Green viene ritirato.

### Device già pronti per la migrazione

| Device | Pronto? | Note |
|---|---|---|
| Shelly (tutti) | ✅ | API HTTP locale verificata, nessuna dipendenza HA |
| Deye | ✅ | Script Python già funzionante |
| SolarEdge | ⚠️ | Serve API key dal portale SolarEdge |
| Netatmo | ⚠️ | Servono credenziali OAuth2 dal dev portal |
| Ring | ⚠️ | API non ufficiale, da validare |
| Zigbee | ⚠️ | Serve coordinator USB + setup zigbee2mqtt |
| Tesla | ⚠️ | Serve setup Tesla Fleet API |
| Velux | ⚠️ | Da validare pyvlx standalone |
| Sonos | ✅ | SoCo funziona standalone |

---

## MQTT Topic Convention

```
device/{family}/{device_id}/state      # stato pubblicato dal device agent
device/{family}/{device_id}/command    # comandi ricevuti dal device agent
device/{family}/{device_id}/energy     # metriche energetiche

orchestrator/feed                      # feed JSON corrente
orchestrator/feed/update               # delta update feed
orchestrator/decision                  # decisioni prese dall'orchestratore
orchestrator/push/notify               # richiesta notifica al push-agent
orchestrator/push/announce             # richiesta annuncio vocale

system/agent/{agent_name}/status       # heartbeat e stato di ogni agente
system/agent/{agent_name}/log          # log operativo
```

---

## Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| Linguaggio | Python 3.12 |
| MQTT Broker | Mosquitto |
| LLM locale | Ollama + Qwen3-30B-A3B |
| LLM cloud | Claude API (Haiku per frequente, Sonnet per pesante) |
| Time-series DB | InfluxDB 2.x |
| Config DB | SQLite |
| Backend API | FastAPI + uvicorn |
| WebSocket | FastAPI WebSocket |
| Frontend | React/Preact + TypeScript |
| Tunnel | Cloudflare Tunnel (cloudflared) |
| Auth | Cloudflare Access (email OTP) |
| Edge | Cloudflare Workers |
| Process manager | systemd (o Docker Compose) |
| Zigbee | zigbee2mqtt + coordinator USB |
| TTS | Gemini TTS (gemini-2.5-flash-preview-tts) |
| Vision | Gemini Vision (gemini-2.0-flash) |

---

## Hardware

| Componente | Cosa | Prezzo stimato |
|---|---|---|
| Mini PC N100 16GB RAM, 512GB SSD | Tutto il sistema | ~€150 |
| SONOFF ZBDongle-E | Coordinator Zigbee USB | ~€30 |
| Atom Echo M5Stack ×3-4 | Terminali vocali nelle stanze | ~€50 |
| **Totale** | | **~€230** |

Il Green HA viene ritirato dopo la Fase 3 della migrazione.
