# Stick Logger LSW-3 - Investigazione completa

> Ultimo aggiornamento: 2026-02-23
> Fonte: investigazione diretta via HTTP e Solarman V5 protocol

## Identificazione

| Parametro | Valore |
|---|---|
| Modello | LSW-3-C (WiFi stick logger) |
| Serial Number (cover_mid) | 3168688670 |
| Inverter SN | 2504221369 |
| Firmware | LSW3_32_5406_SS_04_00.00.00.07 |
| Brand ID | 21510 (Deye) |
| Protocol ID | 82 |
| Dispositivi collegati | 1 |

## Rete

| Parametro | Valore |
|---|---|
| WiFi SSID | Akasha |
| IP LAN | 192.168.86.69 |
| MAC LAN | 74:E9:D8:07:5B:EC |
| RSSI | 70-76% (variabile) |
| Modalità | APSTA (AP + Station) |
| AP SSID | AP_3168688670 |
| AP IP | 10.10.100.254 |
| AP MAC | 70:E9:D8:07:5B:EC |

## Porte e servizi

| Porta | Servizio | Stato |
|---|---|---|
| 80 | Web interface HTTP | Funzionante (auth: admin:admin) |
| 8899 | Solarman V5 / Modbus passthrough | Accetta connessioni, MA non inoltra Modbus |
| 502 | Modbus TCP standard | Connection refused (non supportato) |

## Web Interface (porta 80)

### Pagine accessibili
- `status.html` - Stato in tempo reale (funziona)
- `remote.html` - Configurazione server remoti (modificabile ma NON usata dal firmware)
- `hide_set_edit.html` - Configurazione nascosta (protetta, non modificabile via POST)
- `config_hide.html` - Frame container per la pagina nascosta
- `index_cn.html` - Pagina principale
- Altre pagine (`data.html`, `record.html`, `config.html`, ecc.) restituiscono 404 nel body

### Dati real-time da status.html
Variabili JavaScript estratte dalla pagina:
```
webdata_sn = "2504221369"       # Inverter serial
webdata_now_p = "61109"          # Potenza attuale (valore raw, probabilmente signed 16-bit)
webdata_today_e = "0.0"          # Energia oggi (kWh)
webdata_total_e = "0.0"          # Energia totale (kWh)
webdata_utime = "4"              # Upload count (al cloud)
status_a = "1"                   # Connesso a Server A (cloud) ✓
status_b = "0"                   # NON connesso a Server B ✗
status_c = "0"                   # NON connesso a Server C ✗
```

## Configurazione server

### PROBLEMA CRITICO: Doppia configurazione

Il logger ha DUE sistemi di configurazione indipendenti:

#### 1. Configurazione nascosta (`hide_set_edit.html`) - USATA DAL FIRMWARE
```
server_a = ,5406.deviceaccess.host,10443,TCP    ← Cloud Solarman (funzionante)
server_b = ,5406.deviceaccess.host,10443,TCP    ← Cloud Solarman (duplicato)
```
- Questa configurazione è **protetta a livello firmware**
- I POST a `do_cmd.html` NON modificano questi valori
- Il firmware USA questi valori per il data forwarding

#### 2. Configurazione pubblica (`remote.html`) - NON USATA
```
server_b = 192.168.86.68,,10000,TCP              ← HA (configurato ma ignorato)
server_c = ,5406.deviceaccess.host,10443,TCP     ← Cloud Solarman
```
- Modificabile via POST a `do_cmd.html`
- Ma il logger NON usa questi valori per il forwarding effettivo

### Formato configurazione server
```
IP,hostname,porta,protocollo
```
Esempio: `192.168.86.68,,10000,TCP` (IP senza hostname) o `,5406.deviceaccess.host,10443,TCP` (hostname senza IP)

## Configurazione UART (Modbus RS485)

| Parametro | Valore |
|---|---|
| Baud Rate | 9600 |
| Data Bits | 8 |
| Parity | None |
| Stop Bits | 1 |
| Flow Control | NFC |
| Net Protocol | TCP |
| Net Mode | SERVER |
| Net Port | 8899 |
| Net Timeout | 300s |

## Test Solarman V5 Protocol (porta 8899)

### Keepalive (control 0x4710)
- **Funziona** - Il logger risponde correttamente al keepalive

### Business Data Request (control 0x4510) - Lettura Modbus
- **NON funziona** - Tutte le richieste restituiscono `status 0x01` con payload Modbus di soli 2 byte (`01 00`)
- Testati registri: 0, 500-504, 588 (Battery SOC)
- Testati unit ID: 0, 1, 2, 3, 247, 248
- Testato con e senza CRC Modbus
- Testato con keepalive preventivo
- Risultato sempre identico: status 0x01, nessun dato Modbus

### Interpretazione
Il `status 0x01` nel protocollo Solarman V5 indica che il logger non riesce a ottenere una risposta dall'inverter via Modbus RTU. Tuttavia il logger RIESCE a leggere dati dall'inverter internamente (evidenziato da `webdata_now_p` e `webdata_utime > 0`). Questo suggerisce che:
1. Il firmware usa un protocollo proprietario interno per comunicare con l'inverter (non Modbus standard)
2. Il Modbus passthrough per client esterni è rotto o disabilitato in questa versione firmware

## Integrazione Home Assistant

### Stato attuale
- Integrazione: `solarman_deye` (custom component)
- Modalità: **push (server)** su porta 10000
- Titolo: "Solarman Deye (push:10000)"
- Entry ID: `01KJ010931Z0DHTDN4W9JFBQKH`
- **Frame ricevuti: 0** ← Non funziona
- **Tutti i 44 sensori Deye in stato "unknown"**

### Perché non funziona
Il logger non si connette alla porta 10000 di HA perché la configurazione server nascosta (quella effettivamente usata dal firmware) punta entrambi i server al cloud Solarman, e non è modificabile via web interface.

## Soluzioni proposte

### 1. Solarman Cloud API (più semplice)
Installare l'integrazione HACS `ha_solarman` di David Rapan che usa il cloud API Solarman.
- Richiede: registrazione su api.solarmanpv.com per ottenere app_id e app_secret
- Pro: Nessuna modifica al logger, funziona subito
- Contro: Dipendenza dal cloud, latenza dati ~5 min

### 2. DNS Redirect (medio)
Reindirizzare `5406.deviceaccess.host` all'IP di HA (192.168.86.68) nel router/DNS locale.
- Il logger si connette a HA credendo sia il cloud
- Configurare l'integrazione HA su porta 10443
- Pro: Dati locali, nessun cloud
- Contro: Interrompe l'upload al cloud, richiede DNS locale

### 3. Adattatore RS485 diretto (più affidabile)
Collegare un adattatore USB-RS485 alla porta Modbus dell'inverter Deye.
- Bypassa completamente il stick logger
- Pro: Lettura diretta registri di configurazione, massima affidabilità
- Contro: Richiede hardware aggiuntivo e accesso fisico all'inverter

## Endpoint web utili

| Endpoint | Metodo | Descrizione |
|---|---|---|
| `GET /status.html` | GET | Stato real-time (scrape JS vars) |
| `GET /remote.html` | GET | Config server pubblica |
| `GET /hide_set_edit.html` | GET | Config server nascosta (read-only) |
| `POST /do_cmd.html` | POST | Salva configurazione (solo remote, non hidden) |
| `POST /success.html` | POST | Riavvio logger (`HF_PROCESS_CMD=RESTART`) |

Auth per tutti: `admin:admin` (Basic Auth)
