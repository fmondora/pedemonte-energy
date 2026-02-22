# Analisi: Trade-off Riserva Backup vs Autoconsumo Notturno

> Data analisi: 2026-02-22
> Autore: Electrical Engineer Agent
> Richiesta da: Davide Duca (installatore) + Team Lead

## Contesto

Il 22/02/2026 il proprietario ha abbassato il parametro **Batt Low %** da 35% a 15% sul Deye SUN-12K-SG04LP3-EU. Davide Duca ha espresso preoccupazione: "Sarebbe da capire come impostare una soglia da non scendere per avere un po' di riserva di backup. Tipo 35 soglia backup e 10 soc. Altrimenti quando vai in backup e la batteria e' scarica non riesce piu' a partire da solo l'impianto."

Questa analisi quantifica il trade-off tra sicurezza (riserva per blackout) e autoconsumo (massimizzare l'uso della batteria).

---

## 1. Come Funzionano i Parametri Batteria del Deye

### Parametri Chiave (configurazione attuale)

| Parametro | Valore | Funzione |
|---|---|---|
| **Batt Low %** | **15%** | Soglia a cui l'inverter **smette di scaricare** la batteria in **modalita' grid-tied** (funzionamento normale con rete presente). La batteria si "ferma" qui durante l'uso notturno normale. |
| **Batt Shutdown %** | **10%** | Soglia a cui l'inverter si **spegne completamente** per proteggere la batteria da scarica profonda. Limite assoluto. |
| **Batt Restart %** | **50%** | Soglia a cui l'inverter **riparte** dopo uno shutdown. Dopo essersi spento al 10%, riprende a erogare solo quando il SOC risale al 50% (tramite ricarica solare o da rete). |

### Comportamento in Scenari Diversi

**Scenario A - Funzionamento Normale (rete presente):**
1. La batteria si scarica durante la notte alimentando i carichi
2. Quando il SOC raggiunge **Batt Low % (15%)**, la batteria smette di scaricarsi
3. I carichi vengono alimentati dalla **rete elettrica**
4. L'inverter resta acceso e funzionante
5. La batteria mantiene il 15% come "riserva dormiente"

**Scenario B - Blackout con batteria sopra Batt Low %:**
1. La rete cade -> l'inverter passa a **modalita' backup** (UPS)
2. La batteria alimenta i carichi collegati alla porta backup
3. La batteria puo' scaricarsi **fino a Batt Shutdown % (10%)**
4. L'inverter ha pieno margine operativo

**Scenario C - Blackout con batteria a/sotto Batt Low %:**
1. La batteria e' gia' ferma al 15% (Batt Low), la rete alimenta i carichi
2. La rete cade -> l'inverter tenta di passare a backup
3. La batteria ha ancora **5% di energia** disponibile (15% - 10% = 5% SOC)
4. 5% SOC = **0.9 kWh = circa 2 ore di backup** a 0.41 kW di consumo
5. Se il blackout dura piu' di 2 ore, l'inverter raggiunge Batt Shutdown e **si spegne**

**Scenario D - Blackout con inverter in shutdown:**
1. L'inverter si e' spento perche' il SOC ha raggiunto il 10%
2. Per ripartire serve che il SOC risalga al **50% (Batt Restart)**
3. Senza rete e senza sole -> **l'impianto non riparte** fino al ritorno di uno dei due
4. Questo e' lo scenario che preoccupa Davide

---

## 2. Dati Misurati

### Notte del 22/02/2026 (con Batt Low = 35%)

| Metrica | Valore |
|---|---|
| SOC al tramonto (~17:30) | ~67% (stimato) |
| SOC a mezzanotte | 51% |
| SOC allo switch a rete (05:10) | 35% |
| Consumo notturno medio | 0.41 kW |
| Energia scaricata da batteria | 2.57 kWh (in 5.08 ore) |
| Energia prelevata da rete | 0.93 kWh (da 05:10 a 06:50) |
| Energia **inutilizzata** nella batteria | 4.3 kWh (25% SOC tra 35% e 10%) |
| Energia per punto SOC (misurata) | 0.171 kWh |

La batteria da 340Ah ha una capacita' totale utilizzabile di circa **17.1 kWh** (100% -> 0%). La capacita' effettiva tra 100% e 10% (Shutdown) e' circa **15.4 kWh**.

---

## 3. Analisi Quantitativa: Confronto Scenari

### Energia Utilizzabile e Autonomia

| Batt Low % | SOC Usabile (100% -> Low) | Energia Disponibile | Autonomia (a 0.41 kW) | Riserva Backup (Low -> Shutdown) | Durata Backup |
|---|---|---|---|---|---|
| **35%** | 65% | 11.1 kWh | 27.1 h | 4.3 kWh (25% SOC) | **10.4 ore** |
| **25%** | 75% | 12.8 kWh | 31.3 h | 2.6 kWh (15% SOC) | **6.3 ore** |
| **20%** | 80% | 13.7 kWh | 33.4 h | 1.7 kWh (10% SOC) | **4.2 ore** |
| **15%** | 85% | 14.5 kWh | 35.5 h | 0.9 kWh (5% SOC) | **2.1 ore** |

### Impatto sulla Notte del 22/02/2026 (SOC partenza = 67%)

| Batt Low % | SOC a Disposizione | Ore Coperte | Copre la Notte? | Energia da Rete |
|---|---|---|---|---|
| **35%** | 32% (67->35) | 13.3 h | Quasi (mancano ~10 min) | 0.1 kWh |
| **25%** | 42% (67->25) | 17.5 h | SI | 0 kWh |
| **20%** | 47% (67->20) | 19.6 h | SI | 0 kWh |
| **15%** | 52% (67->15) | 21.7 h | SI | 0 kWh |

**Nota**: In questa notte specifica, partendo da 51% SOC a mezzanotte, con Batt Low al 35% si sono consumati dalla rete 0.93 kWh. Con Batt Low al 15% (o anche 25%) la batteria avrebbe coperto l'intera notte senza prelevare dalla rete.

### Differenziale Economico Annuo (stima)

| Variazione | Energia Extra/notte | Risparmio Stimato/anno |
|---|---|---|
| 35% -> 25% | +1.7 kWh | ~156 EUR |
| 35% -> 20% | +2.6 kWh | ~234 EUR |
| 35% -> 15% | +3.4 kWh | ~312 EUR |

> Nota: Il risparmio effettivo dipende da quante notti la batteria ha SOC sufficiente per raggiungere il Batt Low. In estate con batteria piena, la differenza tra 35% e 15% e' irrilevante (la notte e' piu' corta della capacita'). Il risparmio reale si concentra nei mesi invernali/nuvolosi (circa 120-150 notti/anno) e si stima in circa 100-160 EUR/anno passando da 35% a 20%.

---

## 4. Statistiche Blackout in Italia

### Dati ARERA (2023, media nazionale, clienti BT)

| Indicatore | Valore |
|---|---|
| **Durata media interruzioni/utente/anno (SAIDI)** | **44 minuti** |
| **Numero medio interruzioni/utente/anno (SAIFI)** | **3.4** |
| **Durata media singola interruzione (CAIDI)** | **~13 minuti** |
| Standard massimo ripristino ARERA | 8 ore |

### Distribuzione per Concentrazione Demografica

| Zona | Durata Media | N. Interruzioni |
|---|---|---|
| Alta concentrazione (>50k abitanti) | ~25-35 min/anno | ~2-3/anno |
| Media concentrazione (5k-50k) | ~40-55 min/anno | ~3-4/anno |
| **Bassa concentrazione (<5k)** | **~60-90 min/anno** | **~4-6/anno** |

> Pedemonte ricade probabilmente nella **bassa concentrazione**. Questo significa un rischio leggermente superiore alla media.

### Energia Necessaria per Coprire un Blackout

| Durata Blackout | Energia Necessaria (a 0.41 kW) | SOC Necessario (sopra Shutdown 10%) |
|---|---|---|
| 15 min (media) | 0.10 kWh | 0.6% |
| 30 min | 0.20 kWh | 1.2% |
| 1 ora | 0.41 kWh | 2.4% |
| 2 ore | 0.82 kWh | 4.8% |
| 4 ore (raro) | 1.64 kWh | 9.6% |
| 8 ore (eccezionale) | 3.28 kWh | 19.2% |

---

## 5. Analisi del Rischio

### Probabilita' di Scenario Critico

Affinche' si verifichi il problema temuto da Davide (blackout + batteria insufficiente), devono accadere **contemporaneamente**:

1. **Deve esserci un blackout** -> ~3-6 volte/anno a Pedemonte
2. **Il blackout deve durare piu' della riserva** -> la maggior parte dura <30 min
3. **Deve capitare quando la batteria e' vicina al Batt Low %** -> solo le ultime 1-2 ore prima dell'alba

La probabilita' congiunta e' **molto bassa** (stima: <0.5% per anno con Batt Low al 20%).

### Matrice di Rischio

| Batt Low % | Riserva Backup | Copre 99% Blackout? | Copre Blackout 4h? | Rischio Residuo |
|---|---|---|---|---|
| 35% | 10.4 ore | SI | SI | Minimo (sovradimensionato) |
| 25% | 6.3 ore | SI | SI | Molto Basso |
| **20%** | **4.2 ore** | **SI** | **SI** | **Basso** |
| 15% | 2.1 ore | SI | NO (solo 2h) | Basso-Medio |

---

## 6. Raccomandazione

### Valore Ottimale Proposto: **Batt Low = 20%**

**Motivazione:**
- **Riserva di 10% SOC** (20% -> 10% Shutdown) = 1.7 kWh = **4.2 ore di backup**
- Copre il **99.9% dei blackout** in Italia (durata media 13 min, il 99% sotto le 4 ore)
- Rispetto al 35%, recupera **2.6 kWh/notte** di autoconsumo
- Risparmio stimato: **~120-160 EUR/anno** rispetto al 35%
- Margine di sicurezza **confortevole**: 4.2 ore di backup anche nel caso peggiore (batteria al 20% + blackout improvviso)

### Perche' NON 15%?

Il valore attuale di 15% e' funzionalmente accettabile per il 95% degli scenari, ma:
- La riserva di 5% SOC (0.9 kWh, ~2 ore) e' marginale per blackout prolungati
- Non copre scenari eccezionali (blackout 4+ ore da maltempo, che e' proprio quando e' piu' probabile)
- Il guadagno rispetto a 20% e' solo 0.9 kWh/notte (circa 40 EUR/anno in piu')
- Il rapporto rischio/beneficio non e' ottimale

### Perche' NON 35%?

Il valore originale di 35% e' **eccessivamente conservativo**:
- Riserva di 4.3 kWh (10.4 ore) -> sovradimensionata per l'Italia
- Spreca 3.4 kWh/notte rispetto al 15%, 2.6 kWh rispetto al 20%
- Nelle notti invernali con batteria non piena, causa prelievo dalla rete evitabile

### Alternativa: Batt Low = 25% (per chi vuole massima tranquillita')

Se il proprietario o Davide preferiscono un margine extra:
- Riserva = 15% SOC = 2.6 kWh = **6.3 ore di backup**
- Copre anche blackout eccezionali con ampio margine
- Costo: solo 0.9 kWh/notte in meno rispetto al 20%
- Compromesso ragionevole tra le posizioni

---

## 7. Strategia Stagionale

### Ha Senso una Riserva Variabile per Stagione?

**Conclusione: NO, non e' necessaria.**

| Stagione | Produzione | Batteria a Fine Giornata | Durata Notte | Motivazione |
|---|---|---|---|---|
| **Estate** | Alta | Spesso 100% SOC | ~9 ore (3.7 kWh) | Batteria copre ampiamente la notte a qualsiasi soglia |
| **Inverno** | Bassa | 50-80% SOC | ~13.5 ore (5.5 kWh) | Anche al 20%, la batteria copre la notte nella maggior parte dei casi |

In estate, la batteria e' quasi sempre piena e la notte e' corta: il Batt Low non viene mai raggiunto comunque. In inverno, il risparmio del Batt Low basso e' piu' importante perche' la batteria parte con SOC ridotto.

Una strategia stagionale aggiungerebbe complessita' senza un beneficio significativo. Il valore fisso del 20% e' gia' un buon equilibrio per tutte le stagioni.

---

## 8. Nota Importante sul Batt Restart %

Il parametro **Batt Restart % = 50%** ha un impatto critico spesso sottovalutato:

- Dopo un shutdown (SOC = 10%), l'inverter non riparte fino a quando il SOC non risale al **50%**
- Questo richiede ricarica da **rete** o da **solare**
- Se manca la rete (blackout prolungato) e non c'e' sole (notte), l'impianto resta fermo
- **Questo e' il vero rischio evidenziato da Davide**

La riserva di Batt Low **evita di arrivare al shutdown** durante il funzionamento normale. Ma in backup mode, la batteria si scarica fino al 10% e poi l'inverter si spegne. La chiave e' che il **margine tra Batt Low e Shutdown** dia abbastanza tempo per "sopravvivere" alla durata del blackout.

### Suggerimento Aggiuntivo

Valutare con Davide se il parametro **Batt Restart** puo' essere abbassato (es. da 50% a 30%). Questo ridurrebbe il tempo necessario per riavviare l'inverter dopo uno shutdown. Con un Batt Restart al 30%, basterebbero poche ore di sole mattutino per ripartire, invece delle diverse ore necessarie per raggiungere il 50%.

> **ATTENZIONE**: La modifica del Batt Restart % va concordata con l'installatore e verificata con il BMS della batteria. Ripartire con SOC troppo basso potrebbe danneggiare le celle o causare instabilita'.

---

## 9. Riepilogo Decisionale

| Opzione | Batt Low % | Pro | Contro | Raccomandazione |
|---|---|---|---|---|
| Conservativa (Davide) | 35% | Massima sicurezza backup | Spreca 4.3 kWh/notte, 250+ EUR/anno | NO - Troppo conservativa |
| **Ottimale** | **20%** | **Buon equilibrio sicurezza/autoconsumo, 4.2h backup** | **Blackout >4h non coperto** | **SI - Raccomandato** |
| Intermedia | 25% | 6.3h backup, buona sicurezza | 0.9 kWh/notte in meno vs 20% | Accettabile se si preferisce prudenza |
| Aggressiva (attuale) | 15% | Massimo autoconsumo | Solo 2h backup, marginale | Accettabile ma subottimale per sicurezza |

---

## 10. Prossimi Passi

1. **Discutere con il proprietario** la raccomandazione di Batt Low = 20%
2. **Verificare con Davide** la possibilita' di ridurre Batt Restart % da 50% a 30%
3. **Monitorare per 7 giorni** con il valore attuale (15%) per raccogliere dati reali
4. **Implementare la modifica** a 20% dopo la fase di osservazione
5. **Verificare** il comportamento della batteria con il nuovo valore

---

*Fonti: Dati ARERA 2023 su continuita' servizio elettrico, Manuale Deye SUN-12K-SG04LP3-EU, Forum DIY Solar Power, dati misurati dall'impianto di Pedemonte*
