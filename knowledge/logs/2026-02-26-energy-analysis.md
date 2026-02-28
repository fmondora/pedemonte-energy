# Analisi Energetica - 26 Febbraio 2026

> Data analisi: 27/02/2026
> Autore: Electrical Engineer Agent
> Fonte dati: PlantsDetails-History-26-feb-2026.xlsx (282 data points, 5 min interval)

---

## 1. Bilancio Energetico della Giornata

| Metrica | Valore |
|---|---|
| **Produzione totale** | **40.11 kWh** |
| Consumo totale | 19.04 kWh |
| Export in rete | 16.77 kWh |
| Import da rete | 0.41 kWh |
| Scarica batteria | 9.75 kWh |
| Carica batteria | 11.42 kWh |
| Energia autoconsumata | 23.34 kWh |

### KPI Principali

| KPI | Valore | Giudizio |
|---|---|---|
| **Tasso autoconsumo** | **58.2%** | Migliorabile (troppo export) |
| **Tasso autosufficienza** | **97.8%** | Eccellente (quasi zero import) |
| **Rapporto export/produzione** | **41.8%** | Alto (quasi meta' della produzione persa) |
| **Rapporto import/consumo** | **2.2%** | Ottimo |
| **Delta SOC giornaliero** | **+11%** (55% -> 66%) | Positivo (batteria piu' carica a fine giornata) |

---

## 2. Profilo della Giornata

### Batteria

| Parametro | Valore |
|---|---|
| SOC inizio (00:00) | 55% |
| SOC minimo | 30% (ore ~08:00) |
| SOC massimo | 100% |
| SOC fine (24:00) | 66% |
| Batteria piena | 12:55 - 17:25 (4.5 ore) |

La batteria e' partita al 55% e si e' scaricata al 30% durante la notte (25% di SOC usato = ~4.3 kWh). Il Batt Low e' impostato a 15%, quindi la batteria aveva ancora margine. La ricarica solare e' iniziata verso le 09:00 e la batteria era piena alle 12:55. E' rimasta piena per **4.5 ore** durante le quali tutto il surplus e' andato in rete.

### Produzione e Export

| Fascia oraria | Produzione | Consumo | Export |
|---|---|---|---|
| Notte (00-07) | 0.00 kWh | 2.73 kWh | 0.01 kWh |
| Mattina (07-12) | 13.81 kWh | 5.16 kWh | 0.12 kWh |
| Pranzo (12-14) | 12.90 kWh | 2.58 kWh | 6.99 kWh |
| Pomeriggio (14-17) | 12.72 kWh | 3.00 kWh | 9.47 kWh |
| Sera (17-21) | 0.68 kWh | 4.54 kWh | 0.17 kWh |
| Notte (21-24) | 0.00 kWh | 1.01 kWh | 0.00 kWh |

**Osservazione chiave**: il 98% dell'export (16.46 kWh su 16.77) avviene tra le 12:00 e le 17:00, con il picco tra le 13:00 e le 14:00 (6.10 kWh in una sola ora).

- Picco export: **6.25 kW** alle 13:20
- Ore di export significativo (>0.1 kW): **4.8 ore**
- Potenza media durante export: **3.96 kW**

### Picchi di Consumo

| Ora | Potenza | Fonte alimentazione | Probabile carico |
|---|---|---|---|
| 18:15-18:20 | 5.38-5.44 kW | Batteria (5.1 kW) + Rete (0.5 kW) | Cucina/riscaldamento serale |
| 14:40 | 4.69 kW | PV (5.8 kW) | Elettrodomestico pomeridiano |
| 12:30 | 4.55 kW | PV (6.4 kW) | Cucina pranzo |
| 11:00-11:20 | 3.00-3.04 kW | PV (5.3-5.6 kW) + Rete (0.3 kW) | Carico mattutino |
| 08:50-09:05 | ~2.8 kW | PV + Batteria | Carico mattutino |
| 20:10-20:20 | ~2.5 kW | Batteria | Serata |

**Nota**: il picco serale 18:15-18:20 (5.4 kW) e' significativo perche' avviene dopo il tramonto e drena rapidamente la batteria. In quei 15 minuti la batteria ha perso ~10% SOC.

---

## 3. Analisi Autoconsumo (58.2%)

### E' buono il 58.2%?

Per un impianto fotovoltaico residenziale **senza accumulo**, un autoconsumo tipico in Italia e' il 25-35%. Con un accumulo da 16 kWh, ci si aspetta 60-80%.

Il 58.2% e' **sotto la media attesa** per un impianto con 16 kWh di batteria. Questo perche':

1. **La produzione e' stata eccezionale** per febbraio (40.11 kWh - una giornata quasi estiva)
2. **La batteria era piena a meta' giornata** e per 4.5 ore tutto il surplus e' andato in rete
3. **Il consumo di 19 kWh e' moderato** per una casa, soprattutto nel pomeriggio

### Confronto con il 23 Febbraio

| Metrica | 23 Feb | 26 Feb | Delta |
|---|---|---|---|
| Produzione | 34.26 kWh | 40.11 kWh | +17% |
| Consumo | 13.06 kWh | 19.04 kWh | +46% |
| Export | 16.49 kWh | 16.77 kWh | +1.7% |
| Import | 0.05 kWh | 0.41 kWh | +720% |
| Autoconsumo | 51.9% | 58.2% | +6.3 pp |
| Autosufficienza | 99.6% | 97.8% | -1.8 pp |

Il confronto rivela un **problema strutturale**: nonostante produzione diversa (+17%), l'export e' quasi identico (~16.5-16.8 kWh). La batteria si riempie comunque verso le 13:00 e il pomeriggio finisce tutto in rete. Il 26 Feb ha autoconsumo migliore solo perche' il consumo era piu' alto (+46%).

---

## 4. Analisi Economica

### Valori del 26 Febbraio

| Voce | Valore |
|---|---|
| Costo import (0.41 kWh x 0.25 EUR/kWh) | 0.10 EUR |
| Ricavo export SSP (16.77 kWh x 0.08 EUR/kWh) | 1.34 EUR |
| Risparmio autoconsumo (23.34 kWh x 0.25 EUR/kWh) | 5.84 EUR |
| **Valore economico netto della giornata** | **7.08 EUR** |

### Mancato Risparmio per Export

L'energia esportata (16.77 kWh) viene valorizzata a ~0.08 EUR/kWh (Ritiro Dedicato / SSP medio), ma se fosse stata autoconsumata varrebbe 0.25 EUR/kWh.

| Calcolo | Valore |
|---|---|
| Valore export al prezzo SSP | 1.34 EUR |
| Valore se autoconsumata | 4.19 EUR |
| **Mancato risparmio** | **2.85 EUR** |

Su base annua, considerando ~180 giornate solari simili (con fattore correttivo 0.6 per giornate meno produttive):

**Mancato risparmio annuo stimato: ~308 EUR**

---

## 5. Strategie di Miglioramento

### 5.1 Time-Shifting dei Carichi (Impatto: ALTO)

La finestra di surplus solare con batteria piena va dalle **12:55 alle 17:25**. Potenza media disponibile: **~4 kW**, picco **6.25 kW**.

| Carico | Potenza | Durata | Energia | Risparmio/uso |
|---|---|---|---|---|
| Lavatrice | 1.5-2.0 kW | 2 ore | 3-4 kWh | 0.75-1.00 EUR |
| Lavastoviglie | 1.5-2.0 kW | 1.5 ore | 2.5-3 kWh | 0.63-0.75 EUR |
| Boiler elettrico | 1.5-2.0 kW | 2-3 ore | 3-6 kWh | 0.75-1.50 EUR |
| Asciugatrice | 2.0-2.5 kW | 2 ore | 4-5 kWh | 1.00-1.25 EUR |
| EV (se presente) | 3.7 kW | variabile | fino a 10+ kWh | 2.50+ EUR |

**Raccomandazione**: spostare lavatrice, lavastoviglie e boiler nella fascia 13:00-17:00 potrebbe assorbire 8-13 kWh di surplus, riducendo l'export del 50-80%.

**Impatto stimato**:
- Autoconsumo: 58.2% -> 75-85%
- Export: 16.77 kWh -> 4-9 kWh
- Risparmio aggiuntivo: 1.40-2.20 EUR/giorno

**Implementazione**: automazione Home Assistant con timer che avviano gli elettrodomestici smart quando SOC = 100% e produzione > consumo + 2 kW.

### 5.2 Pre-riscaldamento con Accumulo Termico (Impatto: MEDIO)

Il picco serale (18:15, 5.4 kW) sembra legato al riscaldamento. Se la pompa di calore o il riscaldamento elettrico viene avviato alle 15:00-16:00 (quando c'e' surplus), la casa accumula calore e riduce il picco serale.

**Impatto stimato**:
- Riduzione picco serale: 5.4 kW -> 3-4 kW
- Energia spostata: ~2-3 kWh
- Risparmio: 0.34-0.51 EUR/giorno

### 5.3 Seconda Batteria (Impatto: ALTO)

| Parametro | Valore |
|---|---|
| Costo 2a batteria 16 kWh (Battery Queen) | **1.200 EUR** |
| Export giornaliero assorbibile | ~16 kWh |
| Risparmio giornaliero | 2.85 EUR (giorno ottimale) |
| Risparmio annuo stimato | ~308 EUR |
| **Payback period** | **~3.9 anni** |
| Vita utile LiFePO4 | 15-20+ anni |
| **Guadagno netto ciclo vita** | **~3.700 - 4.900 EUR** |

**Giudizio: CONSIGLIATA.** Con un payback sotto i 4 anni e una vita utile di 15-20 anni, la seconda batteria e' un investimento eccellente. Dopo il payback, il risparmio netto stimato e' di 3.700-4.900 EUR.

Con 32 kWh di accumulo totale:
- L'export si ridurrebbe quasi a zero nelle giornate come il 26/02
- Autoconsumo: 58% -> 90%+
- La casa sarebbe quasi completamente off-grid anche in giornate di alta produzione
- Maggiore autonomia notturna (2 notti intere a 0.40 kW)

**Nota**: la seconda batteria e' complementare al time-shifting, non alternativa. Idealmente entrambe le strategie vanno implementate.

### 5.4 Installazione Meter al POD (Impatto: MEDIO)

Come gia' segnalato nell'architettura, il Deye opera senza meter al POD (Meter Select = No Meter). Questo impedisce le funzionalita' Selling First e Zero Export di funzionare correttamente. Con un meter:

- Il Deye potrebbe gestire attivamente l'export
- Possibilita' di limitare l'export a zero o a un valore target
- Migliore coordinamento con il SolarEdge

---

## 6. Giudizio Complessivo sulla Giornata

### Rating: BUONA (7/10)

**Punti di forza:**
- Autosufficienza eccellente (97.8% - praticamente off-grid)
- Import quasi nullo (0.41 kWh, 0.10 EUR)
- Produzione eccezionale per febbraio (40.11 kWh)
- Batteria chiude la giornata con +11% SOC (66% vs 55%)
- Picchi di consumo gestiti senza problemi

**Punti di debolezza:**
- 16.77 kWh esportati (41.8% della produzione "persi" a 0.08 EUR/kWh)
- Autoconsumo 58.2% sotto la media attesa (60-80%) per impianto con batteria
- 4.5 ore di batteria piena con surplus in rete
- Nessun time-shifting dei carichi osservato
- Il picco serale (5.4 kW) ha richiesto 0.5 kW da rete

### Cosa ha funzionato bene
1. La batteria ha coperto completamente la notte (55% -> 30%) senza ricorrere alla rete
2. La ricarica solare e' stata rapida (30% -> 100% in ~4 ore)
3. I carichi di pranzo (12:00-12:45, ~4 kW) sono stati assorbiti dal PV senza toccare la batteria
4. Il SOC a fine giornata (66%) garantisce una notte successiva coperta

### Cosa si puo' migliorare
1. **Spostare lavatrice/lavastoviglie tra le 13:00 e le 17:00** - impatto immediato, costo zero
2. **Pre-riscaldare la casa alle 15:00-16:00** per ridurre il picco serale
3. **Installare un meter al POD** per permettere al Deye di gestire l'export
4. **Automazione HA** per time-shifting automatico dei carichi basato su SOC e produzione

---

## 7. Prossimi Passi

1. **Priorita' 1 - Time-shifting**: creare automazioni HA che avviano carichi differibili quando SOC = 100% e surplus > 2 kW (coinvolgere homeassistant-expert e domotica-expert)
2. **Priorita' 2 - Meter al POD**: discutere con installatore (Davide Duca) installazione DTSU666
3. **Priorita' 3 - Monitoraggio**: raccogliere dati per almeno 7 giorni consecutivi per confermare il pattern
4. **Priorita' 4 - Analisi carichi**: identificare esattamente quali elettrodomestici causano i picchi (18:15, 14:40, 12:30)

---

## 8. Confronto Storico

| Metrica | 23 Feb | 26 Feb | Trend |
|---|---|---|---|
| Produzione | 34.26 kWh | 40.11 kWh | +17% (giornata piu' soleggiata) |
| Consumo | 13.06 kWh | 19.04 kWh | +46% (piu' attivita') |
| Export | 16.49 kWh | 16.77 kWh | ~stabile (problema strutturale) |
| Import | 0.05 kWh | 0.41 kWh | +0.36 kWh (picco serale) |
| Autoconsumo | 51.9% | 58.2% | +6.3pp (per maggior consumo) |
| Autosufficienza | 99.6% | 97.8% | -1.8pp (picco serale non coperto) |

**Conclusione strutturale**: l'export di ~16.5 kWh e' un dato costante indipendente dalla produzione (34 o 40 kWh). Questo indica che la **capacita' di assorbimento** del sistema (batteria + carichi) e' il collo di bottiglia, non la produzione. L'unico modo per ridurre l'export e' aumentare il consumo nelle ore di surplus tramite time-shifting dei carichi.

---

*Formule usate:*
- *Autoconsumo = (Produzione - Export) / Produzione = (40.11 - 16.77) / 40.11 = 58.2%*
- *Autosufficienza = (Consumo - Import) / Consumo = (19.04 - 0.41) / 19.04 = 97.8%*
- *Prezzi: Import 0.25 EUR/kWh (F1), Export 0.08 EUR/kWh (SSP/RD medio)*
