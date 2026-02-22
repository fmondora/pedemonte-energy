# Inventario Entity Home Assistant - Casa Pedemonte
Data: 2026-02-22

## Riepilogo

| Metrica | Valore |
|---|---|
| **Entity totali** | 1086 |
| **Funzionanti (OK)** | 743 (68%) |
| **Unavailable** | 216 (20%) |
| **Unknown** | 127 (12%) |
| **Non mappate/auto-generate** | 178 (16%) |

## Entity per dominio

| Dominio | Totale | OK | Unavail | Unknown | Note |
|---|---|---|---|---|---|
| automation | 41 | 34 | 7 | 0 | |
| binary_sensor | 139 | 112 | 25 | 2 | |
| button | 39 | 0 | 13 | 26 | Tutti unknown/unavail (normale per button) |
| camera | 1 | 1 | 0 | 0 | |
| climate | 4 | 2 | 2 | 0 | Bumbeta + Jacquelyn unavail |
| cover | 18 | 10 | 8 | 0 | Bumbeta + Jacquelyn unavail |
| device_tracker | 15 | 6 | 4 | 5 | |
| event | 33 | 20 | 0 | 13 | |
| input_boolean | 1 | 1 | 0 | 0 | |
| input_number | 3 | 2 | 1 | 0 | |
| input_select | 3 | 3 | 0 | 0 | |
| light | 23 | 21 | 2 | 0 | |
| lock | 8 | 3 | 4 | 1 | |
| media_player | 8 | 6 | 2 | 0 | |
| number | 26 | 18 | 6 | 2 | |
| person | 6 | 3 | 0 | 3 | Anna, Davide, Michele = unknown |
| script | 9 | 6 | 3 | 0 | |
| select | 29 | 12 | 14 | 3 | |
| sensor | 494 | 335 | 96 | 63 | Dominio più grande |
| switch | 122 | 95 | 25 | 2 | |
| update | 47 | 43 | 2 | 2 | |
| altri | 18 | 13 | 2 | 3 | |

---

## Problemi principali identificati

### 1. Veicoli fantasma: Bumbeta e Jacquelyn (tutte unavailable)
Ci sono 2 veicoli Tesla completamente unavailable che generano ~60 entity inutili:
- `*.bumbeta_*` — ~20 entity, tutte unavailable
- `*.jacquelyn_*` — ~20 entity, tutte unavailable

**Azione consigliata**: Rimuovere queste integrazioni Tesla da HA se i veicoli non esistono più.

### 2. Deye Solarman: tutte le entity in unknown (40+ entity)
Tutte le entity `sensor.solarman_deye_3168688670_*` sono in stato **unknown** con `frames_received = 0`.
Il server è in ascolto (`Listening on port 10000`) ma non riceve dati dall'inverter.

**Azione consigliata**: Verificare connettività Solarman → inverter Deye (dongle WiFi, IP, rete).

### 3. Dispositivi CozyLife/Unknown con MAC address (15+ entity)
Switch e sensori con nomi tipo `unknown_00_04_74_*` — sono dispositivi CozyLife non identificati:
- `switch.unknown_00_04_74_00_01_45_bc_80` — sconosciuto
- `switch.unknown_00_04_74_00_01_5d_3c_fa` — sconosciuto
- `switch.unknown_00_04_74_00_01_5d_3d_13` — sconosciuto
- `switch.unknown_00_04_74_00_01_71_2c_09` — Luce bagnetto
- `switch.unknown_00_04_74_00_01_71_2c_37` — Light 8
- `switch.unknown_00_04_74_00_01_71_42_5e` — Loft
- `switch.unknown_00_04_74_00_01_71_42_88` — Lampada Deck
- `switch.unknown_00_04_74_00_01_71_42_90` — Light 7
- `switch.unknown_00_04_74_00_01_71_42_93` — Light 6
- `switch.unknown_00_04_74_00_01_71_58_0b` — sconosciuto

**Azione consigliata**: Rinominare i dispositivi CozyLife nell'interfaccia HA. Identificare i 4 totalmente sconosciuti.

### 4. Sensore Netatmo Unknown 70:ee:50:7a:93:24
Un modulo Netatmo che funziona (CO2, temp, umidità, pressione, rumore) ma non è stato identificato/rinominato.

**Azione consigliata**: Rinominare in HA (probabile modulo interno soggiorno/sala).

### 5. Shelly non rinominati
Molti Shelly hanno ancora il nome auto-generato con MAC:
- `shellyprodm2pm_08f9e0e4a51c` — Light 1 senza nome
- `shellyprodm2pm_08f9e0e4b920` — Light 0 senza nome
- `shellyplus1pm_c4d8d5429dc0` — completamente senza nome
- `shellypro4pm_34987a46d3e0_switch_3` — "Luci e Gavoni switch_3" generico

### 6. Dishwasher Pedemonte: tutto unavailable (~20 entity)
La lavastoviglie Bosch/Siemens Home Connect è completamente offline.

**Azione consigliata**: Verificare connessione WiFi della lavastoviglie e ri-autenticare Home Connect.

### 7. Automazioni unavailable (7)
- `automation.aggiorna_energia_consumata_asciugatrice`
- `automation.avvia_musica_spa_da_spotify_con_la_sauna`
- `automation.incrementa_contatore_pressioni_veranda`
- `automation.set_sauna_status_to_idle_and_stop_music_on_switch_off`
- `automation.shelly_webhook`
- `automation.temperatura_ragazze`
- `automation.toggle_dispositivi_con_shelly_button`

**Azione consigliata**: Queste automazioni fanno riferimento ad entity/servizi che non esistono più. Vanno fixate o rimosse.

### 8. Script duplicati/unavailable
- `script.turn_off_lightst` (typo!) — unavailable
- `script.turn_off_the_lights_after_1_hour` — unavailable (duplicato di `script.turn_off_lights`)
- `script.start_sauna_with_temperature` — unavailable

### 9. Samsung TV: parzialmente unavailable
La TV Samsung QN90BA 75 ha lo switch unavailable e molti sensori unavailable. Normale quando è spenta, ma lo switch dovrebbe funzionare via Wake-on-LAN.

### 10. Person tracking incompleto
- Anna, Davide, Michele: stato **unknown** (nessun device tracker associato o app non configurata)

---

## Mappa dispositivi Shelly

| Entity ID (MAC) | Nome assegnato | Posizione probabile |
|---|---|---|
| shellyprodm2pm_08f9e0e4c01c | Noble Silence | Camera? |
| shellyprodm2pm_08f9e0e4a51c | Bed light / Light 1 (non nominato) | Camera da letto rooftop |
| shellyprodm2pm_08f9e0e4b864 | Rooftop Bathroom / Rooftop light | Bagno + luce rooftop |
| shellyprodm2pm_08f9e0e4b920 | Light 0 (non nominato) / Spa Light | Zona spa |
| shellypro4pm_34987a46d3e0 | Luci e Gavoni (4 canali) | Gavone sud, scala rooftop, +2 |
| shellyplus1pm_10061cd19aa4 | Presa Ospiti | Camera ospiti |
| shellyplus1pm_c4d8d5429dc0 | (senza nome) | ? |
| shelly1pmminig3_543204503e2c | Ventola Cantina | Cantina |

---

## Azioni prioritarie consigliate

1. **Rimuovere integrazioni Bumbeta/Jacquelyn** → elimina ~60 entity inutili
2. **Fixare connessione Deye Solarman** → riattiva ~40 entity energia
3. **Rinominare dispositivi CozyLife** in HA → identifica ~15 entity
4. **Rinominare Netatmo sconosciuto** → identifica 5 entity
5. **Rinominare Shelly senza nome** → identifica ~5 entity
6. **Fixare/rimuovere 7 automazioni rotte**
7. **Rimuovere script duplicati** (typo `turn_off_lightst`)
8. **Verificare lavastoviglie Home Connect**
9. **Configurare app HA per Anna, Davide, Michele**
