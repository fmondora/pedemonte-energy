# Aggiunta Seconda Batteria Battery Queen al Deye SUN-12K-SG04LP3-EU

> Data analisi: 2026-02-27
> Fonte: Datasheet SUN-5/12K-SG04LP3-EU, Manuale utente, knowledge base Battery Queen 51.2V 314Ah
> Autore: deye-expert

## Sommario Esecutivo

**Si, il Deye SUN-12K-SG04LP3-EU supporta il collegamento di piu batterie in parallelo.** Il datasheet dichiara esplicitamente "Support multiple batteries parallel". Tuttavia, l'operazione richiede attenzione su diversi aspetti tecnici, e **si raccomanda fortemente l'intervento dell'installatore (Davide Duca)**.

---

## 1. Supporto Multi-Batteria del Deye SUN-12K-SG04LP3-EU

### Cosa dice la documentazione ufficiale

| Fonte | Informazione |
|---|---|
| Datasheet (pagina 1) | "Support multiple batteries parallel" |
| Datasheet (tabella) | Number of Battery Input: **1** |
| Datasheet (tabella) | Battery Voltage Range: **40-60V** |
| Datasheet (tabella) | Max Charging Current (12K): **240A** |
| Datasheet (tabella) | Max Discharging Current (12K): **240A** |
| Parametri agente | Capacita batteria supportata: **fino a 60 kWh** |
| Manuale sezione 3.3 | Un singolo connettore DC per batteria (item 8) |
| Manuale sezione 3.3.2 | Una singola porta BMS (CAN/RS485) (item 11) |
| Manuale sezione 5.6 | Singolo parametro "Battery Capacity" nel menu |
| Errore F46 | "check each battery status... make sure all parameters are same" (implica multi-pack) |

### Interpretazione

L'inverter ha **una sola porta DC di ingresso batteria** e **una sola porta BMS (CAN/RS485)**. Tuttavia, il supporto per "multiple batteries parallel" indica che:

- Le batterie vanno collegate **in parallelo sul bus DC** (stesso polo + e - condiviso)
- Il collegamento NON e "in cascata" (serie) -- sarebbe incompatibile con il range 40-60V
- Le batterie si collegano fisicamente in parallelo: i terminali + di entrambe vanno allo stesso morsetto + dell'inverter, e i terminali - allo stesso morsetto -
- Con 2 batterie in parallelo da 51.2V: tensione = 51.2V (invariata), capacita = 628 Ah (~32 kWh)

### Capacita massima di accumulo

- Range tensione batteria: 40-60V
- Corrente max carica/scarica: 240A (modello 12K)
- Capacita massima supportata: **~60 kWh** (indicazione dall'agente, basata su documentazione Deye estesa)
- Con 2x Battery Queen da ~16 kWh = **~32 kWh** -- ampiamente entro i limiti

---

## 2. Collegamento Fisico

### Schema di collegamento: PARALLELO (NON serie/cascata)

```
                    ┌──────────────────┐
                    │   Deye 12K       │
                    │   SG04LP3-EU     │
                    │                  │
                    │  BAT+ ──┬── BAT- │
                    │         │        │
                    └─────────┼────────┘
                              │
                    ┌─────────┼────────┐
                    │    DC Breaker    │
                    │    300A DC       │
                    │  (GIA' PRESENTE) │
                    └─────────┼────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              │    Bus bar / Junction box     │
              │      (+) ─────┼───── (-)      │
              │               │               │
              ├───────┐       │       ┌───────┤
              │       │       │       │       │
         ┌────┴───┐   │       │   ┌───┴────┐  │
         │Fusibile│   │       │   │Fusibile│  │
         │200-250A│   │       │   │200-250A│  │
         └────┬───┘   │       │   └───┬────┘  │
              │       │       │       │       │
     ┌────────┴──┐    │       │  ┌────┴──────┐│
     │ Battery   │    │       │  │ Battery   ││
     │ Queen #1  │    │       │  │ Queen #2  ││
     │ 51.2V     │    │       │  │ 51.2V     ││
     │ 314Ah     │    │       │  │ 314Ah     ││
     │ ~16 kWh   │    │       │  │ ~16 kWh   ││
     └───────────┘    │       │  └───────────┘│
                      │       │               │
                      └───────┴───────────────┘
```

### IMPORTANTE: NON collegare in serie (cascata)

- Due batterie da 51.2V in serie darebbero **102.4V** -- FUORI dal range 40-60V dell'inverter
- Questo **DANNEGGEREBBE IRREVERSIBILMENTE** l'inverter
- Il collegamento DEVE essere in **parallelo**: +con+, -con-

### Componenti necessari per il collegamento

| Componente | Specifica | Note |
|---|---|---|
| **Cavi DC** | 250kcmil / 120mm2 (come quelli esistenti) | Per il modello 12kW, come da Chart 3-2 del manuale |
| **Fusibili DC** | 200-250A per ogni batteria | Protezione individuale di ogni batteria |
| **Bus bar / Junction box** | Adeguato per 300A+ | Per unire i cavi delle due batterie prima dell'inverter |
| **DC Breaker** | 300A (gia presente per la batteria #1) | Verificare che sia adeguato per la corrente totale |
| **Capicorda / terminali** | M10 (come da manuale, connettore a bullone) | Per il modello 5-12kW |
| **Cavi BMS** | Cavo CAN o RS485 (dipende dal protocollo) | Vedi sezione 3 sotto |

### Procedura di collegamento fisico (da eseguire con impianto SPENTO)

1. **Spegnere completamente l'inverter** (DC switch OFF + AC breaker OFF)
2. **Attendere almeno 5 minuti** (scarica condensatori interni)
3. **Scollegare la batteria #1** dal bus DC
4. **Installare i fusibili individuali** per ogni batteria
5. **Collegare entrambe le batterie in parallelo** tramite bus bar/junction box
6. **Verificare la polarita** (+con+, -con-) -- un errore distrugge l'inverter
7. **Collegare il cavo BMS** (vedi sezione 3)
8. **Ricollegare al DC breaker** dell'inverter
9. **Accendere e configurare** (vedi sezione 4)

---

## 3. Gestione BMS

### Porta BMS dell'inverter

L'inverter ha **una sola porta BMS** (RJ45) che supporta sia CAN che RS485 sullo stesso connettore:

| Pin | Funzione |
|---|---|
| 1 | 485_B |
| 2 | 485_A |
| 3 | -- |
| 4 | CAN-H |
| 5 | CAN-L |
| 6 | GND_485 |
| 7 | 485_A |
| 8 | 485_B |

### Come gestire due batterie con un singolo BMS port

Ci sono **due scenari possibili**, a seconda delle capacita della Battery Queen:

#### Scenario A: La Battery Queen supporta il daisy-chain BMS (piu probabile)

Se la Battery Queen supporta il collegamento in parallelo con comunicazione daisy-chain:

1. **Batteria #1** (Master) si collega via CAN/RS485 all'inverter (come ora)
2. **Batteria #2** (Slave) si collega alla Batteria #1 tramite una porta di espansione/parallelo
3. Il **BMS Master** (Batteria #1) aggrega i dati di entrambe e comunica con l'inverter
4. L'inverter vede un **unico sistema batteria** con capacita raddoppiata

Questo e il metodo standard per la maggior parte delle batterie LiFePO4 da rack/server.

#### Scenario B: La Battery Queen NON supporta il daisy-chain BMS

Se la Battery Queen non ha una porta di espansione per il parallelo BMS:

1. Le batterie si collegano **solo in parallelo DC** (senza comunicazione BMS tra di loro)
2. L'inverter comunica con **una sola batteria** via BMS
3. Il BMS della seconda batteria opera in modo **indipendente** (protegge solo se stessa)
4. L'inverter vede il SOC/tensione di una sola batteria (ma la corrente e condivisa)

Questo scenario e **meno ideale** ma funziona, perche:
- Le due batterie identiche tendono a bilanciarsi naturalmente (stessa tensione = stessa chimica)
- Ogni BMS protegge individualmente la propria batteria
- L'inverter controlla la tensione del bus DC, che e comune

### INFORMAZIONE MANCANTE CRITICA

**Non abbiamo il manuale completo della Battery Queen.** Dobbiamo verificare:

- [ ] Se la Battery Queen ha una porta di espansione/parallelo per il BMS
- [ ] Quale protocollo BMS usa esattamente (CAN o RS485 -- attualmente sconosciuto)
- [ ] Se il produttore supporta ufficialmente il collegamento in parallelo di piu unita
- [ ] Il numero massimo di batterie collegabili in parallelo

**Azione raccomandata**: Contattare il venditore/produttore della Battery Queen e chiedere:
1. "La Battery Queen 51.2V 314Ah supporta il collegamento in parallelo di piu unita?"
2. "Esiste una porta di comunicazione per il daisy-chain BMS tra batterie?"
3. "Quale protocollo BMS usate? CAN, RS485, o entrambi?"
4. "Avete un manuale di installazione per configurazione multi-batteria?"

---

## 4. Configurazione Software dell'Inverter

### Parametri da modificare sul Deye

| Parametro | Valore Attuale | Nuovo Valore | Note |
|---|---|---|---|
| **Battery Capacity** | 314 Ah | **628 Ah** | Somma delle due batterie in parallelo |
| **Max A Charge** | 200 A | **200-240 A** | Verificare con le specifiche BMS; max inverter = 240A |
| **Max A Discharge** | 200 A | **200-240 A** | Verificare con le specifiche BMS; max inverter = 240A |
| **Batt Type** | BMS Lithium Batt | BMS Lithium Batt | Invariato |
| **Lithium Mode** | 0 | Da verificare | Potrebbe cambiare se il protocollo BMS richiede adattamento |
| **Batt Shutdown %** | 10% | 10% | Invariato -- ora equivale a ~6.3 kWh (era ~1.6 kWh) |
| **Batt Low %** | 20% | 15-20% | Considerare di abbassare -- piu capacita = piu margine |
| **Batt Restart %** | 35% | 30-35% | Considerare di abbassare |

### Note sulla corrente di carica/scarica

- L'inverter 12K supporta **max 240A** di carica e scarica
- Ogni Battery Queen probabilmente supporta 150-200A (da confermare)
- In parallelo, la corrente si **divide equamente** tra le due batterie
- Con Max Charge/Discharge a 200A: ogni batteria riceve ~100A (ben entro i limiti)
- **NON impostare oltre 240A** -- e il limite hardware dell'inverter

### Procedura di configurazione

1. Accedere al menu **System Setup > Battery Setting**
2. Modificare **Batt Capacity** da 314 a **628** Ah
3. Verificare e eventualmente aumentare **Max A Charge** e **Max A Discharge**
4. Verificare nella pagina **Li-BMS** che la comunicazione funzioni correttamente
5. Monitorare il **SOC** nelle prime ore per verificare che il calcolo sia corretto
6. Verificare che non ci siano errori F46 (backup battery fault) o F58 (BMS communication fault)

---

## 5. Rischi e Precauzioni

### Rischio 1: Squilibrio di SOC al momento del collegamento -- ALTO RISCHIO

**Problema**: Se la batteria #1 (gia in uso) ha un SOC diverso dalla batteria #2 (nuova), al momento del collegamento in parallelo ci sara una **corrente di equalizzazione molto elevata** tra le due batterie. Due batterie LiFePO4 con anche solo 2-3V di differenza possono generare **centinaia di ampere** di picco.

**Precauzione OBBLIGATORIA**:
1. **Prima di collegare fisicamente**, misurare la tensione di entrambe le batterie
2. Le tensioni DEVONO essere **entro 0.5V** l'una dall'altra (idealmente entro 0.2V)
3. Se la differenza e maggiore:
   - Caricare/scaricare la batteria con SOC piu basso/alto fino a eguagliare le tensioni
   - Usare un resistore di pre-carica per limitare la corrente iniziale
4. **Mai collegare due batterie con piu di 1V di differenza** -- puo danneggiare i BMS e i connettori

### Rischio 2: Bilanciamento a lungo termine -- BASSO RISCHIO

**Problema**: Nel tempo, le due batterie potrebbero sviluppare uno squilibrio di capacita/SOC.

**Mitigazione**:
- Le batterie **identiche** (stesso modello, stessa chimica, stessa capacita) tendono a bilanciarsi naturalmente
- Il bus DC condiviso forza la stessa tensione su entrambe
- Ogni BMS gestisce il bilanciamento celle **interno** alla propria batteria
- Lo squilibrio tra le due batterie e generalmente **minimo** se sono dello stesso lotto/eta
- Se una batteria e significativamente piu vecchia, lo squilibrio potrebbe aumentare nel tempo

### Rischio 3: Protezione BMS non coordinata (se Scenario B) -- MEDIO RISCHIO

**Problema**: Se i due BMS operano indipendentemente, uno potrebbe scollegare la propria batteria mentre l'altra continua a lavorare. Questo causerebbe un **raddoppio improvviso della corrente** sulla batteria rimasta.

**Mitigazione**:
- I fusibili individuali proteggono ogni batteria dal sovraccarico
- L'inverter ha protezioni interne contro il sovracorrente DC
- Il BMS-Err-Stop nel menu Advanced Function dovrebbe rilevare il problema

### Rischio 4: Polarita invertita -- RISCHIO CATASTROFICO

**Problema**: Un errore di polarita durante il collegamento distrugge l'inverter immediatamente.

**Mitigazione**:
- **Triplo controllo** della polarita prima di chiudere il circuito
- Usare un multimetro per verificare la tensione e la polarita
- Mai lavorare di fretta o da soli

### Rischio 5: Corrente totale oltre i limiti -- BASSO RISCHIO

**Problema**: Due batterie in parallelo possono erogare il doppio della corrente.

**Mitigazione**:
- L'inverter limita la corrente a 240A via software
- I fusibili individuali (200-250A per batteria) proteggono da cortocircuiti
- Il DC breaker protegge il collegamento verso l'inverter

---

## 6. Serve l'Installatore (Davide Duca)?

### Risposta: SI, fortemente raccomandato

**Motivazioni**:

1. **Sicurezza elettrica**: Si lavora con correnti DC fino a 240A a 51.2V -- potenzialmente letali in caso di cortocircuito (arco elettrico DC). Il manuale Deye dichiara esplicitamente: "All wiring must be performed by a professional person" e "Only qualified personnel can install this device with battery"

2. **Garanzia**: Un'installazione non professionale potrebbe invalidare la garanzia dell'inverter e delle batterie

3. **Dimensionamento protezioni**: Il DC breaker attuale (presumibilmente 300A) potrebbe dover essere sostituito o affiancato da protezioni aggiuntive. Serve una valutazione professionale

4. **Pre-carica**: Il collegamento di due batterie con SOC diverso richiede competenza e strumentazione adeguata

5. **Configurazione BMS**: La configurazione del collegamento BMS (daisy-chain o indipendente) richiede conoscenza specifica del modello Battery Queen

6. **Normativa**: In Italia, gli interventi sull'impianto di accumulo richiedono personale qualificato. Potrebbe essere necessaria una comunicazione all'ENEA o al GSE se l'accumulo e registrato

### Cosa fare prima di chiamare l'installatore

1. **Procurarsi il manuale della Battery Queen** -- chiedere al venditore
2. **Verificare con il venditore** il supporto parallelo multi-batteria (vedi sezione 3)
3. **Acquistare la seconda batteria** (identica alla prima: stessa marca, modello, capacita)
4. **Acquistare i componenti aggiuntivi**: fusibili DC, bus bar/junction box, cavi DC aggiuntivi
5. **Informare Davide Duca** del progetto e chiedere un preventivo per l'installazione

---

## 7. Checklist Pre-Installazione

- [ ] Manuale Battery Queen ottenuto e verificato supporto parallelo
- [ ] Protocollo BMS confermato (CAN o RS485)
- [ ] Supporto daisy-chain BMS verificato
- [ ] Seconda batteria acquistata (identica alla prima)
- [ ] Componenti aggiuntivi acquistati (fusibili, bus bar, cavi)
- [ ] Installatore contattato e data intervento fissata
- [ ] Verificare se serve comunicazione al GSE/ENEA per aumento accumulo
- [ ] Backup della configurazione attuale dell'inverter (foto di tutte le schermate)

---

## 8. Benefici Attesi

| Parametro | Prima | Dopo |
|---|---|---|
| Capacita accumulo | ~16 kWh | **~32 kWh** |
| Autonomia notturna (3kW medi) | ~4-5 ore | **~8-10 ore** |
| Autonomia backup (5kW medi) | ~2.5 ore | **~5 ore** |
| SOC utilizzabile (20%-100%) | ~12.8 kWh | **~25.6 kWh** |
| Copertura giornaliera tipica | Parziale (serale) | **Quasi completa (sera+notte)** |

Con 32 kWh di accumulo, la casa di Pedemonte potrebbe raggiungere un'autonomia significativamente maggiore, specialmente in primavera/estate quando la produzione PV e elevata.

---

## Raccomandazione Finale

### Raccomandazione: Aggiunta seconda batteria in parallelo

**Contesto**: Impianto con Deye SUN-12K-SG04LP3-EU e una Battery Queen 51.2V 314Ah (~16 kWh). Desiderio di raddoppiare l'accumulo.

**Problema/Opportunita**: 16 kWh di accumulo non coprono il fabbisogno notturno completo. Raddoppiare a 32 kWh migliorerebbe significativamente l'autosufficienza.

**Azione raccomandata**:
1. Verificare il supporto parallelo della Battery Queen con il produttore
2. Acquistare una seconda Battery Queen identica
3. Far eseguire l'installazione da Davide Duca (installatore qualificato)
4. Aggiornare la configurazione inverter (capacita 628Ah)
5. Monitorare il sistema per 1-2 settimane dopo l'installazione

**Parametri da modificare**: Battery Capacity 314 -> 628 Ah, eventualmente Max A Charge/Discharge

**Rischio**: **Medio** - L'operazione e supportata dall'inverter ma richiede competenza tecnica per il collegamento sicuro e la gestione del BMS. Il rischio principale e lo squilibrio di tensione al momento del primo collegamento.

**Impatto atteso**: Raddoppio della capacita di accumulo (~32 kWh), autonomia notturna quasi completa, migliore autosufficienza energetica.

**Verifica**: Monitorare SOC, tensione batteria, corrente di carica/scarica nelle prime 48 ore. Verificare assenza di errori F46, F55, F56, F58 sul display dell'inverter.
