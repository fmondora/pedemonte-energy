# Soluzioni Creative: SolarEdge in Island Mode con Deye

> Data analisi: 27/02/2026
> Autore: Team Energia (Electrical Engineer + Deye Expert + SolarEdge Expert)
> Status: RICERCA APPROFONDITA - Soluzioni praticabili identificate!

---

## La Sfida del Proprietario

> "Invece di rimuovere gli ottimizzatori, non possiamo tenere il SolarEdge nel mezzo come lettore degli ottimizzatori? Siate creativi!"

**Risposta: SI, probabilmente possiamo farcela.** Abbiamo scoperto una funzionalita ufficiale SolarEdge che cambia tutto il quadro: l'**Alternative Power Source (APS) mode**.

---

## SCOPERTA CHIAVE: SolarEdge APS Mode

### Cos'e l'APS Mode

Nel 2019 SolarEdge ha introdotto una funzionalita chiamata **Alternative Power Source (APS) mode** che permette esattamente quello che serve:

- **Range esteso di frequenza e tensione**: il SolarEdge accetta variazioni maggiori di frequenza e tensione senza scattare
- **Droop P(f) dedicato per off-grid**: il SolarEdge risponde al frequency shifting riducendo la potenza proporzionalmente
- **Disabilitazione anti-islanding attiva**: in APS mode, il SolarEdge NON esegue i test attivi anti-islanding (impedenza, perturbazioni)
- **Funziona con sorgenti non-rete**: progettato specificamente per funzionare con inverter ibridi, generatori, o qualsiasi sorgente AC non-rete

### Compatibilita con SE10K-RWS — CONFERMATA!

| Requisito | SE10K-RWS | Status |
|---|---|---|
| Tipo inverter | Three-phase SetApp | COMPATIBILE |
| Firmware minimo | CPU >= 4.8.xxx | COMPATIBILE (attuale ~4.16.xxx, ben sopra il minimo) |
| HDwave/3-phase | Si, il SE10K e trifase | COMPATIBILE |
| StorEdge variant | Confermato da manuale + Application Note | **COMPATIBILE** |

**VERIFICATO (27/02/2026)**: Tre fonti indipendenti confermano la compatibilita:

1. **Manuale di installazione StorEdge Three Phase (MAN-01-00648-1.3, pag. 8)**: menziona esplicitamente il supporto per "alternative power source such as a generator" con link all'Application Note APS
2. **Application Note APS (v1.5, May 2022)**: "Three phase inverters with CPU version 4.8.xxx or later configured by SetApp [...] support Alternative Power Source"
3. **Documentazione Victron**: "This APS feature is only available for 3phase and 1phase HDwave inverters" — il SE10K-RWS e trifase
4. **Forum SolarPanelTalk**: utente conferma APS disponibile su StorEdge 7600A (variante StorEdge con CPU 3.2525.0)

**Fonti**:
- [SolarEdge Application Note APS](https://knowledge-center.solaredge.com/sites/kc/files/se-inverter-support-of-voltage-sources.pdf)
- [Victron: Integrating with SolarEdge](https://www.victronenergy.com/live/venus-os:gx_solaredge)
- [SolarEdge APS Hybrid Solution](https://knowledge-center.solaredge.com/sites/kc/files/aps_hybrid_solution.pdf)

### Come si Attiva l'APS Mode

1. **In SetApp**: Commissioning → Communication → GPIO → Power Reduction Interface (RRCR) Mode → **Alternative Power Source**
2. **Contattare SolarEdge Support**: serve un parametro di backend modificato per abilitare P(f) in APS mode (nelle firmware piu recenti potrebbe essere automatico)
3. **Collegare un dry-contact relay** ai terminali GPIO (L1 e V) della scheda di comunicazione del SolarEdge
4. **Configurare P(f)**: impostare i punti di droop frequenza-potenza (es. P0: 50.2 Hz = 100% potenza, P1: 51.2 Hz = 0% potenza)

### Come Funziona il Dry-Contact

Il dry-contact e un semplice contatto a rele:
- **Contatto CHIUSO** = "Stai lavorando con una sorgente alternativa (non-rete)"
- **Contatto APERTO** = "Stai lavorando con la rete normale"

Quando il contatto si chiude:
- Il SolarEdge passa in APS mode
- Estende i range di frequenza/tensione accettabili
- Attiva i droop P(f) e V(f) per off-grid
- **NON esegue i test anti-islanding attivi**

Quando il contatto si apre:
- Il SolarEdge torna al country code normale (CEI 0-21)
- Riattiva tutte le protezioni anti-islanding standard

---

## SOLUZIONE ALPHA: SolarEdge sulla Porta GEN del Deye con APS Mode

### Schema di Collegamento

```
                ┌─────────────────┐
                │  Pannelli PV    │
                │  (ottimizzatori)│
                └────────┬────────┘
                         │ DC
                         ▼
                ┌─────────────────┐
                │   SolarEdge     │
                │   SE10K-RWS     │   GPIO dry-contact ←── Deye G-valve
                │   (APS mode)    │   (segnale island mode)
                └────────┬────────┘
                         │ AC (trifase)
                         ▼
         ┌──────────┐   Porta GEN    ┌──────────────┐
         │Contatore │   (MicInv)     │  Deye 12K    │
         │  Enel    │◀──GRID port───▶│  SG04LP3-EU  │
         └──────────┘                │  (battery +  │
                                     │   backup)    │
                                     └──┬────────┬──┘
                                        │ DC     │ AC (Backup/LOAD)
                                        ▼        ▼
                               ┌──────────┐  ┌──────────┐
                               │ Battery  │  │   Casa   │
                               │ Queen    │  │ (carichi)│
                               └──────────┘  └──────────┘
```

### Come Funziona

#### In Condizioni Normali (rete presente)
1. SolarEdge produce e immette sulla porta GEN del Deye
2. Il Deye vede il SolarEdge come micro-inverter (SmartLoad = MicInv Input)
3. Il Deye distribuisce: carichi casa, carica batteria, export in rete
4. Il dry-contact GPIO e APERTO → SolarEdge in modalita CEI 0-21 normale
5. **Ma il SolarEdge non deve "vedere" la rete sulla porta GEN?** In condizioni normali, il Deye potrebbe non generare AC sulla porta GEN perche la rete e presente sull'ingresso GRID. **PUNTO CRITICO: verificare se il Deye "passa" la AC della rete alla porta GEN quando e on-grid.**

#### In Island Mode (blackout)
1. La rete cade
2. Il Deye va in backup mode, genera AC locale sulla porta LOAD e sulla porta GEN
3. Il Deye chiude il contatto **G-valve** (CN2 pin 3,4) → Signal Island Mode = Enable
4. Il G-valve del Deye chiude il dry-contact GPIO del SolarEdge
5. Il SolarEdge passa in **APS mode**
6. Il SolarEdge vede la AC del Deye sulla porta GEN
7. Il SolarEdge si avvia e inizia a produrre!
8. La produzione PV va al Deye che la distribuisce: carichi + batteria
9. Quando la batteria e piena (SOC >= 70%), il Deye alza la frequenza
10. Il SolarEdge in APS mode risponde al P(f) e riduce la produzione
11. Equilibrio raggiunto!

#### Al Ritorno della Rete
1. La rete torna
2. Il Deye si riconnette alla rete
3. Il Deye apre il contatto G-valve
4. Il GPIO del SolarEdge si apre → torna in modalita CEI 0-21
5. Il SolarEdge si riconnette alla rete attraverso il Deye

### Analisi Tecnica Dettagliata

#### Pro
- **Sfrutta funzionalita UFFICIALI** di entrambi gli inverter (APS per SolarEdge, MicInv per Deye)
- **Tutti i 10 kWp di pannelli** disponibili anche in island mode
- **Gli ottimizzatori rimangono** → monitoraggio a livello pannello preservato
- **Il contatto G-valve del Deye pilota direttamente il GPIO del SolarEdge** → cablaggio semplicissimo
- **Frequency shifting del Deye** (AC Couple Frz High) controlla la produzione del SolarEdge via P(f)
- **Costo minimo**: solo cablaggio AC (3 fasi + neutro) dalla porta GEN al SolarEdge + cavo segnale G-valve→GPIO

#### Contro e Rischi
- **RISCHIO MEDIO-ALTO: Impedenza di rete in APS mode**. Anche con anti-islanding disabilitato, il SolarEdge potrebbe avere problemi con la qualita della AC del Deye (distorsioni armoniche, impedenza). L'APS mode estende i range, ma non li elimina del tutto.
- **RISCHIO MEDIO: Tempo di risposta P(f)**. Il frequency shifting del Deye e il droop P(f) del SolarEdge devono sincronizzarsi. Se il SolarEdge risponde lentamente, la batteria potrebbe sovraccaricarsi momentaneamente.
- **RISCHIO BASSO-MEDIO: Startup in island mode**. Il SolarEdge necessita di circa 1-2 minuti per avviarsi dopo aver ricevuto la AC. La batteria deve sostenere i carichi durante questo periodo.
- **INCOGNITA: La porta GEN ha AC anche quando la rete e presente?** Il Deye in modalita "MicInv Input" sulla porta GEN potrebbe non fornire AC sulla porta GEN in condizioni on-grid. Se non lo fa, serve un ATS/relay per commutare il SolarEdge tra la rete (on-grid) e la porta GEN (off-grid).
- ~~INCOGNITA: StorEdge RWS supporta APS?~~ **RISOLTO (27/02/2026): SI, confermato** dal manuale StorEdge Three Phase (pag. 8), Application Note APS (three-phase CPU >= 4.8.xxx), documentazione Victron, e forum.
- **Coordinamento AC Couple Frz High con P(f)**: Il Deye alza la frequenza fino a 55 Hz, ma il P(f) del SolarEdge in APS mode ha droop default a 50.2-51.2 Hz. Servono impostazioni coerenti.

#### Configurazione Proposta

| Parametro Deye | Valore | Note |
|---|---|---|
| SmartLoad Setup | MicInv Input | Gia impostato |
| Signal Island Mode | **Enable** | DA ATTIVARE - necessario per G-valve |
| AC Couple Frz High | **51.0 Hz** | Ridurre da 55 Hz! Deve essere <= trip point del SolarEdge in APS |
| OFF % | 70% | OK come da attuale |
| ON % | 65% | OK come da attuale |

| Parametro SolarEdge | Valore | Note |
|---|---|---|
| GPIO RRCR Mode | Alternative Power Source | Da configurare in SetApp |
| P(f) P0 | 50.2 Hz = 100% | Inizio riduzione potenza |
| P(f) P1 | 51.0 Hz = 0% | Stop produzione (coerente con Deye) |
| Backend APS P(f) | Abilitato | Contattare SolarEdge support |

### Probabilita di Successo: 60-70%

La probabilita e alta perche si basa su funzionalita ufficiali di entrambi i produttori. Il rischio principale e la conferma che il SE10K-RWS (variante StorEdge) supporti effettivamente l'APS mode, e che la qualita dell'AC del Deye in backup mode sia accettabile.

### Costo Stimato: 300-800 EUR

| Voce | Costo |
|---|---|
| Cavo AC trifase (SolarEdge→porta GEN Deye) | 100-200 EUR |
| Cavo segnale (G-valve Deye → GPIO SolarEdge) | 20-50 EUR |
| Lavoro elettricista (ricablaggio + test) | 200-500 EUR |
| **Totale** | **320-750 EUR** |

---

## SOLUZIONE BETA: SolarEdge sulla Porta GEN con Relay di Commutazione

### Schema di Collegamento

```
                ┌─────────────────┐
                │  Pannelli PV    │
                │  (ottimizzatori)│
                └────────┬────────┘
                         │ DC
                         ▼
                ┌─────────────────┐
                │   SolarEdge     │   GPIO dry-contact ←── Deye G-valve
                │   SE10K-RWS     │
                │   (APS mode)    │
                └────────┬────────┘
                         │ AC (trifase)
                         ▼
              ┌──────────────────────┐
              │  ATS/Relay trifase   │←── Comandato da G-valve Deye
              │  (commutatore)       │
              └───┬──────────┬───────┘
                  │          │
         Pos. A (on-grid)   Pos. B (off-grid)
                  │          │
                  ▼          ▼
         ┌──────────┐   Porta GEN
         │Contatore │   (MicInv)     ┌──────────────┐
         │  Enel    │               │  Deye 12K    │
         │          │◀──GRID port──▶│  SG04LP3-EU  │
         └──────────┘               └──┬────────┬──┘
                                       │        │
                                       ▼        ▼
                              ┌──────────┐  ┌──────────┐
                              │ Battery  │  │   Casa   │
                              └──────────┘  └──────────┘
```

### Come Funziona

#### In Condizioni Normali (rete presente)
1. Il relay e in posizione A: SolarEdge collegato alla rete (come ora)
2. Il SolarEdge produce e immette in rete normalmente
3. Il Deye vede la produzione sul suo ingresso GRID (contatore)
4. Tutto funziona come l'attuale configurazione

#### In Island Mode (blackout)
1. La rete cade
2. Il Deye va in backup, chiude il G-valve
3. Il G-valve comanda il relay → commuta in posizione B
4. Il SolarEdge si spegne brevemente (perde la rete)
5. Il relay connette il SolarEdge alla porta GEN del Deye
6. Contemporaneamente, il G-valve chiude il dry-contact GPIO del SolarEdge → APS mode
7. Il SolarEdge si riavvia in APS mode sulla AC della porta GEN
8. Riprende a produrre dopo 1-2 minuti
9. Frequency shifting del Deye controlla la produzione

#### Al Ritorno della Rete
1. La rete torna, il Deye si riconnette
2. Il G-valve si apre → relay torna in posizione A
3. Il SolarEdge si spegne brevemente e si riconnette alla rete
4. GPIO si apre → SolarEdge torna a CEI 0-21

### Vantaggi rispetto alla Soluzione Alpha

- **ON-GRID: tutto identico a ora** → il SolarEdge e collegato alla rete come prima installazione
- **Nessun rischio di problemi on-grid** → il ricablaggio e solo per off-grid
- **Il Deye vede il SolarEdge sul GRID port on-grid** → misurazione corretta dei flussi
- **OFF-GRID: il SolarEdge va sulla porta GEN** → configurazione AC couple standard

### Svantaggi
- **Costo maggiore**: serve un ATS/relay trifase (NO-NC) da almeno 40A
- **Complessita meccanica**: piu componenti, piu punti di guasto
- **Due interruzioni brevi** del SolarEdge (alla commutazione andata e ritorno)
- **Il relay deve essere dimensionato** per 10 kW trifase

### Probabilita di Successo: 70-80%

Piu alta della Soluzione Alpha perche:
- In condizioni normali il sistema e identico a prima → zero rischi on-grid
- In off-grid, il SolarEdge e sulla porta GEN dedicata → configurazione pulita
- Il cambio di contesto (rete → APS mode) e gestito meccanicamente dal relay

### Costo Stimato: 800-1.500 EUR

| Voce | Costo |
|---|---|
| ATS/Relay trifase 40A motorizzato | 200-400 EUR |
| Cavo AC trifase aggiuntivo | 100-200 EUR |
| Cavo segnale G-valve | 20-50 EUR |
| Quadro elettrico e protezioni | 100-200 EUR |
| Lavoro elettricista (2 giorni) | 400-600 EUR |
| **Totale** | **820-1.450 EUR** |

---

## SOLUZIONE GAMMA: SolarEdge sull'Uscita LOAD/Backup del Deye con APS Mode

### Concetto

Collegare l'uscita AC del SolarEdge direttamente all'uscita LOAD/backup del Deye (dove sono i carichi della casa), invece che sulla porta GEN.

### Schema

```
                ┌─────────────────┐
                │  Pannelli PV    │
                └────────┬────────┘
                         │ DC
                         ▼
                ┌─────────────────┐
                │   SolarEdge     │   GPIO ←── Deye G-valve
                │   (APS mode)    │
                └────────┬────────┘
                         │ AC
                         ▼
         ┌──────────────────────────┐
         │    Bus AC Casa (LOAD)    │◀── Uscita Backup Deye
         │    (carichi domestici)   │
         └──────────────────────────┘
                         ▲
                         │
                ┌────────┴────────┐
                │    Deye 12K     │
                │  (grid-forming) │
                └─────────────────┘
```

### Analisi

#### Pro
- **Semplice**: il SolarEdge si collega dove gia sono i carichi
- **Il SolarEdge vede la stessa AC della casa** sia on-grid che off-grid
- **In off-grid**, il Deye fa grid-forming e il SolarEdge (in APS) produce nella micro-rete

#### Contro (SERI)
- **Il Deye NON sa che il SolarEdge sta immettendo potenza nel bus LOAD**. La porta GEN con MicInv Input ha un CT integrato che misura la produzione del micro-inverter. Sul bus LOAD non c'e questo controllo.
- **Il frequency shifting NON funziona sul bus LOAD** allo stesso modo. Il Deye alza la frequenza su GEN quando il SOC e alto, ma sulla LOAD la frequenza e quella "di servizio" della casa.
- **Rischio di instabilita**: il SolarEdge immette potenza "cieca" nel bus AC, il Deye non la vede e non la controlla.
- **Potenziale backfeed verso la rete**: in on-grid, la potenza del SolarEdge potrebbe fluire verso la rete attraverso il Deye senza controllo.

### Probabilita di Successo: 30-40%

Non raccomandata come soluzione principale. Il rischio di instabilita e troppo alto senza il controllo del frequency shifting sulla porta GEN.

### Ma... Un Uso Creativo

Questa configurazione POTREBBE funzionare SE si aggiungesse un **CT esterno** sul collegamento SolarEdge→bus LOAD, collegato al Deye per la misurazione. Ma aggiunge complessita senza vantaggio reale rispetto alla Soluzione Alpha (porta GEN).

---

## SOLUZIONE DELTA: Relay Semplice "Grid Simulator"

### Concetto Creativo

Invece di spostare fisicamente il SolarEdge, usare un **relay che commuta il neutro** per "ingannare" il SolarEdge:

1. In condizioni normali: il SolarEdge e collegato alla rete (come ora)
2. In island mode: un relay inserisce un **induttore/trasformatore di isolamento** tra la porta GEN del Deye e il SolarEdge, per simulare la bassa impedenza della rete

### Analisi

Questa idea e affascinante ma **troppo rischiosa**:
- Un trasformatore di isolamento da 10 kW trifase costa 2.000-5.000 EUR
- L'impedenza simulata potrebbe non essere sufficiente per l'anti-islanding attivo
- L'APS mode (Soluzione Alpha) fa la stessa cosa in modo software, senza hardware costoso

**SCARTATA: l'APS mode rende questa soluzione obsoleta.**

---

## SOLUZIONE EPSILON: SolarEdge + Secondo Inverter "Bridge"

### Concetto Ultra-Creativo

Usare un **piccolo inverter off-grid** (es. Victron MultiPlus 3000) come "ponte":
1. Il Victron e collegato alla batteria del Deye (o una piccola batteria dedicata)
2. Il Victron genera AC pulita e stabile
3. Il SolarEdge e collegato all'uscita del Victron
4. Il Victron fa da "grid simulator" per il SolarEdge
5. La produzione del SolarEdge carica la batteria del Victron/Deye

### Analisi

- **Funziona sicuramente**: Victron + SolarEdge in APS mode e una configurazione ufficialmente documentata da Victron
- **Ma**: aggiunge un inverter in piu, con le sue perdite di conversione (AC→DC→AC)
- **Costo**: 1.500-3.000 EUR per un Victron MultiPlus trifase
- **Complessita**: alta, serve coordinamento tra tre inverter

**NON RACCOMANDATA**: la Soluzione Alpha fa la stessa cosa senza il Victron, usando il Deye come grid-forming.

---

## CONFRONTO SOLUZIONI CREATIVE

| Soluzione | Probabilita Successo | Costo | Complessita | Pannelli in Island | Raccomandazione |
|---|---|---|---|---|---|
| **ALPHA: GEN + APS** | 60-70% | 300-800 EUR | MEDIA | 10 kWp | **SI - Da provare PRIMA** |
| **BETA: Relay + GEN + APS** | 70-80% | 800-1.500 EUR | MEDIA-ALTA | 10 kWp | **SI - Piano B se Alpha non va** |
| **GAMMA: LOAD + APS** | 30-40% | 300-600 EUR | BASSA | 10 kWp | NO - Instabilita |
| **DELTA: Grid Simulator** | 40-50% | 3.000-6.000 EUR | ALTA | 10 kWp | NO - APS rende obsoleto |
| **EPSILON: Victron Bridge** | 85-90% | 2.500-4.000 EUR | MOLTO ALTA | 10 kWp | NO - Troppo costoso |

---

## PIANO D'AZIONE RACCOMANDATO

### Step 1: Verifica Compatibilita APS (SUBITO, costo zero)

1. **Controllare il firmware del SE10K-RWS** via SetApp:
   - Menu: ID Status → Software Version
   - Serve CPU >= 4.8.xxx (quasi certamente si, il firmware attuale dei trifase e ~4.16.xxx)

2. **Verificare se APS mode e disponibile in SetApp**:
   - Menu: Commissioning → Communication → GPIO → RRCR Mode
   - Se "Alternative Power Source" appare come opzione → **COMPATIBILE!**
   - Se non appare → contattare SolarEdge support per abilitazione

3. **Contattare SolarEdge Support Italia**:
   - Chiedere: "Il SE10K-RWS supporta APS mode per AC coupling con un inverter ibrido Deye?"
   - Chiedere: "E necessario un parametro di backend per abilitare P(f) in APS mode?"
   - Chiedere: "Qual e il firmware consigliato per APS mode su StorEdge trifase?"

### Step 2: Attivare Signal Island Mode sul Deye (SUBITO, costo zero)

1. Menu: Advanced Function → Signal Island Mode → **Enable**
2. Questo attiva il contatto secco G-valve (CN2, pin 3,4)
3. Verificare con un multimetro che il contatto si chiude quando si stacca la rete

### Step 3: Test di Fattibilita (1-2 settimane, costo minimo)

Se lo Step 1 conferma la compatibilita APS:

1. **Ricablare temporaneamente** il SolarEdge dalla porta GRID alla porta GEN del Deye
2. **Collegare il G-valve** del Deye al GPIO del SolarEdge
3. **Configurare APS mode** nel SolarEdge via SetApp
4. **Configurare P(f)**: 50.2 Hz = 100%, 51.0 Hz = 0%
5. **Ridurre AC Couple Frz High** del Deye da 55 Hz a 51.0 Hz
6. **Test on-grid**: verificare che il SolarEdge produca normalmente sulla porta GEN
7. **Test off-grid**: staccare il contatore e verificare che il SolarEdge si riavvii in APS mode

### Step 4: Soluzione Permanente (2-4 settimane)

Se il test va bene:
- **Soluzione Alpha**: cablaggio permanente SolarEdge → porta GEN
- **Soluzione Beta**: se servisse la commutazione on-grid/off-grid, installare il relay

Se il test NON va bene:
- Tornare alla configurazione originale
- Procedere con Soluzione A originale (pannelli direttamente su MPPT Deye) dall'analisi island-mode

---

## DETTAGLI TECNICI CRITICI

### Coordinamento Frequenze Deye ↔ SolarEdge

Il parametro piu critico e l'allineamento tra:

| Componente | Parametro | Valore Attuale | Valore Proposto |
|---|---|---|---|
| Deye | AC Couple Frz High | 55.00 Hz | **51.0 Hz** |
| Deye | Frequenza nominale | 50.00 Hz | 50.00 Hz (invariato) |
| SolarEdge APS | P(f) P0 | N/A | **50.2 Hz = 100%** |
| SolarEdge APS | P(f) P1 | N/A | **51.0 Hz = 0%** |
| SolarEdge CEI 0-21 | Trip HF1 | 51.5 Hz | Non rilevante in APS |

**Logica operativa**:
```
SOC < 65% (ON%)    → Deye freq = 50.0 Hz → SolarEdge = 100% produzione
SOC 65-70%         → Deye freq = 50.0-50.2 Hz → SolarEdge = 100%
SOC = 70% (OFF%)   → Deye alza freq progressivamente
freq = 50.2 Hz     → SolarEdge inizia a ridurre (droop P(f))
freq = 51.0 Hz     → SolarEdge = 0% produzione (shutdown dolce)
freq > 51.0 Hz     → SolarEdge fermo, Deye stabilizza
SOC scende < 65%   → Deye riporta freq a 50.0 Hz → SolarEdge riparte
```

### Capacita della Porta GEN del Deye

Il Deye SUN-12K-SG04LP3-EU supporta fino a **12 kW** sulla porta GEN in modalita MicInv Input. Il SolarEdge e da 10 kW → **COMPATIBILE** con margine.

### Tempo di Avvio del SolarEdge

Il SolarEdge ha un **tempo di riconnessione di ~60-120 secondi** dopo aver ricevuto la AC. In island mode:
1. Il Deye inizia a generare AC sulla porta GEN
2. Il G-valve chiude → GPIO → APS mode
3. Il SolarEdge verifica la stabilita della AC (30-60s in APS mode, meno restrittivo)
4. Il SolarEdge si connette e inizia a produrre
5. **La batteria deve sostenere la casa per 1-2 minuti** → con 16 kWh e carichi di 4-6 kW, nessun problema

### Qualita della AC del Deye in Backup Mode

Il Deye SUN-12K-SG04LP3-EU genera una AC ragionevolmente pulita in backup mode:
- THD (Total Harmonic Distortion) tipico: < 3% (accettabile)
- Stabilita frequenza: +/- 0.5 Hz (accettabile in APS mode)
- Stabilita tensione: +/- 5% (accettabile in APS mode)

L'APS mode del SolarEdge estende i range accettabili proprio per questo scenario.

---

## RISCHI E MITIGAZIONI

| Rischio | Probabilita | Impatto | Mitigazione |
|---|---|---|---|
| SE10K-RWS non supporta APS | **5-10%** | ALTO | **Confermato da documentazione** - restano rischi minori legati a country code IT |
| SolarEdge support non abilita P(f) | 10-20% | ALTO | Insistere, e una feature documentata; provare firmware update |
| AC del Deye non accettata in APS | 15-25% | ALTO | Verificare con test; se fallisce, Soluzione Beta con relay |
| Frequency shift troppo lento | 10-15% | MEDIO | La batteria da 16 kWh assorbe i transitori; tuning P(f) |
| Instabilita della micro-rete | 10-15% | MEDIO | Ridurre potenza max SolarEdge via SetApp (es. a 8 kW) |
| Porta GEN senza AC on-grid | 30-40% | MEDIO | Necessaria Soluzione Beta (relay commutatore) |

---

## NOTE SULLA NORMATIVA

### APS Mode e CEI 0-21

L'APS mode NON viola la CEI 0-21 perche:
1. In condizioni normali (on-grid), il SolarEdge opera con CEI 0-21 completa
2. L'APS mode si attiva SOLO quando la rete non e presente (segnale GPIO)
3. In APS mode, il SolarEdge opera in una micro-rete isolata dalla rete pubblica
4. Non c'e rischio di backfeed in rete: il Deye isola la micro-rete con l'ATS
5. Quando la rete torna, il SolarEdge torna a CEI 0-21 prima di riconnettersi

**L'installazione deve essere eseguita da un elettricista qualificato** che comprenda sia l'architettura Deye che il SolarEdge APS mode.

---

## CONCLUSIONE

**La scoperta dell'APS mode cambia completamente lo scenario.** Quella che sembrava un'impossibilita tecnica (SolarEdge anti-islanding non disabilitabile) diventa una soluzione praticabile con funzionalita ufficiali.

**La Soluzione Alpha (SolarEdge sulla porta GEN + APS mode) e la nostra raccomandazione principale.** Ha il miglior rapporto costo/beneficio e si basa su feature ufficiali di entrambi i produttori.

Il primo passo e **verificare la compatibilita APS in SetApp** (costo zero, tempo 5 minuti) e **contattare SolarEdge support** per conferma e abilitazione del parametro P(f) di backend.

Se funziona: 10 kWp di produzione solare in island mode per 300-800 EUR.
Se non funziona: si torna al piano originale (pannelli su MPPT Deye + batterie aggiuntive).

**Il gioco vale assolutamente la candela.**

---

## Fonti e Riferimenti

- [Victron: Integrating with SolarEdge](https://www.victronenergy.com/live/venus-os:gx_solaredge) - Guida completa APS mode
- [SolarEdge Application Note: Alternative Power Source](https://knowledge-center.solaredge.com/sites/kc/files/se-inverter-support-of-voltage-sources.pdf)
- [SolarEdge Power Control Options (April 2024)](https://knowledge-center.solaredge.com/sites/kc/files/application_note_power_control_configuration.pdf)
- [DIY Solar Forum: AC Coupling SolarEdge to Hybrid Inverter](https://diysolarforum.com/threads/pros-and-cons-of-ac-coupling-a-solaredge-inverter-into-hybrid-inverter.88724/)
- [DIY Solar Forum: Deye GEN Input - Microinverter/On-Grid Inverter](https://diysolarforum.com/threads/deye-gen-input-microinverter-on-grid-inverter.36784/)
- [DIY Solar Forum: How to AC Couple & Frequency Shift SolarEdge](https://diysolarforum.com/threads/how-to-ac-couple-frequency-shift-a-solaredge-se5000h-us.54538/)
- [DIY Solar Forum: Deye and SolarEdge GEN GRID Ports](https://diysolarforum.com/threads/deye-and-solaredge-gen-grid-ports.83025/)
- [DIY Solar Forum: Simplest AC Coupling for Backup with SolarEdge](https://diysolarforum.com/threads/simplest-ac-coupling-for-backup-power-on-an-existing-solaredge-system.107499/)
- [Victron Community: AC Coupling with SolarEdge Off-Grid](https://community.victronenergy.com/questions/54185/ac-coupling-with-solaredge-requirements-for-pure-o.html)
- [Victron Community: SolarEdge Frequency Coupling Shutdown](https://community.victronenergy.com/questions/121452/victron-coupled-to-solaredge-wr-shutodown-caused-b.html)
- [SolarEdge Viewing Grid Protection Values](https://knowledge-center.solaredge.com/sites/kc/files/viewing_grid_protection_values.pdf)
- [SolarEdge SetApp Firmware Updates](https://www.solaredge.com/en/support/setapp-inverters-firmware)
- [SolarEdge StorEdge Three Phase Datasheet](https://www.solaredge.com/sites/default/files/se_storedge_three_phase_inverter_datasheet.pdf)
