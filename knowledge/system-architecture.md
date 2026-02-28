# Architettura Impianto Pedemonte

> Ultimo aggiornamento: 2026-02-28 (aggiunto monitoraggio Deye Cloud API in HA)

## Schema Generale

```
                    ┌─────────────────┐
                    │  Pannelli PV    │
                    │  (stringhe con  │
                    │  ottimizzatori) │
                    └────────┬────────┘
                             │ DC
                             ▼
                    ┌─────────────────┐
                    │   SolarEdge     │
                    │   SE10K-RWS     │
                    │  (produzione)   │
                    └────────┬────────┘
                             │ AC
                             ▼
         ┌──────────────┐   Ingresso "contatore"   ┌──────────────┐
         │  Contatore   │◀──────AC──────▶┌─────────────────┐      │
         │  Enel (POD)  │               │   Deye 12K      │      │
         └──────────────┘    Rete AC ──▶│  SG04LP3-EU     │      │
                                        │  (batteria +    │      │
                                        │   backup)       │      │
                                        └──┬──────────┬───┘      │
                                           │ DC      │ AC (Backup)
                                           ▼         ▼
                                  ┌──────────────┐  ┌──────────────┐
                                  │ Battery Queen│  │    Casa      │
                                  │ 51.2V 314Ah │  │  (carichi)   │
                                  │  ~16 kWh    │  │              │
                                  └──────────────┘  └──────────────┘

                    ┌─────────────────┐
                    │  Stick Logger   │
                    │  LSW-3-C        │──WiFi──▶ Solarman Cloud
                    │  (sul Deye)     │
                    └─────────────────┘

                    ┌─────────────────┐
                    │  SolarEdge      │
                    │  EV Charger     │──── Rete SolarEdge ──▶ SE10K-RWS
                    │  22kW (trifase) │
                    └─────────────────┘

NOTA: Il SolarEdge è collegato sull'ingresso "contatore" del Deye (lato grid),
NON come micro-inverter sul lato backup/load. Questo significa che in island
mode (blackout o stacco contatore), il SolarEdge perde il riferimento di rete
e si SPEGNE. La casa va solo a batteria.
Confermato dal test del 27/02/2026: staccando il contatore Enel, produzione
PV scende a zero e la casa funziona solo dalla batteria.
```

## Ruoli dei Componenti

### SolarEdge SE10K-RWS → Produzione PV
- Collegato ai pannelli solari tramite ottimizzatori
- Converte l'energia solare da DC ad AC
- Immette l'energia nella rete domestica
- **NON gestisce la batteria** (nessuna batteria collegata al SolarEdge)
- Monitoraggio a livello di pannello tramite ottimizzatori

### Deye SUN-12K-SG04LP3-EU → Batteria + Backup
- Collegato alla batteria Battery Queen 51.2V 314Ah
- Gestisce carica/scarica della batteria
- Fornisce backup alla casa tramite ATS integrato
- La casa è alimentata dall'uscita backup del Deye
- **Il SolarEdge è collegato sull'ingresso "contatore" del Deye (lato grid)** — confermato da Davide Duca
- In island mode (blackout), il SolarEdge si spegne e la casa va SOLO a batteria
- Modalità: Selling First con Load First
- Monitoraggio cloud tramite stick logger LSW-3-C + Solarman

### Stick Logger LSW-3-C → Monitoraggio Deye
- Modello: Deye LSW-3-C
- Collegato all'inverter Deye via porta COM (RS232/RS485)
- Connessione WiFi 2.4GHz alla rete domestica
- Invia dati al cloud Solarman (SolarmanSmart) → sincronizzati su Deye Cloud
- App mobile + portale web per monitoraggio real-time
- Memoria interna 2MB per logging (intervallo 1-15 min)
- Alimentato direttamente dall'inverter (plug-and-play)
- Modbus passthrough (porta 8899) NON funzionante su questo firmware

### Monitoraggio in Home Assistant (dal 2026-02-28)
- **SolarEdge**: integrazione nativa HA (real-time, ~15s)
- **Deye**: Deye Cloud API via `command_line` sensor (polling 5 min)
  - Script: `homeassistant/scripts/deye_cloud_sensor.py`
  - Credenziali: `/config/secrets.yaml`
  - ~75 datapoint per ogni poll (potenza, energia, batteria, temperature, tensioni per fase)
- **Energy Dashboard**: contatori hardware Deye (grid import/export, batteria) + Riemann sum SolarEdge (produzione PV)
- **Dashboard YAML**: `homeassistant/dashboards/overview.yaml` (mode: yaml, non editabile da UI)
- Dettagli sensori: `knowledge/homeassistant/deye-ha-integration-options.md`

### Battery Queen 51.2V 314Ah → Accumulo
- Collegata al Deye via DC (protocollo BMS - CAN o RS485)
- Capacità: ~16 kWh
- Fornisce energia alla casa di notte e durante i blackout

### SolarEdge EV Charger 22kW → Ricarica Auto Elettrica
- Wallbox trifase 22kW integrata nell'ecosistema SolarEdge
- Comunica con l'inverter SolarEdge per funzioni smart:
  - **Solar Boost**: carica con eccesso solare
  - **Monitoraggio integrato**: produzione PV in tempo reale
  - **Gestione dinamica**: limita la carica per non superare la potenza contrattuale
- Part Number: 8E-FVK22000-01
- Seriale: S03727-999019011-41
- **IMPORTANTE**: dipende dall'inverter SolarEdge per le funzioni smart. Senza SolarEdge diventa un caricatore "stupido". Questo e un motivo in piu per mantenere il SolarEdge (soluzione APS) invece di sostituirlo.

### Casa → Backup del Deye
- Tutti i carichi della casa sono sull'uscita backup del Deye
- In caso di blackout, il Deye alimenta la casa dalla batteria + PV
- Quando la rete è presente, la casa riceve energia da: batteria, PV (via SolarEdge→Deye), rete

## Flussi Energetici

### Giorno (con sole)
1. SolarEdge produce energia dai pannelli → AC
2. L'energia va alla casa (tramite Deye backup output)
3. L'eccesso carica la batteria (tramite Deye)
4. Ulteriore eccesso viene immesso in rete

### Notte (senza sole)
1. La batteria alimenta la casa (tramite Deye)
2. Quando la batteria raggiunge il Batt Low % (20%), il Deye passa alla rete
3. La rete alimenta la casa fino all'alba

### Blackout (VERIFICATO 27/02/2026)
1. Il Deye si scollega dalla rete (ATS)
2. La batteria alimenta la casa
3. ~~Se c'e sole, il SolarEdge puo continuare a produrre~~ **FALSO: il SolarEdge si SPEGNE** (anti-islanding CEI 0-21). Verificato con test reale di stacco contatore.
4. **La casa va SOLO a batteria** - nessuna produzione PV disponibile
5. La batteria si scarica fino al Batt Shutdown % (10%), poi il Deye si spegne
6. **Vedi analisi completa**: `knowledge/optimizations/island-mode-analysis.md`

## Implicazioni per la Configurazione

1. **Meter Select = No Meter** sul Deye è un problema: senza meter al POD, il Deye non sa quanta energia il SolarEdge sta producendo/immettendo. Le funzioni Selling First e Zero Export non possono funzionare correttamente.

2. **SmartLoad = MicInv Input** è corretto: il Deye tratta l'input AC dal SolarEdge come un micro-inverter.

3. **La casa sul backup** significa che in caso di blackout TUTTA la casa perde corrente se la batteria si esaurisce. La riserva di backup (Batt Low 20%) è quindi ancora più importante.

4. **Il SolarEdge non ha batteria**: tutta la gestione energetica (accumulo, backup, time shifting) dipende esclusivamente dal Deye.

## Problemi Aperti

1. **Meter al POD**: serve un meter (es. DTSU666 Deye) al punto di consegna per misurare i flussi reali rete-casa
2. **~~Coordinamento SolarEdge-Deye~~** → **RISOLTO (27/02/2026)**: il SolarEdge NON produce in backup mode. Anti-islanding CEI 0-21 non disabilitabile. Vedi `island-mode-analysis.md`
3. **Grid Code**: il Deye e su "General Standard" invece di CEI 0-21
4. **Configurazione SolarEdge**: da esportare e documentare (profilo StorEdge, limiti export, ecc.)
5. **NUOVO - PV in Island Mode**: nessuna produzione solare in blackout. Soluzioni proposte in `island-mode-analysis.md`: pannelli direttamente su MPPT Deye oppure sostituzione SolarEdge con Fronius
