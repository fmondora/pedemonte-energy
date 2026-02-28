# Opzioni di Integrazione Deye SUN-12K-SG04LP3-EU con Home Assistant

> Ultimo aggiornamento: 2026-02-28
> Autore: deye-expert, team-lead
> Contesto: Deye Cloud API integrata in HA come command_line sensor

## Situazione Attuale

**INTEGRAZIONE ATTIVA: Deye Cloud API (Opzione 4)** - implementata il 2026-02-28.

L'inverter Deye SUN-12K-SG04LP3-EU è ora monitorato in HA tramite la Deye Cloud API:
- **Script**: `homeassistant/scripts/deye_cloud_sensor.py` (solo stdlib, no dipendenze esterne)
- **Sensore**: `command_line` sensor `sensor.deye_inverter` con polling ogni 5 minuti
- **Credenziali**: in `/config/secrets.yaml` (deye_appid, deye_appsecret, deye_email, deye_password)
- **13 template sensors** derivati dagli attributi del sensore principale

### Sensori attivi in HA

**Energia (kWh, total_increasing) - per Energy Dashboard:**
- `sensor.deye_grid_import_energy` ← `TotalEnergyBuy` (contatore hardware CT)
- `sensor.deye_grid_export_energy` ← `TotalEnergySell` (contatore hardware CT)
- `sensor.deye_battery_charge_energy` ← `TotalChargeEnergy`
- `sensor.deye_battery_discharge_energy` ← `TotalDischargeEnergy`
- `sensor.deye_consumption_energy` ← `TotalConsumption`

**Potenza (W, measurement) - per monitoraggio real-time:**
- `sensor.deye_battery_power` ← `BatteryPower`
- `sensor.deye_grid_power` ← `TotalGridPower`
- `sensor.deye_consumption_power` ← `TotalConsumptionPower`

**Stato:**
- `sensor.deye_battery_soc` ← `SOC` (%)
- `sensor.deye_battery_voltage` ← `BatteryVoltage` (V)
- `sensor.deye_inverter_temperature` ← `AC Temperature` (°C)

**Giornalieri (kWh):**
- `sensor.deye_daily_production` ← `DailyActiveProduction`
- `sensor.deye_daily_consumption` ← `DailyConsumption`

### Energy Dashboard configurato con:
- **Rete**: `sensor.deye_grid_import_energy` / `sensor.deye_grid_export_energy` (contatori HW, sostituiscono i vecchi Riemann sum)
- **Solare**: `sensor.solar_production_energy` (Riemann sum su SolarEdge, unica fonte PV)
- **Batteria**: `sensor.deye_battery_charge_energy` / `sensor.deye_battery_discharge_energy`

### Note tecniche API
- La risposta API usa `deviceDataList` come chiave (NON `data`)
- Il token è nel campo `accessToken` (camelCase)
- L'API restituisce ~75 datapoint per device
- I valori cumulativi (Total*) sono contatori hardware molto più accurati dei Riemann sum

### Cosa è stato rimosso
- `sensor.grid_import_energy` (Riemann sum su grid_import_power) → sostituito da `sensor.deye_grid_import_energy`
- `sensor.grid_export_energy` (Riemann sum su grid_export_power) → sostituito da `sensor.deye_grid_export_energy`
- I template sensors `grid_import_power` e `grid_export_power` sono MANTENUTI (usati da Abundance)

---

### Integrazioni precedentemente tentate (NON funzionanti)

L'integrazione locale con Home Assistant non funziona:

- **Modbus passthrough (porta 8899)**: risponde con status 0x01, il firmware non inoltra le richieste Modbus
- **Push mode (solarman_deye su porta 10000)**: 0 frame ricevuti, la configurazione nascosta del logger punta entrambi i server al cloud e non e' modificabile

Le opzioni alternative sono documentate sotto per riferimento futuro (es. upgrade a RS485 per latenza < 5s).

---

## Opzione 1: Solarman Cloud API

### Descrizione
Utilizzare l'API cloud di Solarman per recuperare i dati dell'inverter tramite un'integrazione HACS dedicata. I dati passano dal logger al cloud Solarman, e Home Assistant li recupera via API REST.

### Integrazioni disponibili

#### A) `home-assistant-solarman-api` (daspilker)
- Repository: https://github.com/daspilker/home-assistant-solarman-api
- Integrazione specifica per API cloud Solarman
- Richiede: credenziali Solarman Cloud + serial number inverter
- Testata con Deye SUN600G3-EU-230 (microinverter), compatibilita' con ibridi da verificare

#### B) `ha-solarman` (David Rapan) - modalita' cloud
- Repository: https://github.com/davidrapan/ha-solarman
- Principalmente per accesso locale via Solarman V5, ma supporta anche modalita' cloud
- Basata su pysolarmanv5 asincrono
- Supporta inverter Deye ibridi (profili disponibili nella wiki)
- Integrazione piu' matura e con community attiva

### Passi pratici

1. **Registrazione API Solarman**
   - Inviare email a service@solarmanpv.com o info@solarmanpv.com
   - Richiedere app_id e app_secret per accesso API
   - Specificare: uso personale per monitoraggio Home Assistant
   - Fornire: email, nome, serial number del logger (3168688670)
   - Endpoint API: https://api.solarmanpv.com
   - Tempo di risposta stimato: 1-5 giorni lavorativi

2. **Installazione integrazione HACS**
   - In HA, andare su HACS > Integrazioni > menu 3 punti > Repository personalizzato
   - Aggiungere URL del repository (daspilker o davidrapan)
   - Cercare "Solarman" e installare
   - Riavviare Home Assistant

3. **Configurazione**
   - Andare su Impostazioni > Dispositivi e servizi > Aggiungi integrazione
   - Cercare "Solarman API" o "Solarman"
   - Inserire: app_id, app_secret, email account Solarman, password, serial inverter
   - Selezionare il profilo del dispositivo (Deye SG04LP3)

### Sensori disponibili (stimati)
- Potenza PV istantanea (W)
- Energia prodotta oggi/totale (kWh)
- Potenza batteria carica/scarica (W)
- SOC batteria (%)
- Tensione/corrente batteria
- Potenza griglia import/export (W)
- Potenza carico (W)
- Tensioni e correnti per fase (L1, L2, L3)
- Temperatura inverter
- Stato operativo

### Valutazione

| Criterio | Valore |
|---|---|
| **Hardware necessario** | Nessuno |
| **Costo** | Gratuito |
| **Complessita'** | Bassa - solo configurazione software |
| **Affidabilita'** | Media - dipende dal cloud Solarman (uptime, manutenzione, policy API) |
| **Latenza dati** | 5-15 minuti (il logger invia dati ogni 5 min, poi l'API li rende disponibili) |
| **Mantiene cloud** | Si - nessuna modifica al logger |
| **Scrittura registri** | No - solo lettura via API cloud |
| **Rischio** | Basso - Solarman potrebbe cambiare policy API o revocare accesso |

---

## Opzione 2: DNS Redirect

### Descrizione
Reindirizzare il dominio `5406.deviceaccess.host` (usato dal logger per connettersi al cloud) verso l'IP di Home Assistant. Il logger crede di connettersi al cloud ma in realta' invia i dati a HA, dove l'integrazione solarman_deye in push mode li riceve.

### Attenzione - Rischi importanti

1. **TLS/Encryption**: Deye ha iniziato a distribuire firmware che introduce TLS nelle comunicazioni. Se il firmware del nostro logger (LSW3_32_5406_SS_04_00.00.00.07) usa TLS, il redirect non funzionera' perche' HA non puo' presentare un certificato valido per il dominio Solarman.

2. **IP hardcoded**: Alcuni firmware usano IP hardcoded oltre al DNS, rendendo il redirect inefficace.

3. **Perdita cloud**: Reindirizzando il DNS, si perde il monitoraggio cloud Solarman (app + portale).

### Passi pratici

1. **Identificare l'IP del server Solarman**
   ```bash
   nslookup 5406.deviceaccess.host
   # Annotare l'IP per eventuale ripristino
   ```

2. **Configurare DNS override nel router**
   - Accedere al pannello di amministrazione del router (Google Wifi/Nest)
   - Nota: Google Wifi/Nest NON supporta DNS override personalizzato nativamente
   - **Alternativa A**: Configurare Pi-hole o AdGuard Home su HA come DNS server
     - Installare add-on AdGuard Home in HA
     - Aggiungere regola DNS rewrite: `5406.deviceaccess.host` -> `192.168.86.68` (IP di HA)
     - Impostare il router per usare HA come DNS server primario
   - **Alternativa B**: Usare un file hosts se si ha accesso a un DNS server locale

3. **Configurare HA per ricevere i dati**
   - L'integrazione `solarman_deye` (gia' installata) in push mode
   - Cambiare la porta di ascolto da 10000 a **10443** (la porta usata dal logger per il cloud)
   - Oppure: configurare un port forward nel firewall di HA da 10443 a 10000
   - Il logger si connettera' a HA:10443 credendo sia il cloud

4. **Riavviare il logger**
   ```bash
   curl -u admin:admin -X POST http://192.168.86.69/success.html \
     -d "HF_PROCESS_CMD=RESTART"
   ```

5. **Verificare la connessione**
   - Controllare `status_a` su http://192.168.86.69/status.html
   - Se diventa 1, il logger si connette a HA
   - Verificare in HA che i sensori Deye mostrino dati

### Valutazione

| Criterio | Valore |
|---|---|
| **Hardware necessario** | Nessuno (ma serve Pi-hole/AdGuard se il router non supporta DNS override) |
| **Costo** | Gratuito |
| **Complessita'** | Alta - richiede DNS override, possibili problemi TLS, debug networking |
| **Affidabilita'** | Bassa-Media - TLS potrebbe bloccare tutto, IP hardcoded possibile |
| **Latenza dati** | 1-5 minuti (intervallo di invio del logger) |
| **Mantiene cloud** | **No** - il cloud Solarman viene perso |
| **Scrittura registri** | No - il protocollo push e' solo dati dal logger |
| **Rischio** | Medio-Alto - potrebbe non funzionare affatto per TLS, si perde il cloud |

---

## Opzione 3: Gateway RS485 Esterno (Elfin EW11 o USB-RS485)

### Descrizione
Collegare un gateway RS485-to-WiFi (Elfin EW11/EW11A) o un adattatore USB-RS485 direttamente alla porta Modbus RTU dell'inverter Deye, bypassando completamente lo stick logger. Home Assistant comunica via Modbus TCP con il gateway.

### Porte di comunicazione del Deye SG04LP3

L'inverter ha diverse porte di comunicazione sul pannello inferiore:

1. **Porta WiFi/COM** (porta 16) - usata dallo stick logger LSW-3-C
   - Connettore proprietario Deye per data logger
   - Lo stick logger e' gia' collegato qui
   - **NON disponibile** per uso esterno

2. **Porta BMS/RS485** (porta RJ45) - per comunicazione batteria
   - Pin 1: RS485_B, Pin 2: RS485_A (RS485 per Modbus)
   - Pin 4: CAN-H, Pin 5: CAN-L (CAN bus per BMS batteria)
   - Pin 3/6: GND
   - Pin 7: RS485_A (duplicato), Pin 8: RS485_B (duplicato)
   - **NOTA**: Se la Battery Queen usa CAN per BMS, i pin RS485 (1,2) sono LIBERI
   - Puo' essere usata contemporaneamente per CAN (batteria) e RS485 (monitoraggio)

3. **Porta Meter-485** (porta RJ45) - per energy meter esterno
   - Pin 1: METER-485_B, Pin 2: METER-485_A
   - Pin 6: GND
   - Pin 7: METER-485_A (duplicato), Pin 8: METER-485_B (duplicato)
   - **Disponibile** se non c'e' un energy meter collegato (attualmente Meter Select = No Meter)

### Opzione consigliata: Porta Meter-485

Dato che `Meter Select = No Meter` nella configurazione attuale, la porta Meter-485 e' completamente libera e puo' essere usata per collegare un gateway Modbus esterno senza conflitti.

### Hardware: Elfin EW11A

L'Elfin EW11A e' un gateway compatto RS485-to-WiFi con supporto Modbus TCP:
- Alimentazione: 5-36V DC (l'EW11 base richiede 5-18V DC)
- Connettore: RJ45 con pin RS485 A, B e alimentazione
- Protocollo: Modbus RTU <-> Modbus TCP bridge
- Interfaccia web per configurazione
- Prezzo: 15-25 EUR (Amazon, AliExpress, eBay)

### Passi pratici

1. **Acquistare l'hardware**
   - Elfin EW11A (~20 EUR) - versione A per range alimentazione piu' ampio
   - Cavo RJ45 (incluso di solito, oppure un cavo ethernet standard)
   - Alimentatore 5V USB (o derivare l'alimentazione dall'inverter se possibile)

2. **Preparare il cavo RJ45**
   - Crimpare un cavo RJ45 con solo i pin necessari:
     - Pin 1 (RS485_B del Meter-485) -> Pin B dell'EW11
     - Pin 2 (RS485_A del Meter-485) -> Pin A dell'EW11
     - Pin 6 (GND) -> GND dell'EW11
   - Oppure tagliare un cavo ethernet e collegare i fili corrispondenti ai morsetti dell'EW11
   - **ATTENZIONE**: verificare con un multimetro la corrispondenza dei pin prima di collegare

3. **Collegare fisicamente**
   - Inserire il cavo RJ45 nella porta Meter-485 dell'inverter Deye (pannello inferiore)
   - Collegare l'altro estremo all'Elfin EW11A
   - Alimentare l'EW11A con un alimentatore USB 5V

4. **Configurare l'Elfin EW11**
   - Connettersi all'AP WiFi dell'EW11 (HF-EW11_xxxx)
   - Accedere alla web interface (10.10.100.254)
   - Configurare WiFi: connettere alla rete domestica (SSID: Akasha)
   - Configurare seriale:
     - Baud rate: 9600
     - Data bits: 8
     - Parity: None
     - Stop bits: 1
   - Configurare rete:
     - Protocollo: Modbus TCP
     - Porta: 8899 (o 502)
     - Modalita': TCP Server
   - Salvare e riavviare

5. **Configurare Home Assistant**

   **Opzione A: Integrazione Modbus nativa HA**
   Aggiungere in `configuration.yaml`:
   ```yaml
   modbus:
     - name: deye_inverter
       type: tcp
       host: <IP_ELFIN_EW11>
       port: 8899
       sensors:
         - name: "Deye Battery SOC"
           slave: 1
           address: 588
           input_type: holding
           data_type: uint16
           unit_of_measurement: "%"
         - name: "Deye PV Power"
           slave: 1
           address: 672
           input_type: holding
           data_type: uint16
           unit_of_measurement: "W"
         # ... altri registri dal Modbus map Deye
   ```

   **Opzione B: Integrazione ha-solarman (David Rapan)**
   - Installare da HACS
   - Configurare con IP dell'EW11, porta, e serial number inverter
   - Selezionare profilo Deye SG04LP3 (mappa registri predefinita)
   - Vantaggi: profilo completo con tutti i sensori gia' mappati

6. **Verificare la comunicazione**
   - Controllare in HA che i sensori mostrino valori
   - In caso di errori, verificare:
     - Polarita' A/B dei cavi RS485
     - Slave ID (default: 1 per Deye)
     - Baud rate (9600)

### Conflitti con lo stick logger

- **Nessun conflitto**: lo stick logger usa la porta WiFi/COM (connettore proprietario), mentre il gateway RS485 usa la porta Meter-485 (RJ45). Sono porte fisicamente separate.
- Lo stick logger continua a funzionare e a caricare dati al cloud Solarman.
- L'accesso Modbus via EW11 e il cloud Solarman coesistono senza problemi.

### Valutazione

| Criterio | Valore |
|---|---|
| **Hardware necessario** | Elfin EW11A + cavo RJ45 + alimentatore USB |
| **Costo** | 20-30 EUR |
| **Complessita'** | Media - cablaggio fisico + configurazione EW11 + configurazione HA |
| **Affidabilita'** | **Alta** - connessione Modbus diretta, nessuna dipendenza cloud o firmware logger |
| **Latenza dati** | **< 5 secondi** - polling Modbus diretto in tempo reale |
| **Mantiene cloud** | **Si** - lo stick logger continua a funzionare indipendentemente |
| **Scrittura registri** | **Si** - Modbus permette sia lettura che scrittura dei registri dell'inverter |
| **Rischio** | Basso - nessuna modifica software, facilmente reversibile |

---

## Confronto Riepilogativo

| Criterio | Solarman API | DNS Redirect | RS485 (EW11) | **Deye Cloud** ★ |
|---|---|---|---|---|
| Costo | Gratuito | Gratuito* | 20-30 EUR | **Gratuito** |
| Complessita' setup | Bassa | Alta | Media | **Bassa** |
| Credenziali | Email richiesta | N/A | N/A | **Self-service** |
| Affidabilita' | Media | Bassa | **Alta** | Media |
| Latenza dati | 5-15 min | 1-5 min | **< 5 sec** | 5-15 min |
| Cloud mantenuto | Si | **No** | **Si** | Si |
| Scrittura registri | No | No | **Si** | Parziale |
| Dipendenza esterna | Cloud Solarman | DNS/firmware | Nessuna | Cloud Deye |
| Accesso fisico | No | No | Si (una tantum) | No |

*Richiede Pi-hole/AdGuard se il router non supporta DNS override

---

## Raccomandazione

### Opzione consigliata: **Opzione 3 - Gateway RS485 (Elfin EW11A)** sulla porta Meter-485

Motivazioni:

1. **Affidabilita' massima**: connessione Modbus diretta all'inverter, nessuna dipendenza da cloud, DNS o firmware del logger
2. **Latenza minima**: dati in tempo reale con polling ogni pochi secondi, fondamentale per automazioni energetiche intelligenti
3. **Scrittura registri**: unica opzione che permette di CONTROLLARE l'inverter da HA (es. cambiare modalita', SOC target, fasce orarie) - essenziale per ottimizzazione energetica
4. **Nessun conflitto**: usa la porta Meter-485 libera, lo stick logger continua a funzionare
5. **Costo contenuto**: 20-30 EUR una tantum
6. **Facilmente reversibile**: basta scollegare il cavo RJ45

### Strategia suggerita: Approccio a due fasi

**Fase 1 (immediata)**: Usare la **Deye Cloud API** (Opzione 4, self-service) per avere subito i dati in HA.

**Fase 2 (appena arriva l'hardware)**: Installare l'Elfin EW11A sulla porta Meter-485 per dati real-time e controllo bidirezionale.

---

## Opzione 4: Deye Cloud API (Self-Service) ★ NUOVA

> Aggiunta: 2026-02-25

### Descrizione
Deye ha un portale sviluppatori **self-service** dove si possono ottenere AppId e AppSecret direttamente, senza dover inviare email. I dati passano dal logger al cloud Solarman → sincronizzati su Deye Cloud → recuperati via API REST.

### Portale sviluppatori
- **Registrazione/Login**: https://www.deyecloud.com/login
- **Creazione app**: https://developer.deyecloud.com/app
- **Documentazione API**: https://developer.deyecloud.com/api
- **Sample code Python**: https://github.com/DeyeCloudDevelopers/deye-openapi-client-sample-code
- **Supporto**: cloudservice@deye.com.cn

### API endpoints (regione EU)
- **Base URL**: `https://eu1-developer.deyecloud.com/v1.0`
- **Autenticazione**: `POST /account/token?appId={appId}`
- **Lista stazioni**: `POST /station/list`
- **Dati stazione**: `POST /station/latest`
- **Lista dispositivi**: `POST /device/list`
- **Dati dispositivo real-time**: `POST /device/latest`
- **Dati storici**: `POST /device/history`
- **Punti di misura**: `POST /device/measure/point`
- **Controllo inverter**: endpoint sotto `/commission/`

### Autenticazione
```
POST /account/token?appId={appId}
{
  "appSecret": "<appsecret>",
  "email": "<email>",
  "password": "<sha256_hash_password>",
  "companyId": "0"
}
→ response contiene access_token (durata: 2 ore)
→ usare header: Authorization: bearer <token>
```

### Script Python
Disponibile in `scripts/deye_cloud.py`:
```bash
# Setup: compilare .env con DEYE_APPID, DEYE_APPSECRET, DEYE_EMAIL, DEYE_PASSWORD
python3 scripts/deye_cloud.py --discover     # Scopri stazioni e dispositivi
python3 scripts/deye_cloud.py               # Dati real-time inverter
python3 scripts/deye_cloud.py --json-flat   # Output per HA command_line
python3 scripts/deye_cloud.py --loop 300    # Loop continuo ogni 5 min
```

### Integrazione con HA
I dati possono essere integrati in HA tramite:
1. **command_line sensor** - Lo script Python gira come sensore periodico
2. **REST sensor** - Usando i dati API direttamente
3. **MQTT** - Lo script pubblica su broker MQTT

### Valutazione

| Criterio | Valore |
|---|---|
| **Hardware necessario** | Nessuno |
| **Costo** | Gratuito |
| **Complessita'** | **Bassa** - self-service, credenziali immediate |
| **Affidabilita'** | Media - dipende dal cloud Deye |
| **Latenza dati** | 5-15 minuti |
| **Mantiene cloud** | Si |
| **Scrittura registri** | **Parziale** - API di commissioning disponibili |
| **Rischio** | Basso |

### Vantaggio rispetto a Opzione 1 (Solarman API)
- **Credenziali self-service**: non serve inviare email, si ottengono dal portale sviluppatori
- **API di controllo**: endpoints di commissioning per controllare l'inverter
- **Documentazione ufficiale**: portale sviluppatori con sample code Python

---

## Nota sulla porta Meter-485 e il meter esterno

La porta Meter-485 e' attualmente libera (`Meter Select = No Meter`). Se in futuro si decidesse di installare un meter esterno (es. DTSU666 per misurare i flussi al POD), questa porta sarebbe necessaria per il meter. In quel caso:
- L'EW11 andrebbe spostato sulla porta BMS/RS485 (pin 1,2 - liberi se la batteria usa CAN)
- Oppure usare un bus RS485 condiviso (il Modbus RTU supporta piu' dispositivi sullo stesso bus, con slave ID diversi)

Questo e' un punto da coordinare con l'electrical-engineer quando si pianifica l'installazione del meter.
