# Architettura Impianto Pedemonte

> Ultimo aggiornamento: 2026-02-22

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
                    │   SE10K-RWS     │        ┌──────────────┐
                    │  (produzione)   │───AC──▶│  Rete (POD)  │
                    └────────┬────────┘        └──────┬───────┘
                             │ AC                     │ AC
                             ▼                        ▼
                    ┌─────────────────┐        ┌──────────────┐
                    │   Deye 12K      │◀──AC──▶│  Contatore   │
                    │  SG04LP3-EU     │        │  Enel        │
                    │  (batteria +    │        └──────────────┘
                    │   backup)       │
                    └──┬──────────┬───┘
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
- Vede il SolarEdge come micro-inverter (SmartLoad = MicInv Input)
- Modalità: Selling First con Load First
- Monitoraggio cloud tramite stick logger LSW-3-C + Solarman

### Stick Logger LSW-3-C → Monitoraggio Deye
- Modello: Deye LSW-3-C
- Collegato all'inverter Deye via porta COM (RS232/RS485)
- Connessione WiFi 2.4GHz alla rete domestica
- Invia dati al cloud Solarman (SolarmanSmart)
- App mobile + portale web per monitoraggio real-time
- Memoria interna 2MB per logging (intervallo 1-15 min)
- Alimentato direttamente dall'inverter (plug-and-play)
- Protocollo Modbus per integrazione con Home Assistant

### Battery Queen 51.2V 314Ah → Accumulo
- Collegata al Deye via DC (protocollo BMS - CAN o RS485)
- Capacità: ~16 kWh
- Fornisce energia alla casa di notte e durante i blackout

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

### Blackout
1. Il Deye si scollega dalla rete (ATS)
2. La batteria alimenta la casa
3. Se c'è sole, il SolarEdge può continuare a produrre (se il Deye mantiene la frequenza)
4. La batteria si scarica fino al Batt Shutdown % (10%), poi il Deye si spegne

## Implicazioni per la Configurazione

1. **Meter Select = No Meter** sul Deye è un problema: senza meter al POD, il Deye non sa quanta energia il SolarEdge sta producendo/immettendo. Le funzioni Selling First e Zero Export non possono funzionare correttamente.

2. **SmartLoad = MicInv Input** è corretto: il Deye tratta l'input AC dal SolarEdge come un micro-inverter.

3. **La casa sul backup** significa che in caso di blackout TUTTA la casa perde corrente se la batteria si esaurisce. La riserva di backup (Batt Low 20%) è quindi ancora più importante.

4. **Il SolarEdge non ha batteria**: tutta la gestione energetica (accumulo, backup, time shifting) dipende esclusivamente dal Deye.

## Problemi Aperti

1. **Meter al POD**: serve un meter (es. DTSU666 Deye) al punto di consegna per misurare i flussi reali rete↔casa
2. **Coordinamento SolarEdge-Deye**: verificare che il SolarEdge continui a produrre correttamente quando il Deye è in backup mode
3. **Grid Code**: il Deye è su "General Standard" invece di CEI 0-21
4. **Configurazione SolarEdge**: da esportare e documentare (profilo StorEdge, limiti export, ecc.)
