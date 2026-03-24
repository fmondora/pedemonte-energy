# Smart Surplus Advisor — Design

Data: 2026-03-24

## Obiettivo

Quando c'è un eccesso di produzione solare (>4kW), batteria carica (≥95%), e almeno 2 ore di sole residue secondo Forecast.Solar, il sistema notifica l'utente proponendo come usare il surplus: caricare la Tesla, accendere la sauna, o avviare elettrodomestici.

## Requisiti

- Notifica mobile (bottoni actionable) + annuncio Sonos (stile treno inglese, Gemini TTS dinamico)
- Una sola notifica per evento surplus (cooldown fino a reset)
- Sauna proposta solo 14:00-22:00, con accensione diretta dal bottone
- Tesla: solo suggerimento "collega", il SolarEdge EV Charger regola da solo
- Elettrodomestici (lavatrice, lavastoviglie, asciugatrice): solo suggerimento nel testo/voce
- Non tocca il sistema Abundance esistente

## Condizioni di attivazione

Tutte devono essere vere:

| Condizione | Sensore | Soglia |
|---|---|---|
| Surplus alto | `sensor.abundance_surplus_kw` | > 4 kW |
| Batteria carica | `sensor.deye_battery_soc` | ≥ 95% |
| Ore sole residue | `sensor.solar_forecast_hours_remaining` | ≥ 2h |
| Orario diurno | time | 09:00-18:00 |
| Non già notificato | `input_boolean.smart_surplus_notified` | off |

## Logica selezione carichi

| Carico | Condizione | Azione |
|---|---|---|
| Tesla | Batteria auto < 80% + auto a casa | Suggerimento testo |
| Sauna 90°C | Orario 14:00-22:00 | Bottone → accende switch |
| Lavatrice | Sempre | Suggerimento testo/voce |
| Lavastoviglie | Sempre | Suggerimento testo/voce |
| Asciugatrice | Sempre | Suggerimento testo/voce |

Priorità messaggio: Tesla > Sauna > Elettrodomestici.

## Bottoni notifica mobile

- Sauna disponibile (14-22): `[Accendi Sauna]` `[OK, grazie]`
- Tesla scarica + a casa: `[OK, collego Tesla]` `[OK, grazie]`
- Entrambe: `[Accendi Sauna]` `[OK, collego Tesla]` `[OK, grazie]`
- Elettrodomestici: sempre nel testo, nessun bottone

## Annuncio Sonos

- Ding + voce Gemini TTS (modello `gemini-2.5-flash-preview-tts`, voce `Kore`)
- Stile treno inglese, in inglese
- Testo dinamico generato da template Jinja2 con surplus, ore residue, carichi suggeriti
- Script Python 3.12 genera mp3, upload su HA media library, playback su `media_player.family_room`

## Componenti da creare

| Componente | Tipo | Scopo |
|---|---|---|
| `sensor.solar_forecast_hours_remaining` | template sensor | Ore di sole utile (>1kW) residue da Forecast.Solar |
| `input_boolean.smart_surplus_notified` | input_boolean | Cooldown: una notifica per evento |
| `automation.smart_surplus_advisor` | automazione HA | Trigger + logica + notifiche |
| `script.generate_surplus_tts` | shell_command | Python3.12 → Gemini TTS → mp3 → Sonos |

## Cooldown

- `input_boolean.smart_surplus_notified` → on dopo notifica
- Reset: mezzanotte OR surplus scende sotto 2kW

## Flusso

```
Surplus > 4kW (5 min) + SOC ≥ 95% + Ore sole ≥ 2h + non già notificato
    │
    ├─► Template Jinja2: costruisce messaggio con surplus, ore, carichi
    ├─► Notifica mobile con bottoni dinamici
    │       └─► "Accendi Sauna" → switch.turn_on sauna
    │       └─► "OK, grazie" → dismiss
    ├─► Shell command: python3.12 genera TTS → mp3 → Sonos (ding + annuncio)
    └─► input_boolean.smart_surplus_notified = on
```

## Approccio scelto

Automazione standalone (Approccio A) — separata dal sistema Abundance esistente.
