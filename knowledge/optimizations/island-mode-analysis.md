# Analisi Island Mode: Perche i Pannelli si Spengono in Off-Grid

> Data analisi: 27/02/2026
> Autore: Team Energia (SolarEdge Expert + Deye Expert + Electrical Engineer)
> Urgenza: ALTA - Il proprietario sta testando ORA

---

## Sintesi per il Proprietario (TL;DR)

**Quando stacchi il contatore Enel, il SolarEdge si spegne ed e CORRETTO che lo faccia.** Non e un guasto: e una protezione di sicurezza obbligatoria per legge (CEI 0-21 anti-islanding).

**Il SolarEdge SE10K-RWS NON supporta il funzionamento in island/backup mode.** Il manuale SolarEdge lo dice esplicitamente: "For backup power, an inverter specifically designed for backup applications is required; this inverter is not in the scope of this document."

**Conseguenza pratica: in blackout (o off-grid), la casa va SOLO a batteria.** I 10 kW di pannelli collegati al SolarEdge sono completamente inutilizzati.

**Esistono soluzioni**, ma nessuna e banale o immediata. Vedi sezione 5.

---

## 1. Perche il SolarEdge si Spegne

### 1.1 La Catena di Eventi

```
1. Il contatore Enel viene staccato (o blackout reale)
2. Il Deye rileva la perdita di rete (entro 0.1s, protezioni IP)
3. Il Deye si disconnette dalla rete e va in BACKUP MODE
4. Il Deye genera una AC locale a 230V/400V 50Hz sulla porta LOAD (backup)
5. La casa viene alimentata dalla batteria tramite il Deye
6. Il SolarEdge rileva la perdita di rete (anti-islanding)
7. Il SolarEdge si SPEGNE (SafeDC attivato, ottimizzatori a 1V)
8. Nessuna produzione solare → la casa va SOLO a batteria
```

### 1.2 Perche l'Anti-Islanding si Attiva

Il SolarEdge ha protezioni anti-islanding **integrate e non disabilitabili**:

| Protezione | Cosa verifica | Perche scatta |
|---|---|---|
| **Frequenza** | 48.0 - 51.5 Hz (CEI 0-21) | La AC del Deye in backup potrebbe avere micro-variazioni |
| **Tensione** | 185 - 265 V (L-N) | La AC del Deye potrebbe oscillare sotto carico |
| **Impedenza di rete** | Bassa impedenza tipica della rete pubblica | La AC del Deye ha impedenza MOLTO piu alta della rete Enel |
| **Test attivo anti-islanding** | Perturbazioni periodiche di frequenza | Il SolarEdge inietta piccole perturbazioni e misura la risposta. Una rete reale "assorbe" le perturbazioni. La AC del Deye NO. |

**Il punto chiave e l'impedenza.** La rete Enel ha impedenza bassissima (praticamente "infinita" capacita di assorbire/fornire potenza). La AC generata dal Deye in backup mode ha impedenza alta (la sorgente e un inverter da 12kW con batteria). Il SolarEdge rileva questa differenza e conclude: "non sono connesso alla rete, sono in un'isola" → si spegne.

### 1.3 E un Requisito Normativo

La norma **CEI 0-21** (connessione alla rete BT in Italia) **IMPONE** la protezione anti-islanding per tutti gli inverter grid-connected. L'anti-islanding **non puo essere disabilitato** dall'installatore ne dall'utente. E una protezione di sicurezza per:

- Proteggere i tecnici che lavorano sulla rete (pensano che sia de-energizzata)
- Evitare di alimentare la rete pubblica in modo incontrollato
- Proteggere gli apparecchi dalla AC non regolata

---

## 2. Il SolarEdge SE10K-RWS Puo Funzionare in Island Mode?

### 2.1 Risposta Breve: NO

Il **SE10K-RWS** e un inverter **StorEdge** (gestione batteria + PV), ma **NON** e un inverter con funzione backup. Dal manuale ufficiale (Installation Guide MAN-01-00648-1.3, pagina 10):

> "For backup power, an inverter specifically designed for backup applications is required; **this inverter is not in the scope of this document**."

### 2.2 Confronto con Prodotti SolarEdge che Supportano Backup

| Prodotto | Backup/Island Mode | Note |
|---|---|---|
| **SE10K-RWS** (quello installato) | **NO** | StorEdge, non Backup |
| SolarEdge Home Hub (SE-XXXX-HUB) | **SI** | Inverter con backup integrato |
| SolarEdge Backup Interface (BI) | **SI** | Accessorio esterno per backup |
| SolarEdge Energy Hub | **SI** | Nuova generazione con backup |

### 2.3 Il Backup Interface e Compatibile?

Il **SolarEdge Backup Interface** (codice SE-BUI-S-RWS-01-3) e un accessorio che aggiunge la funzione backup a un inverter StorEdge RWS. **Potrebbe** essere compatibile con il SE10K-RWS, ma:

- Richiede verifica di compatibilita firmware
- Richiede installazione professionale (modifica del quadro elettrico)
- Costo stimato: 1.500-2.500 EUR + installazione
- **ATTENZIONE**: il Backup Interface creerebbe la SUA isola AC. Questo complicherebbe enormemente l'architettura perche avremmo DUE inverter che cercano di creare isole AC indipendenti (il Deye e il SolarEdge con BI)

### 2.4 Configurazione SetApp

Non esiste nessuna impostazione in SetApp per:
- Disabilitare l'anti-islanding (vietato da CEI 0-21)
- Abilitare il funzionamento in island mode senza hardware dedicato
- Accettare un segnale esterno di "island mode"

---

## 3. Il Deye Supporta il Micro-Inverter in Backup Mode?

### 3.1 Risposta Breve: SI, il Deye e Pronto

Il Deye SUN-12K-SG04LP3-EU supporta il **Modo IV: AC Couple** che prevede esplicitamente un inverter grid-tied collegato alla porta GEN come micro-inverter. Il manuale mostra questo schema nel capitolo 6.

### 3.2 Parametri Rilevanti gia Configurati

| Parametro | Valore Attuale | Funzione |
|---|---|---|
| SmartLoad Setup | **MicInv Input** | Porta GEN come ingresso micro-inverter |
| OFF % | **70%** | SOC a cui il micro-inverter viene spento (frequenza alta) |
| ON % | **65%** | SOC a cui il micro-inverter viene riacceso |
| AC Couple Frz High | **55.00 Hz** | Frequenza massima per segnalare "stop produzione" |
| MI Export to Grid Cutoff | **Disable** | |
| Signal Island Mode | **Disable** | Contatto secco G-valve NON attivo |

### 3.3 Come Funziona AC Couple Frz High (Frequency Shifting)

Questo e il meccanismo chiave per il controllo del micro-inverter:

```
SOC batteria alta (>= OFF% = 70%):
  → Il Deye AUMENTA la frequenza fino a AC Couple Frz High (55 Hz)
  → Il micro-inverter rileva over-frequency → RIDUCE la produzione
  → Quando SOC scende sotto ON% (65%), il Deye RIPORTA la freq a 50 Hz
  → Il micro-inverter riprende a produrre normalmente
```

**IMPORTANTE**: Questo funziona SOLO se il micro-inverter e acceso e produce. Se il SolarEdge si spegne per anti-islanding, non c'e nulla da controllare.

### 3.4 La AC sulla Porta GEN in Backup Mode

Quando il Deye va in backup mode:
- La porta **LOAD** (backup) e ATTIVA: alimenta la casa dalla batteria
- La porta **GRID** e DISCONNESSA dalla rete (ATS aperto)
- La porta **GEN**: e alimentata dalla stessa AC locale del Deye

**Il Deye genera AC anche sulla porta GEN in backup mode**, perche in Modo IV (AC Couple) il micro-inverter deve "vedere" una rete per poter produrre. Il Deye fa da "grid-forming" inverter: genera la rete locale.

### 3.5 Il Problema: Il SolarEdge Non Collabora

Il Deye e progettato per funzionare con un micro-inverter in island mode. Ma il SolarEdge:
1. Rileva che la AC sulla porta GEN non e la "vera" rete Enel
2. Attiva l'anti-islanding e si spegne
3. Il Deye rimane solo con la batteria

### 3.6 Signal Island Mode e Contatto G-Valve

Il Deye ha un parametro **Signal Island Mode** (attualmente Disable). Quando attivato:
- Il relay sulla N line del load port si chiude (N → ground)
- Il contatto secco **G-valve** (CN2, pin 3,4) si chiude quando l'inverter e in off-grid mode

Questo contatto secco POTREBBE essere usato per segnalare a un dispositivo esterno che il sistema e in island mode. Tuttavia, il SolarEdge SE10K-RWS **non ha un ingresso per ricevere questo segnale**. Non c'e nessun modo per dire al SolarEdge "siamo in island mode, disabilita l'anti-islanding".

---

## 4. Limiti di Potenza e Stabilita in Backup Mode

### 4.1 Anche SE il SolarEdge Producesse...

Se ipoteticamente il SolarEdge riuscisse a produrre in island mode, il Deye dovrebbe gestire:

| Parametro | Valore | Note |
|---|---|---|
| Potenza Deye backup mode | 12 kW (continua) | 13.2 kW picco per 10s |
| Potenza SolarEdge max | 10 kW | Immissione sulla porta GEN |
| Potenza carichi casa | 1-6 kW | Variabile |
| Potenza carica batteria | fino a ~10 kW | 200A x 51.2V |

**Scenario critico**: sole pieno (SolarEdge produce 10 kW) + carichi bassi (1 kW) = 9 kW surplus che va in batteria. Il Deye dovrebbe:
1. Stabilizzare tensione e frequenza mentre assorbe 10 kW dalla porta GEN
2. Alimentare i carichi (1 kW)
3. Caricare la batteria con l'eccesso (9 kW)
4. Evitare sovraccarichi e instabilita

Il Deye SUN-12K-SG04LP3-EU e dimensionato per gestire questo (12 kW), ma la stabilita della micro-rete dipende dalla velocita di regolazione dell'inverter. Il meccanismo AC Couple Frz High e progettato esattamente per questo: quando la batteria e piena, il Deye alza la frequenza e il micro-inverter riduce la produzione.

---

## 5. Soluzioni Possibili

### Soluzione A: Collegare Pannelli Direttamente al Deye (RACCOMANDATA - PIU PRATICA)

**Concetto**: Spostare alcune stringhe di pannelli dal SolarEdge al Deye, collegandole direttamente agli MPPT del Deye.

| Aspetto | Dettaglio |
|---|---|
| **Fattibilita** | ALTA - Il Deye ha 2 MPPT, fino a 15.6 kW DC (18 kW per il 12K) |
| **Costo** | 200-500 EUR (cablaggio DC + connettori) |
| **Tempo** | 1 giorno di lavoro per elettricista |
| **Produzione in island mode** | SI - Gli MPPT del Deye funzionano anche in backup mode |
| **Limite** | Si perdono gli ottimizzatori SolarEdge su quelle stringhe |
| **Impatto** | Produzione solare disponibile in backup mode |

**Come fare**:
1. Identificare 1-2 stringhe di pannelli (es. 3-5 kWp)
2. Disconnetterle dal SolarEdge (rimuovere ottimizzatori o bypassarli)
3. Collegarle agli ingressi MPPT del Deye (DC1 e/o DC2)
4. Il Deye produrra direttamente in backup mode

**Limite**: il Deye ha 2 MPPT con max 13A+13A per il 5K, fino a 26A+13A per il 12K. Verificare la compatibilita delle stringhe (tensione e corrente).

**ATTENZIONE**: I pannelli con ottimizzatori SolarEdge NON possono essere collegati direttamente al Deye. Servono pannelli SENZA ottimizzatore, oppure bypassare gli ottimizzatori (operazione non banale e che invalida la garanzia SolarEdge).

**Variante pratica**: Se ci sono pannelli di riserva o la possibilita di aggiungere nuovi pannelli (anche 2-3 pannelli da 400-500W), collegarli direttamente al Deye sarebbe la soluzione piu semplice e economica.

### Soluzione B: Inverter Grid-Tied Compatibile con Island Mode

**Concetto**: Sostituire il SolarEdge con un inverter grid-tied che supporta l'accoppiamento AC in island mode.

| Inverter | Funzione Island Mode | Compatibilita con Deye AC Couple |
|---|---|---|
| **Fronius Symo/Gen24** | "MicroGrid" mode tramite contatto esterno | SI - Ampiamente testato con inverter ibridi |
| **SMA Sunny Boy/Tripower** | "Secure Power Supply" (limitato) | Parziale - funziona in configurazioni specifiche |
| **Victron MultiPlus** | Nativo in island mode | SI - Ma e un inverter ibrido, non grid-tied |
| **GoodWe** | Supporta AC couple con inverter ibrido | SI - Alcuni modelli |

**Il Fronius e la scelta piu comune e testata** per AC coupling con inverter ibridi in island mode:
- Ha un ingresso digitale per "MicroGrid" mode
- Quando riceve il segnale, disabilita l'anti-islanding e lavora come "grid-following" su rete locale
- Il contatto G-valve del Deye (Signal Island Mode) potrebbe pilotare direttamente l'ingresso MicroGrid del Fronius

| Aspetto | Dettaglio |
|---|---|
| **Fattibilita** | ALTA - Soluzione collaudata nel settore |
| **Costo** | 2.000-4.000 EUR (Fronius 10kW trifase) + installazione |
| **Tempo** | 2-3 giorni di lavoro |
| **Produzione in island mode** | SI - Tutti i 10 kW PV disponibili anche in backup |
| **Impatto** | Si perdono gli ottimizzatori SolarEdge e il monitoraggio a livello pannello |

### Soluzione C: SolarEdge Backup Interface

**Concetto**: Aggiungere il SolarEdge Backup Interface (BI) al SE10K-RWS per abilitare la funzione backup nativa del SolarEdge.

**PROBLEMA CRITICO**: Questa soluzione crea un conflitto architetturale:
- Il Deye gestisce gia il backup della casa
- Il SolarEdge con BI vorrebbe creare la SUA isola AC
- Avremmo DUE inverter che cercano di fare "grid-forming" sulla stessa rete locale
- Questo NON funziona senza un coordinamento sofisticato

| Aspetto | Dettaglio |
|---|---|
| **Fattibilita** | BASSA - Conflitto architetturale con il Deye |
| **Costo** | 1.500-2.500 EUR (BI) + 1.000-2.000 EUR ricablaggio |
| **Complessita** | MOLTO ALTA |
| **Rischio** | ALTO - Due inverter grid-forming sulla stessa rete = instabilita |

**NON RACCOMANDATA** nella configurazione attuale.

### Soluzione D: Ricablaggio del SolarEdge sull'Uscita Backup del Deye

**Concetto**: Collegare l'uscita AC del SolarEdge direttamente all'uscita BACKUP del Deye (invece che alla porta GEN), cosi il SolarEdge "vede" la AC locale del Deye come rete.

**PROBLEMA**: Il SolarEdge farebbe comunque l'anti-islanding test e rileverebbe che la "rete" ha impedenza alta. Si spegnerebbe lo stesso.

**INOLTRE**: Il SolarEdge in questo caso immeterebbe potenza nel bus AC locale del Deye senza che il Deye ne sia consapevole (non passerebbe dalla porta GEN con il controllo MicInv). Questo potrebbe destabilizzare il sistema.

| Aspetto | Dettaglio |
|---|---|
| **Fattibilita** | MOLTO BASSA - L'anti-islanding scatterebbe comunque |
| **Rischio** | ALTO - Potenza non controllata sul bus backup |

**NON RACCOMANDATA.**

### Soluzione E: Mantenere lo Status Quo e Dimensionare le Batterie

**Concetto**: Accettare che in blackout la produzione PV sia zero e dimensionare le batterie di conseguenza.

Questa e la "non-soluzione" gia analizzata in `offgrid-battery-sizing.md`:

| Batterie | Capacita | Autonomia senza sole | Costo |
|---|---|---|---|
| 1 (attuale) | 16 kWh | ~0.7 giorni | 0 EUR |
| 2 | 32 kWh | ~1.5 giorni | +1.200 EUR |
| 3 | 48 kWh | ~2.4 giorni | +2.400 EUR |
| 4 | 64 kWh | ~3.2 giorni | +3.600 EUR |

**Nota**: Questi numeri assumono ZERO produzione solare. Se una soluzione per il SolarEdge in island mode viene implementata, l'autonomia effettiva sarebbe MOLTO maggiore (potenzialmente infinita con sole).

---

## 6. Confronto Soluzioni

| Soluzione | Fattibilita | Costo | Tempo | PV in Island | Rischio | Raccomandazione |
|---|---|---|---|---|---|---|
| **A: PV diretto su Deye** | ALTA | 200-2.000 EUR | 1 giorno | 2-5 kWp | BASSO | **SI - Primo step** |
| **B: Fronius al posto di SE** | ALTA | 2.000-4.000 EUR | 2-3 giorni | 10 kWp | MEDIO | **SI - Soluzione completa** |
| **C: SE Backup Interface** | BASSA | 2.500-4.500 EUR | 3-5 giorni | 10 kWp | ALTO | **NO** |
| **D: Ricablaggio SE** | MOLTO BASSA | 500 EUR | 1 giorno | 0 kWp (non funziona) | ALTO | **NO** |
| **E: Solo batterie** | ALTA | 1.200-3.600 EUR | 1 giorno | 0 kWp | BASSO | **Piano B** |

---

## 7. Raccomandazione Operativa

### IMMEDIATO (oggi/domani)

**Non c'e nulla che puoi fare ORA per far produrre i pannelli in off-grid.** E un limite architetturale, non un errore di configurazione.

Azioni immediate:
1. **Riconnetti il contatore Enel** - I pannelli riprenderanno a produrre normalmente
2. **Verifica lo stato della batteria** - Dopo il test, controlla il SOC e assicurati che sia sopra il 20%
3. **Nessuna modifica alla configurazione** - Il sistema funziona correttamente, e il SolarEdge che non collabora

### BREVE TERMINE (1-4 settimane)

**Attiva "Signal Island Mode" sul Deye** per predisporre il contatto G-valve:
- Menu: Advanced Function → Signal Island Mode → **Enable**
- Questo attiva il contatto secco CN2 (pin 3,4) in off-grid mode
- Non cambia nulla finche non c'e un dispositivo che usa il segnale
- Ma e un prerequisito per la Soluzione B (Fronius)

**Verifica la fattibilita della Soluzione A** (PV diretto su Deye):
- Quanti pannelli ci sono? Sono tutti con ottimizzatori SolarEdge?
- C'e spazio sul tetto per 2-3 pannelli nuovi SENZA ottimizzatori?
- Il cablaggio DC dal tetto al Deye e fattibile?

### MEDIO TERMINE (1-3 mesi)

**Scegliere tra Soluzione A e Soluzione B**:

| Se... | Allora... |
|---|---|
| Vuoi una soluzione economica e veloce | **Soluzione A**: Aggiungi 2-4 pannelli (1.5-2 kWp) direttamente sul Deye |
| Vuoi la soluzione completa (tutti i 10 kWp in island) | **Soluzione B**: Sostituisci il SolarEdge con un Fronius trifase |
| Non vuoi modificare nulla | **Soluzione E**: Aggiungi batterie e accetta l'autonomia limitata |

### Configurazione Consigliata: Soluzione A + E (Ibrida)

La combinazione piu pratica e conveniente:

1. **Aggiungi 2-4 pannelli nuovi** (1-2 kWp) direttamente sugli MPPT del Deye → **200-800 EUR**
2. **Aggiungi la 2a batteria** (Battery Queen, 32 kWh totali) → **1.200 EUR**
3. **Risultato**: In blackout hai 1-2 kWp di produzione solare + 32 kWh di batteria
4. **Autonomia**: Con 1.5 kWp di pannelli sul Deye e giornata media, la produzione copre ~5-8 kWh/giorno. Con 32 kWh di batteria e consumi di 18 kWh/giorno, hai **3-5 giorni** di autonomia in inverno.

**Costo totale: ~1.500-2.000 EUR** per una soluzione che rende la casa molto resiliente ai blackout.

---

## 8. Parametro Deye: Verifica "AC Couple Frz High"

Il parametro **AC Couple Frz High** attualmente impostato a **55.00 Hz** e la frequenza a cui il Deye segnala al micro-inverter di spegnersi. Questo valore deve essere coerente con il grid code dell'inverter grid-tied:

- **SolarEdge CEI 0-21**: si spegne sopra 51.5 Hz (protezione HF1)
- **Deye AC Couple Frz High**: 55.00 Hz

Il valore di 55 Hz e troppo alto per il SolarEdge. Se si sostituisse con un Fronius (Soluzione B), il valore andrebbe adattato alle soglie del Fronius in MicroGrid mode.

---

## 9. Implicazioni per la Strategia Off-Grid

### Prima di questa analisi (ipotesi ottimistica)
L'analisi in `offgrid-battery-sizing.md` assumeva che "Se c'e sole, il SolarEdge puo continuare a produrre (se il Deye mantiene la frequenza)". Questa ipotesi era **SBAGLIATA**.

### Dopo questa analisi (realta)
In off-grid/blackout:
- **Produzione PV = 0 kWp** (SolarEdge spento)
- **La casa va SOLO a batteria**
- **L'autonomia dipende ESCLUSIVAMENTE dalla capacita della batteria**
- **Con 16 kWh e 18 kWh/giorno di consumo: autonomia ~14 ore** (batteria piena) oppure **~9 ore** (partendo da 80%)

### Impatto sul dimensionamento batterie
L'analisi in `offgrid-battery-sizing.md` deve essere ricalibrata:

| Scenario | Prima (con PV in island) | Dopo (senza PV in island) | Differenza |
|---|---|---|---|
| 16 kWh, 1 giorno no sole | 0.9 giorni | 0.7 giorni | -22% |
| 32 kWh, 3 giorni no sole | 2.3 giorni | 1.5 giorni | -35% |
| 48 kWh, 5 giorni no sole | 4.1 giorni | 2.4 giorni | -41% |

**La mancanza di PV in island mode riduce drasticamente l'autonomia.** E il motivo principale per cui la Soluzione A (PV diretto su Deye) ha un impatto enorme sul dimensionamento.

### Con Soluzione A implementata (2 kWp su Deye)

| Scenario | Senza PV su Deye | Con 2 kWp su Deye | Miglioramento |
|---|---|---|---|
| 16 kWh, giorno soleggiato invernale | 0.7 giorni | ~1.2 giorni | +71% |
| 32 kWh, 3 giorni misti | 1.5 giorni | ~2.5 giorni | +67% |
| 48 kWh, 5 giorni misti | 2.4 giorni | ~4.0 giorni | +67% |

Anche solo 2 kWp di produzione diretta in island mode cambiano radicalmente la resilienza del sistema.

---

## 10. Riepilogo Tecnico

| Domanda | Risposta |
|---|---|
| Perche il SolarEdge si spegne? | **Anti-islanding CEI 0-21**: rileva che la AC del Deye non e la rete Enel |
| Il SE10K-RWS supporta island mode? | **NO**: non e progettato per backup, manca l'hardware |
| Serve una config specifica in SetApp? | **Non esiste**: non si puo disabilitare l'anti-islanding |
| Serve un contatto ausiliario? | Il Deye ha il G-valve, ma il SE10K-RWS non ha un ingresso per riceverlo |
| Il Deye supporta MicInv in backup? | **SI**: Modo IV AC Couple, AC Couple Frz High, frequency shifting |
| Il Deye puo stabilizzare con SE che produce? | **SI** in teoria (12 kW capacity, freq shifting), ma il SE non produce |
| Limiti di potenza MicInv in backup? | Il Deye gestisce fino a 12 kW continuativi in backup |
| E un limite hardware/normativo? | **Entrambi**: il SE10K-RWS non ha l'hardware per backup, e la CEI 0-21 vieta di disabilitare l'anti-islanding |
| Soluzione migliore immediata? | **Pannelli direttamente sugli MPPT del Deye** (senza ottimizzatori SE) |
| Soluzione completa a medio termine? | **Sostituire il SolarEdge con un Fronius** (MicroGrid mode) |

---

*Fonti: Manuale Deye SUN-5-12K-SG04LP3-EU (sez. 5.9, 5.10, 6), SolarEdge Installation Guide MAN-01-00648-1.3 (cap. 1, 6), Datasheet SE10K-RWS, CEI 0-21, knowledge base Pedemonte*
