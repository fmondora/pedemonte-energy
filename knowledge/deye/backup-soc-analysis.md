# Analisi: Gestione Backup e SOC Minimo sul Deye SUN-12K-SG04LP3-EU

> Data: 2026-02-22
> Autore: deye-expert
> Contesto: Commento di Davide Duca (installatore) sulla necessita di una riserva di backup

## 1. Come funziona il Backup Mode (ATS) sul Deye 12K

Il Deye SUN-12K-SG04LP3-EU e dotato di un ATS (Automatic Transfer Switch) integrato trifase. Quando la rete viene a mancare:

1. **L'ATS rileva la mancanza di rete** e scollega i carichi dalla rete
2. **L'inverter passa in modalita off-grid** (isola) e alimenta i carichi di backup dalle uscite "Backup"
3. **Il parametro "Backup Delay"** (attualmente 0s) controlla il ritardo prima dello switch - con 0s lo switch e quasi istantaneo (tipicamente <20ms per l'ATS integrato)
4. **I carichi vengono alimentati** dalla batteria e/o dal fotovoltaico

### Cosa succede se il SOC e troppo basso al momento del blackout

Questo e il punto critico sollevato da Davide:

- **Se SOC > Batt Low % (15%)**: L'inverter entra in backup normalmente e alimenta i carichi. La batteria si scarica fino al Batt Shutdown % (10%), poi l'inverter si spegne.
- **Se SOC e tra Batt Low (15%) e Batt Shutdown (10%)**: L'inverter puo ancora entrare in backup, ma ha pochissima energia disponibile. Con 340 Ah di batteria, il 5% corrisponde a circa 0.85 kWh - sufficienti per pochi minuti con carichi pesanti.
- **Se SOC <= Batt Shutdown (10%)**: L'inverter NON puo avviarsi in modalita backup. I carichi di backup restano senza alimentazione.
- **Se l'inverter si spegne per Batt Shutdown durante un blackout**: Per ripartire, il SOC deve raggiungere il **Batt Restart % (50%)**. Senza rete, l'unica fonte di ricarica e il fotovoltaico. Di notte, questo significa che l'inverter resta spento fino all'alba e fino a quando il solare non riporta il SOC al 50%.

**Questo e esattamente il problema descritto da Davide**: se il blackout avviene di notte con batteria scarica, l'impianto non riparte fino al giorno dopo.

## 2. Parametri che controllano la riserva di backup

### Gerarchia dei parametri di protezione batteria

Sul Deye SG04LP3, ci sono 4 soglie chiave (dalla piu alta alla piu bassa):

| Parametro | Valore Attuale | Funzione |
|---|---|---|
| **Batt Restart %** | 50% | SOC a cui l'inverter riprende a funzionare dopo uno shutdown. Richiede ricarica (solare o rete) |
| **Batt Low %** | 15% | Soglia di allarme + limite di scarica in on-grid (TOU/Self-Use). L'icona batteria diventa gialla. **In on-grid, la batteria smette di scaricarsi a questo livello** |
| **Batt Shutdown %** | 10% | L'inverter si spegne completamente per proteggere la batteria. **Questo e l'ultimo limite, sia on-grid che off-grid** |
| *(Batt Empty V)* | *(gestito dal BMS)* | Tensione minima assoluta delle celle |

### Come interagiscono con le diverse modalita

**On-Grid (rete presente)**:
- La batteria si scarica fino al valore **Batt %** della fascia TOU attiva (attualmente 10% per tutte le fasce)
- Ma non scende MAI sotto **Batt Low %** (15%)
- Quindi in pratica: la batteria si scarica fino al 15% e poi si ferma

**Off-Grid / Backup (rete assente)**:
- **Batt Low % non e un limite rigido in off-grid** - e un allarme
- La batteria continua a scaricarsi per alimentare i carichi di backup
- Lo stop effettivo avviene a **Batt Shutdown %** (10%)
- Dopo lo shutdown, serve raggiungere **Batt Restart % (50%)** per ripartire

### Parametro specifico per backup reserve: NON ESISTE nativamente

**Il Deye SG04LP3 NON ha un parametro separato "Backup Reserve"** come alcuni inverter concorrenti (es. Tesla Powerwall ha "Backup Reserve", SolarEdge ha "Backup Reserve SOC").

La riserva di backup sul Deye si ottiene indirettamente attraverso la combinazione di:
- **Batt Low %** = soglia a cui la batteria smette di scaricarsi in on-grid
- **Batt Shutdown %** = soglia di spegnimento assoluto
- **TOU Batt %** = soglia per-fascia nella programmazione Time of Use

## 3. Valutazione della proposta di Davide (35% backup, 10% SOC)

### Interpretazione della proposta

Davide propone: *"Tipo 35 soglia backup e 10 soc"*

Interpreto cosi:
- **Batt Low % = 35%** -> la batteria smette di scaricarsi in on-grid al 35%, riservando il 35% per eventuale backup
- **Batt Shutdown % = 10%** -> in caso di blackout, la batteria puo scaricarsi dal 35% al 10% = 25% di energia disponibile per il backup

### Analisi tecnica della proposta

**PRO:**
- Con 340 Ah a 48V nominali, il 25% di riserva corrisponde a circa **4.1 kWh** disponibili per il backup
- A 0.41 kW di consumo medio notturno, questo garantisce circa **10 ore di autonomia** in blackout
- Buon margine sopra il Batt Shutdown % per evitare lo scenario di "non riparte"

**CONTRO:**
- Il 35% di Batt Low % limita significativamente l'uso notturno della batteria
- Con la configurazione attuale (SOC inizio notte ~51%, come registrato il 22/02), si scaricherebbero solo 51%-35% = 16% = ~2.6 kWh prima di fermarsi
- Questo e praticamente la stessa situazione di prima della modifica di oggi
- Si perderebbe il beneficio dell'abbassamento a 15%

### La proposta e tecnicamente corretta ma eccessivamente conservativa

Davide ha ragione sul principio (serve una riserva), ma il 35% e troppo alto per questo impianto, considerando:
- Il SOC di inizio notte e spesso intorno al 50-60% (in inverno)
- Con Batt Low al 35%, resta pochissimo margine per l'uso notturno quotidiano
- I blackout in Italia sono relativamente rari e generalmente brevi (<1-2 ore)

## 4. Raccomandazione: Bilanciamento tra uso notturno e riserva backup

### Opzione A: Configurazione Conservativa (priorita backup)

| Parametro | Valore | Note |
|---|---|---|
| Batt Low % | 25% | Riserva di backup |
| Batt Shutdown % | 10% | Protezione batteria |
| Batt Restart % | 50% | Riavvio dopo shutdown |
| TOU Batt % (tutte le fasce) | 25% | Coerente con Batt Low |

- Energia disponibile per uso notturno: 100% - 25% = 75% = ~12.4 kWh
- Energia riserva backup: 25% - 10% = 15% = ~2.5 kWh
- Autonomia backup a 0.41 kW: ~6 ore

### Opzione B: Configurazione Bilanciata (RACCOMANDATA)

| Parametro | Valore | Note |
|---|---|---|
| Batt Low % | 20% | Riserva di backup ragionevole |
| Batt Shutdown % | 10% | Protezione batteria |
| Batt Restart % | 40% | Abbassato per ripartenza piu rapida |
| TOU Batt % (tutte le fasce) | 20% | Coerente con Batt Low |

- Energia disponibile per uso notturno: 100% - 20% = 80% = ~13.2 kWh
- Energia riserva backup: 20% - 10% = 10% = ~1.65 kWh
- Autonomia backup a 0.41 kW: ~4 ore
- Buon compromesso tra uso quotidiano e resilienza

### Opzione C: Configurazione Aggressiva (priorita autoconsumo)

| Parametro | Valore | Note |
|---|---|---|
| Batt Low % | 15% | Come impostato oggi |
| Batt Shutdown % | 10% | Protezione batteria |
| Batt Restart % | 50% | Standard |
| TOU Batt % (tutte le fasce) | 10% | Massimo utilizzo |

- Energia disponibile per uso notturno: 100% - 15% = 85% = ~14 kWh
- Energia riserva backup: 15% - 10% = 5% = **solo ~0.85 kWh**
- Autonomia backup a 0.41 kW: **solo ~2 ore**
- Rischio: se il blackout dura piu di 2 ore di notte, l'inverter si spegne e non riparte fino all'alba

### Opzione raccomandata e motivazione

**Raccomando l'Opzione B (Batt Low % = 20%)** per i seguenti motivi:

1. **4 ore di autonomia backup** coprono la stragrande maggioranza dei blackout in Italia (>95% durano meno di 4 ore)
2. **80% di capacita utilizzabile** per l'autoconsumo notturno e un ottimo compromesso
3. **Batt Restart a 40%** (anziche 50%) permette un riavvio piu rapido dopo uno shutdown - basta meno sole al mattino per ripartire
4. Il margine di 10% (20% -> 10%) e sufficiente per gestire carichi di picco durante il backup senza arrivare subito allo shutdown

### Confronto visivo delle opzioni

```
SOC %  Proposta Davide  Opz A (Conserv.)  Opz B (RACCOMANDATA)  Opz C (Aggressiva)  Attuale
100% |----- uso -----|----- uso -----|----- uso ----------|----- uso ---------|----- uso -----
 50% |               |               |                    |                   |
 35% |-- STOP ON-G --|               |                    |                   |
 25% |  riserva bkp  |-- STOP ON-G --|                    |                   |
 20% |               |  riserva bkp  |-- STOP ON-GRID ----|                   |
 15% |               |               |  riserva backup    |-- STOP ON-GRID --|-- STOP ON-G --
 10% |== SHUTDOWN ===|== SHUTDOWN ===|== SHUTDOWN ========|== SHUTDOWN ======|== SHUTDOWN ===
  0% |               |               |                    |                   |
```

## 5. Note aggiuntive importanti

### Batt Restart % - parametro spesso trascurato

Il valore attuale di **50%** e piuttosto alto. Significa che dopo uno shutdown in backup:
- L'inverter non ripartira finche il SOC non raggiunge il 50%
- In inverno con poco sole, potrebbero servire diverse ore
- **Suggerisco di abbassarlo a 40%** per accelerare il riavvio
- Non scendere sotto il 30% per evitare cicli di on/off ripetuti

### SmartLoad vs Backup Load

Nella configurazione attuale, il SmartLoad e configurato come "MicInv Input" con soglie ON 65% / OFF 70%. Questo e separato dal backup e non influenza direttamente la gestione della riserva di backup. I carichi critici devono essere collegati alle uscite di backup dell'inverter, non allo SmartLoad.

### Grid Charge come alternativa stagionale

In inverno, quando la produzione solare e bassa e il SOC di inizio notte e spesso <60%, si potrebbe considerare di attivare **Grid Charge** nelle ore F3 (23-07) per mantenere un SOC minimo del 30-40%. Questo garantirebbe sempre una buona riserva di backup senza sacrificare l'uso notturno. Tuttavia, questo richiede un'analisi costi/benefici sull'energia acquistata dalla rete.

## Fonti

- [Manuale Deye SUN-5-12K-SG04LP3-EU](https://www.deyeinverter.com/deyeinverter/2024/02/03/instructions_sun-5-12k-sg04lp3-eu_240203_en.pdf)
- [DIY Solar Forum - Deye Battery Settings](https://diysolarforum.com/threads/deye-5kw-hybrid-inverter-battery-settings-low-batt-shutdown-restart-batt-empty.74144/)
- [DIY Solar Forum - Deye Backup Loads 12K](https://diysolarforum.com/threads/backup-loads-only-on-deye-hybrid-inverter-3-phase-12k-inverter-sun-12k-sg04lp3-eu-wifi.82668/)
- [DIY Solar Forum - Taming Deye Hybrid Inverters](https://diysolarforum.com/threads/taming-the-deye-hybrid-inverters.106234/)
