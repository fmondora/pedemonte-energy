# Tesla Solar Charger — Design

**Data:** 2026-04-12
**Stato:** Approvato
**Veicolo:** Biancaneve (Tesla Model S)

## Obiettivo

Regolare dinamicamente gli ampere di carica di Biancaneve per assorbire tutto il surplus solare, solo quando la batteria casa è piena. Cascata: batteria casa → Tesla → carichi termici → export rete.

## Setup fisico

- Tesla Model S "Biancaneve" collegata via UMC (Mobile Connector) a presa **CEE 16A trifase rossa**
- Nessun wallbox
- Controllo esclusivamente via API Tesla (integrazione HA già presente)

## Vincoli operativi

| Parametro | Valore | Motivazione |
|---|---|---|
| Range amps | 5 – 16 A trifase | 5A = min Tesla, 16A = max presa |
| Potenza Tesla | 3.45 – 11 kW | 1A trifase = 0.69 kW |
| Risoluzione | 1A (~690W) | step del number entity |
| Soglia attivazione | `battery_soc >= 95%` | Cascata A: batteria first |
| Soglia disattivazione | `battery_soc < 90%` | Isteresi per evitare cicli |
| Loop interval | 30 secondi | Veloce per transitori, lento per contattore |
| Dead-band pausa | 90s sotto min | Evita start/stop su nuvole passeggere |
| Dead-band riavvio | 60s sopra min+1A | Conferma surplus stabile |
| Target grid | -200W | Margine export per sicurezza |

## Pre-condizioni (tutte devono essere vere)

1. `input_boolean.tesla_solar_charger_enabled` = `on` (kill switch manuale)
2. `binary_sensor.biancaneve_online` = `on` (auto disponibile API)
3. `cover.biancaneve_charger_door` connesso (UMC plugged in)
4. `number.biancaneve_charge_limit` non raggiunto (SOC Tesla < limit)
5. `sensor.deye_battery_soc` >= 95%
6. Orario: tra alba e tramonto

## Out of scope

- Little Rascal (seconda Tesla)
- Caricamento da rete notturno
- Tariffe dinamiche (Octopus etc.)
- Pre-condizionamento auto per partenze programmate

## Architettura

**Runtime:** pyscript (custom component HA via HACS). Loop Python con accesso nativo alle entity HA, stato persistente in-memory, hot-reload via `pyscript/reload`.

```
┌─────────────────────────────────────────────────────────────┐
│  Home Assistant                                             │
│                                                             │
│  ┌──────────────────┐   ┌──────────────────────────────┐    │
│  │ Sensor inputs    │   │ pyscript:                    │    │
│  │ - grid_power     │──▶│ tesla_solar_charger.py       │    │
│  │ - battery_soc    │   │                              │    │
│  │ - bianca_charger │   │ @time_trigger("period(...)") │    │
│  │ - bianca_online  │   │ def control_loop():          │    │
│  └──────────────────┘   │   read sensors               │    │
│                         │   check pre-conditions       │    │
│  ┌──────────────────┐   │   compute delta_A            │    │
│  │ Actuators        │◀──│   apply hysteresis           │    │
│  │ - charging_amps  │   │   call services              │    │
│  │ - biancaneve_    │   │   log state                  │    │
│  │   charger switch │   └──────────────────────────────┘    │
│  └──────────────────┘                                       │
│                         ┌──────────────────────────────┐    │
│  ┌──────────────────┐   │ State exposure:              │    │
│  │ input_boolean    │──▶│ - sensor.tsc_state           │    │
│  │ tsc_enabled      │   │ - sensor.tsc_target_amps     │    │
│  │ (kill switch)    │   │ - sensor.tsc_session_energy  │    │
│  └──────────────────┘   │ - sensor.tsc_api_calls_today │    │
│                         └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### File da creare/modificare

| File | Tipo | Cosa fa |
|---|---|---|
| `homeassistant/pyscript/tesla_solar_charger.py` | nuovo | Loop principale e FSM |
| `homeassistant/pyscript/config.yaml` | nuovo | Config pyscript |
| `homeassistant/configuration.yaml` | modify | Aggiunge `pyscript:` |
| `homeassistant/configuration.yaml` | modify | Aggiunge `input_boolean.tesla_solar_charger_enabled` |
| `homeassistant/automations.yaml` | modify | Notifiche Sonos inizio/fine sessione |

## FSM — Macchina a stati

```
      ┌──────────┐
      │   IDLE   │◀───────────────────────────────┐
      └────┬─────┘                                │
           │ pre-condizioni OK                    │
           ▼                                      │
      ┌──────────┐                                │
      │ WAITING  │ osservo surplus                │
      └────┬─────┘                                │
           │ surplus ≥ 3.45kW per 60s             │
           ▼                                      │
      ┌──────────┐                                │
      │ CHARGING │─── surplus < min per 90s ──────┤
      │ (regola  │                                │
      │  amps)   │                                │
      └────┬─────┘                                │
           │ battery < 90% / Tesla full /         │
           │ pre-condizioni cadute / sunset       │
           ▼                                      │
      ┌──────────┐                                │
      │  PAUSED  │─── surplus assente → IDLE ─────┘
      └──────────┘
```

## Algoritmo di controllo (ogni 30s in CHARGING)

```python
def control_step():
    grid_kw = float(sensor.solaredge_grid_power)    # <0 = export
    amps_now = int(number.biancaneve_charging_amps)

    TARGET_GRID_KW = -0.2    # 200W margine export
    delta_kw = TARGET_GRID_KW - grid_kw
    delta_amps = round(delta_kw * 1000 / (230 * 3))  # trifase

    amps_target = clamp(amps_now + delta_amps, MIN_AMPS, MAX_AMPS)

    if amps_target == amps_now:
        return  # dead-band

    if amps_target < MIN_AMPS:
        samples_below_min += 1
        if samples_below_min * LOOP_INTERVAL >= PAUSE_DELAY_S:  # 90s
            enter_paused()
        return
    else:
        samples_below_min = 0

    number.set_value(entity_id="number.biancaneve_charging_amps", value=amps_target)
```

Note:
- Controllo **solo su grid_power** (cattura saldo residuo intero sistema)
- Delta **incrementale** (converge in 2-3 cicli)
- Lettura `charger_power` per diagnostic, non per controllo

## Safety — 7 layer

| Layer | Protezione | Azione |
|---|---|---|
| 1. Kill switch | `input_boolean.tesla_solar_charger_enabled` off | → IDLE, amps=0, charger off |
| 2. Hardware | UMC thermal sensor, Tesla max amps internal | Derating automatico |
| 3. Batteria casa | `battery_soc < 90%` (isteresi da 95%) | → IDLE |
| 4. Anti-import | `grid > +0.5kW` per 90s | → pausa immediata |
| 5. Rate limit | Max 1 scrittura API ogni 10s | Protegge budget API Tesla |
| 6. Watchdog | Charging=on ma power=0 per 5min / loop stallo 120s | Stop + notifica |
| 7. Notifiche | Inizio/fine sessione, anomalie | Sonos + push HA |

## Osservabilità

### Sensori esposti

| Entity | Tipo | Uso |
|---|---|---|
| `sensor.tsc_state` | string | idle/waiting/charging/paused |
| `sensor.tsc_target_amps` | int 0-16 | Dashboard, grafico storico |
| `sensor.tsc_session_energy` | float kWh | Notifica fine sessione |
| `sensor.tsc_session_duration` | minuti | Notifica |
| `sensor.tsc_api_calls_today` | int | Monitoring rate limit |

### Logging

Una riga ogni 30s nel log HA:
```
TSC [CHARGING] grid=-0.3kW bat=100% tesla=4.8kW@7A → 7A (no change)
TSC [CHARGING] grid=-1.8kW bat=100% tesla=4.8kW@7A → 10A (+3)
TSC [PAUSED]   grid=+0.2kW bat=92% → below min 2/3
```

## Integrazione Smart Surplus Advisor

Cascata completa:
```
Surplus disponibile?
  ├── battery_soc < 95% → surplus in batteria (automatico inverter)
  ├── battery_soc ≥ 95% E Tesla collegata → TSC modula carica
  ├── battery_soc ≥ 95% E Tesla NON collegata → Smart Surplus suggerisce termici
  └── nessuno → export rete
```

Modifica Smart Surplus: se `sensor.tsc_state = charging`, surplus già gestito → advisor non annuncia.

## Notifiche Sonos

| Evento | Messaggio | Destinazione |
|---|---|---|
| Sessione iniziata | "Biancaneve si ricarica col sole" | Sonos Family Room |
| Sessione terminata | "Carica completata: +X kWh in Y ore" | Sonos + push HA |
| Import anomalo | "Surplus esaurito, Biancaneve in pausa" | Push HA |
| Tesla non risponde | "Attenzione: Tesla non risponde, carica interrotta" | Push HA |
