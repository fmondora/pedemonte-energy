# Agent House — Design Document

Data: 2026-04-05
Branch: `agent-house`
Revisione: 2 — architettura ispirata a [Block "From Hierarchy to Intelligence"](https://block.xyz/inside/from-hierarchy-to-intelligence)

## Visione

La casa non è un sistema domotico con regole. È un organismo intelligente che osserva, impara, compone soluzioni, e si evolve. L'intelligenza è nel sistema, non nelle regole scritte dall'umano. L'umano è sull'edge — interviene per intuizione, etica, e decisioni che il sistema non deve prendere da solo.

> "Intelligence lives in the system. The people are on the edge."

---

## I quattro componenti

Ispirato direttamente dal framework Block:

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                   INTERFACES                          │  │
│   │   Feed adattivo · Push · Sonos · Alexa · Telegram    │  │
│   │   (superfici — importanti ma non il valore)          │  │
│   └──────────────────────────┬───────────────────────────┘  │
│                              │                               │
│   ┌──────────────────────────▼───────────────────────────┐  │
│   │              INTELLIGENCE LAYER                       │  │
│   │                                                       │  │
│   │   LangGraph stateful loop (checkpointed)             │  │
│   │   ┌─────────┐  ┌──────────┐  ┌───────────┐          │  │
│   │   │ Pattern │→│ Composer  │→│ Evaluator │          │  │
│   │   │ Detector│  │          │  │           │          │  │
│   │   └─────────┘  └──────────┘  └───────────┘          │  │
│   │        ↑              │              │               │  │
│   │        │              ▼              ▼               │  │
│   │   ┌────┴──────────────────────────────────┐          │  │
│   │   │          WORLD MODEL                   │          │  │
│   │   │   InfluxDB (segnali) + SQLite (stato)  │          │  │
│   │   │   "Il segnale più onesto è il kWh"     │          │  │
│   │   └────────────────────────────────────────┘          │  │
│   └──────────────────────────┬───────────────────────────┘  │
│                              │                               │
│   ┌──────────────────────────▼───────────────────────────┐  │
│   │                  CAPABILITIES                         │  │
│   │   Primitivi atomici, senza logica, componibili        │  │
│   │                                                       │  │
│   │   shelly.turn_on()    deye.get_soc()                 │  │
│   │   shelly.turn_off()   deye.set_charge_mode()         │  │
│   │   shelly.get_power()  solaredge.get_power()          │  │
│   │   zigbee.set_valve()  netatmo.get_climate()          │  │
│   │   ring.get_snapshot() tesla.set_charge_amps()        │  │
│   │   sonos.announce()    push.notify()                  │  │
│   │   velux.set_position() gemini.analyze_image()        │  │
│   │   gemini.generate_tts()                              │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Capabilities

Primitivi atomici. Zero logica. Come i "financial primitives" di Block (payments, lending, cards), le capabilities sono building block componibili. Ognuna fa **una cosa sola** e la fa bene.

### Principi

- **Atomiche**: `shelly.turn_on(device_id)` — non "accendi la luce se è buio e sono le 18"
- **Senza stato**: non ricordano nulla, non decidono nulla
- **Componibili**: l'intelligence layer le combina per creare soluzioni
- **Auto-documentate**: ogni capability dichiara cosa fa, che parametri prende, cosa ritorna
- **Testabili**: ogni capability ha un health check (`shelly.ping(device_id)`)

### Catalogo capabilities

#### Energia

| Capability | Cosa fa | Protocollo |
|---|---|---|
| `deye.get_state()` | SOC, power, grid, PV, load per fase | Deye Cloud API |
| `deye.set_charge_mode(mode)` | Selling First, Load First, Grid Charge | Deye Cloud API |
| `deye.set_charge_time(start, end, days)` | Programma ricarica da rete | Deye Cloud API |
| `solaredge.get_power()` | Produzione PV corrente | SolarEdge API |
| `solaredge.get_daily_energy()` | Energia giornaliera prodotta | SolarEdge API |
| `solaredge.get_evcharger()` | Stato ricarica EV | SolarEdge API |

#### Switch e luci

| Capability | Cosa fa | Protocollo |
|---|---|---|
| `shelly.turn_on(device_id)` | Accendi switch/dimmer | HTTP REST LAN |
| `shelly.turn_off(device_id)` | Spegni switch/dimmer | HTTP REST LAN |
| `shelly.set_brightness(device_id, level)` | Regola dimmer 0-100 | HTTP REST LAN |
| `shelly.get_state(device_id)` | Stato + power corrente | HTTP REST LAN |
| `shelly.get_power(device_id)` | Solo power in W | HTTP REST LAN |
| `shelly.list_devices()` | Scan rete, lista tutti gli Shelly | HTTP REST LAN |

#### Clima

| Capability | Cosa fa | Protocollo |
|---|---|---|
| `netatmo.get_climate(station)` | Temp, umidità, pressione, CO2, pioggia, vento | Netatmo API |
| `zigbee.get_temperature(device_id)` | Temperatura sensore | zigbee2mqtt/MQTT |
| `zigbee.set_valve(device_id, position)` | Regola valvola termostatica 0-100 | zigbee2mqtt/MQTT |
| `zigbee.get_contact(device_id)` | Stato sensore porta/finestra | zigbee2mqtt/MQTT |
| `velux.set_position(window_id, pos)` | Apri/chiudi finestra/tapparella | pyvlx LAN |

#### Sicurezza

| Capability | Cosa fa | Protocollo |
|---|---|---|
| `ring.get_last_motion()` | Ultimo evento motion con timestamp | Ring API |
| `ring.get_snapshot()` | Scatta e ritorna snapshot | Ring API |
| `gemini.analyze_image(image, prompt)` | Analisi Vision (garage aperto?) | Gemini API |
| `shelly.toggle_garage()` | Toggle relè garage (1s pulse) | HTTP REST LAN |

#### Trasporto

| Capability | Cosa fa | Protocollo |
|---|---|---|
| `tesla.get_state()` | SOC, stato ricarica, km, is_home | Tesla Fleet API |
| `tesla.set_charge_amps(amps)` | Regola corrente ricarica | Tesla Fleet API |
| `tesla.start_charging()` | Avvia ricarica | Tesla Fleet API |
| `tesla.stop_charging()` | Ferma ricarica | Tesla Fleet API |

#### Output (interfacce push)

| Capability | Cosa fa | Protocollo |
|---|---|---|
| `sonos.announce(speaker, audio_file)` | Annuncio con overlay | SoCo HTTP LAN |
| `sonos.play_ding(speaker)` | Suono ding | SoCo HTTP LAN |
| `push.notify(user, title, body, actions)` | Push mobile con azioni | ntfy |
| `telegram.send(user, text, image)` | Messaggio Telegram | Bot API |
| `gemini.tts(text, voice)` | Genera audio MP3 da testo | Gemini TTS API |

### Implementazione

Ogni capability è una **funzione Python asincrona** con:
- Tipo di ritorno dichiarato
- Retry automatico (max 3, backoff esponenziale)
- Timeout configurabile
- Health check
- Logging su MQTT `system/capability/{name}/call`

```python
# Esempio — NON implementazione, solo interfaccia
@capability(
    name="shelly.turn_on",
    description="Accende uno switch o dimmer Shelly",
    params={"device_id": "ID del device Shelly"},
    returns="bool — True se riuscito",
    retry=3,
    timeout=5
)
async def shelly_turn_on(device_id: str) -> bool:
    ...
```

L'intelligence layer vede il catalogo capabilities come un set di **tool LLM** — esattamente come Claude vede i suoi tool. Ogni capability è un tool con nome, descrizione, parametri, e tipo di ritorno.

---

## 2. World Model

Il world model è il cuore del sistema. Come in Block ("money is the most honest signal"), qui il segnale più onesto è il **kWh** e il **comportamento osservato**.

### Cosa contiene

#### Segnali real-time (MQTT state store in memoria)

Stato corrente di ogni device, aggiornato in continuo. È una foto istantanea della casa.

#### Segnali storici (InfluxDB)

| Categoria | Segnali | Frequenza |
|---|---|---|
| Energia Deye | SOC, battery_power, grid_power, load (L1/L2/L3), import/export | 5 min |
| Energia SolarEdge | PV power, daily/lifetime energy | 15 sec |
| Consumi per device | Power per ogni Shelly con metering | 30 sec |
| Clima | Temp/umidità per stanza e esterno, CO2, pioggia, vento | 5 min |
| Sicurezza | Motion events, stato sensori porta | evento |
| Tesla | SOC, stato ricarica, posizione | 15 min |
| Interazioni utente | Azioni accettate/rifiutate, trigger creati/modificati | evento |

#### Profili comportamentali (SQLite)

Non "preferenze dichiarate" ma **comportamento osservato**:

- "Francesco alza il termostato quando scende sotto 22°C" (non "Francesco preferisce 22°C")
- "La lavatrice gira il lunedì e il giovedì tra le 9 e le 11"
- "Lucia accende le luci cucina alle 6:45 nei giorni feriali"
- "Consumo base notturno: 180W. Se supera 400W, qualcosa è rimasto acceso"
- "Il sabato pomeriggio c'è un 60% di probabilità che Francesco accenda la sauna"

Questi profili vengono **aggiornati automaticamente** dall'intelligence layer:
- Sommari giornalieri → sommari settimanali → profilo globale
- Decay: pattern vecchi perdono peso, pattern recenti dominano

#### Stato della casa (SQLite)

| Dato | Esempio |
|---|---|
| Utenti | Francesco (admin), Lucia (family), Anna (limited), Vicki (limited) |
| Zone | Cucina, soggiorno, camere, garage, rooftop, cantina, spa |
| Device → zona mapping | shelly_24 → cucina, shelly_46 → soggiorno |
| Classificazione azioni | safe/critical per capability per utente |
| Trigger persistenti | Regole linguaggio naturale → codice generato |

### Il world model come contesto LLM

Prima di ogni chiamata LLM, il world model viene **compresso** in formato token-efficiente:

```
ENERGY: pv=5.2kW grid=-3.1kW(exporting) soc=98% load=2.1kW trend=↓
CLIMATE: soggiorno=21.5°/45% camera=19.8°/50% ext=15.2° rain=0 wind=3km/h
LIGHTS: scale=ON(5min) cucina=OFF 6_devices_off
SECURITY: all_clear ring_last=2h_ago garage=closed
TESLA: soc=65% not_charging home=yes
PATTERNS: saturday_afternoon sauna_probability=60% surplus_duration=2h
USER: francesco(admin) last_active=5min_ago
FAILURES: none
```

~200 token per descrivere l'intera casa. L'LLM ragiona su questo, non su kB di JSON.

---

## 3. Intelligence Layer

Non un orchestratore. Un **compositore** che vede pattern e compone soluzioni da capabilities atomiche.

### Architettura: LangGraph stateful loop

```
                    ┌─────────────────────┐
                    │   Observe           │
                    │   (leggi world      │
                    │    model changes)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Detect            │
                    │   (pattern match    │
                    │    + anomalie)      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
              ┌─────│   Compose           │
              │     │   (LLM: quale       │
              │     │    soluzione?)       │
              │     └──────────┬──────────┘
              │                │
              │     ┌──────────▼──────────┐
              │     │   Act               │
              │     │   (esegui           │
              │     │    capabilities)    │
              │     └──────────┬──────────┘
              │                │
              │     ┌──────────▼──────────┐
              │     │   Evaluate          │
              └─────│   (ha funzionato?   │
             retry  │    aggiorna world   │
                    │    model)           │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Present           │
                    │   (genera feed UI   │
                    │    + push)          │
                    └──────────┬──────────┘
                               │
                               └──────→ loop continuo
```

Ogni nodo è checkpointed su PostgreSQL. Il grafo sopravvive ai restart.

### Nodo Observe

Legge i cambiamenti dal world model (MQTT + InfluxDB). Produce un diff: "cosa è cambiato dall'ultimo ciclo?"

```
changes: [
  {signal: "deye.soc", from: 95, to: 98, delta: +3},
  {signal: "shelly.scale.state", from: "off", to: "on", duration: null},
  {signal: "solaredge.pv_power", from: 4800, to: 5200, trend: "rising"}
]
```

### Nodo Detect

Due modalità:

**LLM locale (Ollama, frequente)** — pattern matching veloce:
- "SOC salito sopra 95% con surplus crescente" → pattern: battery_full_surplus
- "Luce scale accesa" → pattern: staircase_timer_start
- "Consumo notturno anomalo" → pattern: anomaly_consumption

**Claude API (raro, su pattern complessi)**:
- "Da 3 giorni il consumo serale è 30% più alto del normale" → analisi profonda
- "Il forecast meteo dice pioggia per 3 giorni" → pianificazione strategica

### Nodo Compose

Il cuore. L'LLM riceve:
- Il pattern rilevato
- Il world model compresso
- Il catalogo capabilities disponibili
- I profili comportamentali degli utenti
- I trigger persistenti attivi

E compone una **soluzione** — una sequenza di capabilities da eseguire:

```json
{
  "pattern": "battery_full_surplus",
  "reasoning": "SOC 98%, surplus 5.2kW, sabato pomeriggio. Francesco accende la sauna il 60% dei sabati. Tesla a casa con SOC 65%.",
  "solution": [
    {"capability": "push.notify", "args": {"user": "francesco", "title": "Surplus 5.2kW", "body": "Batteria piena. Buon momento per la sauna o collegare Tesla.", "actions": [{"label": "Accendi sauna", "action": "sauna_on"}, {"label": "OK", "action": "dismiss"}]}},
    {"capability": "sonos.play_ding", "args": {"speaker": "family_room"}},
    {"capability": "gemini.tts", "args": {"text": "Good afternoon. 5.2 kilowatts of surplus available, battery fully charged. An excellent time for the sauna or to charge your Tesla."}},
    {"capability": "sonos.announce", "args": {"speaker": "family_room", "audio_file": "/tmp/surplus.mp3"}}
  ],
  "level": "safe",
  "auto_execute": true
}
```

Ma anche soluzioni che **nessuno ha chiesto**:

```json
{
  "pattern": "recurring_evening_drain",
  "reasoning": "Da 3 martedì consecutivi, consumo 18-20 sale a 3kW e mercoledì mattina SOC sotto 30%. Imposto carica notturna automatica.",
  "solution": [
    {"capability": "deye.set_charge_time", "args": {"start": "02:00", "end": "06:00", "days": ["tue", "thu"]}},
    {"capability": "push.notify", "args": {"user": "francesco", "title": "Nuova ottimizzazione", "body": "Ho notato consumi alti martedì/giovedì sera. Ho aggiunto carica notturna per avere batteria piena mercoledì. Va bene?", "actions": [{"label": "OK", "action": "confirm"}, {"label": "Annulla", "action": "revert"}]}}
  ],
  "level": "critical",
  "auto_execute": false
}
```

### Nodo Act

Esegue la sequenza di capabilities. Ogni esecuzione:
- Verifica il livello (safe/critical) e il ruolo utente
- Se critical e non admin: aspetta conferma (con timeout e default sicuro)
- Logga su InfluxDB e MQTT
- Gestisce errori con retry + strategia alternativa

### Nodo Evaluate

Dopo l'esecuzione, valuta:
- L'azione è riuscita? (capability ha ritornato successo?)
- L'effetto atteso si è verificato? (es. dopo `shelly.turn_off`, il power è sceso a 0?)
- Se no: riprova con strategia diversa o escalation

Aggiorna il world model con il risultato.

### Nodo Present

Produce il feed UI come array JSON di componenti, ordinati per priorità dall'LLM:

```json
[
  {"type": "alert", "severity": "high", "title": "...", "actions": [...]},
  {"type": "energy_card", "surplus_kw": 5.2, "soc": 98, ...},
  {"type": "insight", "title": "Oggi hai risparmiato €2.40", ...},
  {"type": "trigger_card", "description": "Carica notturna mar/gio", "status": "pending_approval"}
]
```

Il feed viene pushato via WebSocket a tutti i frontend connessi, filtrato per ruolo utente.

### Failure signals → roadmap

Come in Block: quando l'intelligence layer **non può comporre una soluzione**, genera un failure signal che diventa una proposta:

```json
{
  "type": "failure_signal",
  "pattern": "camera_ragazze_no_temperature",
  "reasoning": "Non posso ottimizzare il comfort in camera ragazze perché non ho un sensore di temperatura. Le valvole girano alla cieca.",
  "proposal": {
    "what": "Aggiungere sensore temperatura Zigbee in camera ragazze",
    "cost": "~€15",
    "benefit": "Stimo risparmio €3-5/mese con regolazione precisa valvola",
    "capabilities_unlocked": ["zigbee.get_temperature(camera_ragazze)"]
  }
}
```

Il sistema ti dice cosa gli manca, perché, quanto costa, e cosa guadagni. La roadmap della casa si auto-genera.

---

## 4. Interfaces

Le superfici attraverso cui il sistema interagisce con gli umani. Importanti ma **non il centro di valore** — il valore è nel world model e nell'intelligence layer.

Il principio: **il sistema raggiunge l'utente dove si trova**, non l'utente che va al sistema.

### Gerarchia delle interfacce

```
Voce (Alexa)     → "cosa succede?" "fai questo"     → interazione veloce, mani libere
Push (telefono)  → azione urgente, bottone rapido    → interruzione giustificata
Feed (web/PC)    → monitoring, trend, configurazione → consultazione approfondita
Sonos            → annunci proattivi del sistema     → il sistema ti cerca quando serve
Echo Show        → display ambientale per stanza     → la casa visibile dove sei
```

Non sono alternative — si **complementano**.

### Echo Show — terminali primari della casa

Gli Echo Show sostituiscono il ruolo del "tablet HA appeso al muro". Ma meglio: sono tanti, uno per stanza, ognuno contestuale. L'intelligence layer genera schermate **APL** (Alexa Presentation Language) dinamiche — stesso principio del feed JSON, ma renderizzato come UI nativa Alexa.

| Stanza | Device | Mostra |
|---|---|---|
| Cucina | Echo Show | Energia + clima + suggerimenti giornalieri |
| Soggiorno | Echo Show | Dashboard completa + musica + ospiti |
| Camera | Echo Show | Clima + sveglia + "buonanotte" |

Ogni schermata si adatta a **ora, stanza, utente, e stato della casa**:

- Echo Show cucina alle 7: "Buongiorno Lucia. Oggi sole fino alle 18, buon momento per la lavatrice dopo le 10."
- Echo Show cucina alle 22: "Buonanotte. Batteria 85%. Garage chiuso. Scale si spengono tra 3 min."

#### Confronto con HA Green

| | HA Green + tablet | Echo Show × stanze |
|---|---|---|
| Posizione | 1 posto, vai lì | Già dove sei |
| Input | Touch | Voce + touch |
| Contesto | Dashboard uguale ovunque | Dashboard per stanza |
| Manutenzione | Aggiornamenti HA, YAML, debug | Zero — il sistema genera le schermate |
| Costo aggiuntivo | Green €100 + tablet €200+ | Già presenti in casa |

### Alexa — voce bidirezionale

Due canali nello stesso Alexa Skill:

| Canale | Quando | Esempio | Passa dall'LLM? |
|---|---|---|---|
| **Smart Home** (diretto) | Comandi su device | "Alexa, spegni luce tavolo" | No — capability diretta, <1s |
| **Custom Skill** (conversazione) | Domande e richieste complesse | "Alexa, com'è la batteria?" | Sì — intelligence layer |

#### Smart Home Skill — comandi diretti

Ogni capability `shelly.*` viene esposta come device Alexa nativo. Nessun LLM coinvolto, latenza sotto il secondo:

- "Alexa, spegni luce del tavolo" → `shelly.turn_off(tavolo)`
- "Alexa, metti la luce del soggiorno al 50%" → `shelly.set_brightness(soggiorno, 50)`
- "Alexa, accendi la sauna" → verifica ruolo → `shelly.turn_on(sauna)`

#### Custom Skill — conversazione intelligente

Per domande, analisi, richieste complesse. L'intelligence layer riceve il testo, ragiona sul world model, compone la risposta:

- "Alexa, com'è la casa?" → "Tutto bene. Sei kilowatt di surplus, batteria piena."
- "Alexa, perché stanotte abbiamo consumato tanto?" → "Consumo medio 2.8 kW contro i soliti 1.2. Causa probabile: deumidificatore cantina rimasto acceso."
- "Alexa, com'è la batteria della macchina?" → "Tesla al 58%. Vuoi che inizi a caricare con il surplus?"

Su Echo Show, la risposta vocale è accompagnata da una **schermata APL contestuale** (grafico consumi, stato device, ecc.).

### Feed adattivo (web/PC)

- **React/Preact + TypeScript**, PWA installabile su telefono, tablet, PC
- **WebSocket** per aggiornamenti real-time
- **Pagina singola adattiva** — il feed si ricompone in base al contesto
- L'intelligence layer decide cosa mostrare, in che ordine, con che priorità
- Esposto su `casa.pedemonte.it` via Cloudflare Tunnel

Componenti UI (set fisso, ben progettati):

| Componente | Uso |
|---|---|
| `AlertCard` | Situazioni urgenti |
| `EnergyCard` | Stato energetico con gauge e grafici |
| `ClimateCard` | Temperature per stanza con target |
| `ActionButton` | Bottone contestuale |
| `StatusBadge` | "Casa tutto ok" |
| `InsightCard` | Pattern rilevati, consigli, risparmi |
| `ChartCard` | Grafici storici da InfluxDB |
| `TriggerCard` | Trigger persistente con stato e azioni |
| `FailureCard` | Proposta roadmap (cosa manca al sistema) |
| `NaturalInput` | Campo per creare regole in linguaggio naturale |

### Push (mobile)

- **ntfy** per push iOS/Android con azioni
- Azioni actionable: l'utente risponde direttamente dalla notifica
- Usato per interruzioni giustificate: surplus, anomalie, conferme critiche

### Sonos (voce output)

- **SoCo** per annunci sulla Soundbar e SpaMusic
- **Gemini TTS** per annunci dinamici (stile treno inglese)
- Ding + annuncio con `announce: true` (overlay su musica)
- Annunci proattivi — il sistema parla quando ha qualcosa di rilevante da dire

### Telegram

- Bot per messaggi testo + foto (snapshot Ring, grafici)
- Canale asincrono — per report, riassunti giornalieri, foto sicurezza

---

## Utenti e Ruoli

### Chi sono

| Utente | Ruolo | Vede nel feed | Azioni safe | Azioni critical | Push |
|---|---|---|---|---|---|
| Francesco | admin | Tutto + failure signals + config | Tutte | Tutte (senza conferma) | ntfy (Clancy) + Telegram |
| Lucia | family | Energia (vista), clima, comfort, garage | Luci, temperatura, scene | Garage (con conferma) | ntfy (iPhone Lucia) |
| Anna | limited | Comfort, garage | Luci sua zona, scene | Garage (con conferma) | — |
| Vicki | limited | Comfort, garage | Luci sua zona, scene | Garage (con conferma) | — |

### Autenticazione

- **Cloudflare Access**: email OTP, zero password
- Email → ruolo mappato in SQLite
- Token JWT nel WebSocket identifica l'utente

### Safe vs Critical

| Livello | Comportamento | Esempi |
|---|---|---|
| **safe** | Esecuzione immediata | Spegni luce, regola dimmer, leggi sensore |
| **critical** | Admin: esegue. Altri: conferma push con timeout | Garage, sauna, carica da rete, azioni costose |

Default sicuri sui timeout:
- Garage aperto da >2h → chiude
- Sauna non confermata in 10 min → non accende
- Classificazione configurabile per utente

---

## Esposizione Internet

### Cloudflare Tunnel

- `cloudflared` sul mini PC, tunnel persistente
- Zero porte aperte sul router
- Dominio: `casa.pedemonte.it` (o simile)

### Cloudflare Access

- Policy per email: francesco@*, lucia@*, anna@*, vicki@*
- Auth via email OTP

### Cloudflare Workers

- Cache feed JSON sull'edge (5 sec)
- Rate limiting
- Asset serving frontend
- Fallback "casa offline" se tunnel down

---

## Il loop di feedback (flywheel)

Come il flywheel di Block ("richer signal → better model → more transactions → richer signal"):

```
Più segnali dai device
    → world model più ricco
        → pattern detection più accurata
            → soluzioni composte più intelligenti
                → utente accetta più spesso
                    → più feedback nel world model
                        → loop continuo
```

Ogni interazione dell'utente (accetta, rifiuta, modifica) arricchisce il world model. Il sistema diventa più intelligente con l'uso, non con il codice.

---

## Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| Linguaggio | Python 3.12 |
| Intelligence loop | LangGraph + checkpointing PostgreSQL |
| LLM locale | Ollama + Qwen3-30B-A3B (pattern detection frequente) |
| LLM cloud | Claude API Haiku/Sonnet (composizione complessa) |
| World model (time-series) | InfluxDB 2.x |
| World model (stato/config) | SQLite |
| Checkpointing | PostgreSQL |
| Messaging | MQTT (Mosquitto) |
| Backend API | FastAPI + uvicorn + WebSocket |
| Frontend | React/Preact + TypeScript (PWA) |
| Tunnel | Cloudflare Tunnel |
| Auth | Cloudflare Access |
| Edge | Cloudflare Workers |
| Process manager | Docker Compose |
| Zigbee | zigbee2mqtt + coordinator USB |
| TTS | Gemini TTS |
| Vision | Gemini Vision |

---

## Hardware

| Componente | Cosa | Prezzo stimato |
|---|---|---|
| Mac Mini M4 Pro 48GB RAM, 512GB SSD | Server principale — CPU+GPU unified memory, MLX per LLM locale, ~5W idle, silenzioso | ~€1.650 |
| SONOFF ZBDongle-E | Coordinator Zigbee USB | ~€30 |
| Atom Echo M5Stack ×3-4 | Terminali vocali (futuro) | ~€50 |
| **Totale** | | **~€1.730** |

### Perché Mac Mini M4 Pro 48GB

- **Unified memory**: CPU e GPU condividono 48GB — modelli LLM da 30B+ girano senza copiare dati tra CPU/GPU
- **MLX**: framework Apple ottimizzato per inference su Apple Silicon, usato nativamente da Ollama
- **5W idle**: server 24/7 con consumo trascurabile — coerente con una casa a surplus solare
- **Silenzioso**: nessuna ventola GPU, adatto a un ambiente domestico
- **Capacità LLM**: Qwen3-30B-A3B senza quantizzazione, o due modelli in parallelo (pattern detection + composizione)
- **Docker**: via OrbStack, supporto nativo ARM per tutti i container dello stack

---

## Migrazione da HA

### Fase 1 — World Model

InfluxDB raccoglie segnali in parallelo a HA. Le capabilities vengono implementate e testate una per una. Il world model si riempie. L'intelligence layer osserva ma non agisce.

### Fase 2 — Intelligence attiva

L'intelligence layer inizia a comporre soluzioni. Prima solo notifiche (safe). Poi azioni con conferma (critical). HA resta come fallback — se l'intelligence layer non gestisce qualcosa, HA lo fa.

### Fase 3 — Spegnimento HA

Quando il world model è ricco abbastanza e l'intelligence layer copre tutti gli scenari, HA viene spento. Il coordinator Zigbee USB passa al mini PC. Il Green viene ritirato.

### Cosa cambia rispetto al design v1

| Design v1 (orchestratore) | Design v2 (intelligence layer) |
|---|---|
| Device agents con logica interna | Capabilities atomiche senza logica |
| Orchestratore esegue regole/LLM | Intelligence layer compone soluzioni da pattern |
| Feed UI generato da template | Feed UI generato dal contesto del world model |
| Automazioni migrate da HA | Automazioni auto-generate da pattern osservati |
| L'umano scrive le regole | Il sistema propone, l'umano approva o corregge |
| Errori → retry | Errori → retry → strategia alternativa → failure signal |
| Statico: funziona come lo programmi | Si evolve: impara dai segnali e dal feedback |

---

## Device — mapping completo

### Rete attuale

| Device | IP | Capability | Protocollo |
|---|---|---|---|
| Shelly Pro DM 2PM | .24, .46, .73, .74 | shelly.* | HTTP REST LAN |
| Shelly Plus 2PM | .37, .42 | shelly.* | HTTP REST LAN |
| Shelly Plus 1PM | .39 | shelly.* | HTTP REST LAN |
| Shelly 1PM Mini G3 | .35 | shelly.* | HTTP REST LAN |
| ESP8266/Shelly Gen1 | .55 | shelly.* | HTTP REST LAN |
| Deye Stick Logger | .69 | deye.* | Deye Cloud API |
| Velux KLF 200 | TBD | velux.* | pyvlx LAN |
| Sonos Soundbar | LAN | sonos.* | SoCo HTTP |
| Sonos SpaMusic | LAN | sonos.* | SoCo HTTP |
| Ring Doorbell | cloud | ring.* | Ring API |
| Tesla Biancaneve | cloud | tesla.* | Tesla Fleet API |
| SolarEdge SE10K-RWS | cloud | solaredge.* | SolarEdge API |
| SolarEdge EV Charger | cloud | solaredge.* | SolarEdge API |
| Netatmo Weather | cloud | netatmo.* | Netatmo API |
| Zigbee devices | USB coordinator | zigbee.* | zigbee2mqtt |
| HA Green | .68 | — | Ritirato in Fase 3 |
| Fire TV Stick | .64 | — | Resta con Alexa |
| Echo ×4 | .59 + altri | — | Resta con Alexa (futuro: Skill) |

### Automazioni HA → Pattern dell'intelligence layer

| Automazione HA | Pattern equivalente | L'intelligence layer... |
|---|---|---|
| Scale spegni luci 5 min | `staircase_light_on` | Compone: aspetta 5min → `shelly.turn_off` → `sonos.announce` |
| Garage action (iOS button) | `user_action_garage` | Compone: verifica ruolo → `shelly.toggle_garage` |
| Battery full announcement | `battery_full_surplus` | Compone: `sonos.play_ding` → `gemini.tts` → `sonos.announce` |
| Smart Surplus Advisor | `sustained_surplus` | Compone: analizza surplus/SOC/forecast/abitudini → propone azioni contestuali |
| Regola ricarica Tesla | `solar_production_high` | Compone: calcola ampere da PV → `tesla.set_charge_amps` |
| Ventilazione cantina | `cellar_climate_drift` | Compone: confronta temp/umidità cantina vs esterno → `shelly.turn_on(ventola)` |
| Ring garage detection | `ring_motion_detected` | Compone: `ring.get_snapshot` → `gemini.analyze_image` → se garage aperto: `push.notify` |
| Spegnimento luci >1h | `light_forgotten_on` | Compone: rileva luce on >1h senza attività → `shelly.turn_off` |
| Zanzare off alle 6:00 | `daily_schedule` | Compone: cron 6:00 → `shelly.turn_off(zanzare)` |

La differenza chiave: le automazioni HA sono **regole statiche**. I pattern dell'intelligence layer sono **rilevati dai dati** e le soluzioni sono **composte dinamicamente**. Se un pattern cambia (d'estate i consumi serali calano), il sistema si adatta senza che nessuno tocchi il codice.

---

## MQTT Topic Convention

```
# Capabilities (stato e comandi)
capability/{family}/{device_id}/state     # stato pubblicato
capability/{family}/{device_id}/command   # comandi ricevuti
capability/{family}/{device_id}/health    # health check

# Intelligence layer
intelligence/observe/changes              # diff dal world model
intelligence/detect/pattern               # pattern rilevato
intelligence/compose/solution             # soluzione composta
intelligence/act/execution                # esecuzione in corso
intelligence/evaluate/result              # risultato valutazione
intelligence/present/feed                 # feed UI corrente
intelligence/failure/signal               # cosa manca al sistema

# Sistema
system/capability/{name}/call             # log chiamate capability
system/capability/{name}/error            # errori con contesto
system/worldmodel/update                  # aggiornamento world model
system/heartbeat                          # stato di tutti i processi
```
