# Analisi Energetica - 1 Marzo 2026

> Data analisi: 01/03/2026
> Autore: Electrical Engineer Agent
> Fonte dati: Home Assistant API (sensori Deye Cloud + SolarEdge integration)

---

## 1. Bilancio Energetico della Giornata

### Dati Misurati (contatori hardware Deye + Riemann sum SolarEdge)

| Metrica | Valore | Delta vs 26 Feb |
|---|---|---|
| **Produzione SolarEdge** | **5.3 kWh** | -87% (era 40.1 kWh) |
| **Deye Daily Production (passthrough)** | **5.3 kWh** | -87% |
| **Consumo totale** | **10.4 kWh** | -45% (era 19.0 kWh) |
| Grid Import (giornaliero) | ~0.4 kWh (12.5 -> 12.9) | ~uguale (era 0.41) |
| Grid Export (giornaliero) | ~0.2 kWh (127.8 -> 128.0) | -99% (era 16.8) |
| Battery Charge | ~1.1 kWh (95.6 -> 96.7) | -90% (era 11.4) |
| Battery Discharge | ~5.9 kWh (90.1 -> 96.0) | -39% (era 9.8) |

### KPI Principali

| KPI | Valore | Giudizio |
|---|---|---|
| **Tasso autoconsumo** | **96.2%** | Eccellente (quasi zero export) |
| **Tasso autosufficienza** | **96.2%** | Eccellente |
| **Rapporto export/produzione** | **3.8%** | Ottimo (solo 0.2 kWh persi) |
| **Rapporto import/consumo** | **3.8%** | Buono |
| **Delta SOC giornaliero** | **-29%** (60% -> 31%) | Negativo (batteria in deficit) |

*Autoconsumo = (5.3 - 0.2) / 5.3 = 96.2%*
*Autosufficienza = (10.4 - 0.4) / 10.4 = 96.2%*

---

## 2. Profilo della Giornata

### 2.1 Batteria (andamento SOC)

| Parametro | Valore |
|---|---|
| SOC inizio giornata (23:00 precedente) | 60% |
| SOC a mezzanotte (00:00) | 57% |
| SOC minimo mattina (06:55) | 38% |
| SOC massimo diurno | 41% (raggiunte piu' volte, 09:50-10:40) |
| SOC fine giornata (16:25) | 31% |
| Ciclo notturno (00:00 -> 06:55) | 57% -> 38% = -19% SOC = ~3.2 kWh |

**Osservazione critica**: la batteria non si e' MAI ricaricata significativamente durante il giorno. Il SOC e' oscillato tra 38% e 41% durante le ore solari, per poi riprendere a scendere nel pomeriggio. A fine giornata il SOC e' 31%, in netto deficit rispetto al giorno precedente.

Questo significa che la produzione PV del giorno (5.3 kWh) e' stata **inferiore al consumo** (10.4 kWh), e la differenza e' stata coperta dalla batteria (~5.9 kWh di scarica netta).

### 2.2 Produzione Solare (SolarEdge)

| Fascia oraria | Produzione SE | Potenza media |
|---|---|---|
| 00:00 - 06:40 | 0.0 kWh | 0 W |
| 06:41 - 08:00 | ~0.5 kWh | ~350 W |
| 08:00 - 10:00 | ~1.3 kWh | ~650 W |
| 10:00 - 12:00 | ~1.3 kWh | ~650 W |
| 12:00 - 14:00 | ~1.1 kWh | ~520 W |
| 14:00 - 16:00 | ~1.0 kWh | ~470 W |
| 16:00 - 16:41 | ~0.1 kWh | ~130 W |
| **Totale** | **~5.3 kWh** | |

Potenza massima raggiunta: **~918 W** alle 08:11 (SolarEdge ha capacita' nominale 10 kW).

**Analisi**: la produzione e' stata estremamente bassa per l'impianto. Con un SolarEdge SE10K-RWS, la potenza massima di 918 W rappresenta solo il **9.2% della capacita' nominale**. La produzione totale di 5.3 kWh e' tipica di una giornata molto nuvolosa di inizio marzo.

### 2.3 Consumo

Consumo medio giornaliero: 10.4 kWh / 24h = **~433 W medi**.

| Fascia | Consumo stimato | Note |
|---|---|---|
| Notte (00:00 - 07:00) | ~3.7 kWh | ~350 W medi, consumo base |
| Mattina (07:00 - 12:00) | ~2.7 kWh | Picco a 2759 W alle 08:35 |
| Pomeriggio (12:00 - 17:00) | ~4.0 kWh | Picco a 686 W alle 13:55 |

Picco notevole: **2759 W alle 08:35** - probabilmente boiler/lavatrice/cucina.

### 2.4 Grid Power

La griglia ha oscillato intorno a 7-17 W per la maggior parte della giornata (piccolo prelievo residuo). Momenti di export netto:
- 08:10: -24 W
- 08:40: -191 W (picco produzione mattutina con basso consumo istantaneo)
- 11:15: -96 W
- 13:25: -30 W
- 14:25: -402 W (picco export del giorno)

L'export totale di soli 0.2 kWh conferma che quasi tutta la produzione e' stata autoconsumata.

---

## 3. Confronto con Giornate Precedenti

| Metrica | 23 Feb | 26 Feb | **1 Mar** | Commento |
|---|---|---|---|---|
| Produzione | 34.3 kWh | 40.1 kWh | **5.3 kWh** | Giornata molto nuvolosa |
| Consumo | 13.1 kWh | 19.0 kWh | **10.4 kWh** | Consumo moderato |
| Export | 16.5 kWh | 16.8 kWh | **0.2 kWh** | Quasi zero (niente surplus) |
| Import | 0.05 kWh | 0.41 kWh | **0.4 kWh** | Simile a 26 Feb |
| Autoconsumo | 51.9% | 58.2% | **96.2%** | Alto ma per deficit, non per merito |
| Autosufficienza | 99.6% | 97.8% | **96.2%** | Leggermente peggiore |
| Delta SOC | +11% | +11% | **-29%** | Batteria in forte deficit |

**Nota importante**: il tasso di autoconsumo del 96% e' "falsamente positivo". Non indica efficienza, ma semplicemente che la produzione era cosi' bassa da essere tutta assorbita dai carichi. E' la giornata tipo in cui il sistema dipende completamente dalla batteria e dalla rete.

---

## 4. Analisi Energetica

### 4.1 Bilancio Energetico Dettagliato

```
Produzione PV:        +5.3 kWh
Batteria scarica:     +5.9 kWh (netto: scarica 5.9 - carica 1.1 = 4.8 kWh netti)
Import rete:          +0.4 kWh
                      ─────────
Totale disponibile:   ~10.6 kWh  (≈ consumo 10.4 kWh + perdite inverter)

Consumo casa:         -10.4 kWh
Export rete:          -0.2 kWh
```

### 4.2 Efficienza del Sistema

La batteria ha erogato 5.9 kWh e assorbito 1.1 kWh (ciclo parziale). L'import da rete e' stato contenuto a 0.4 kWh nonostante la bassa produzione, grazie all'accumulo in batteria.

**Round-trip efficiency batteria**: non calcolabile su singolo giorno (ciclo incompleto). Dai contatori cumulativi: carica totale 96.7 kWh, scarica totale 96.0 kWh → efficienza apparente ~99% (ma i contatori potrebbero non essere perfettamente sincronizzati o resettati).

### 4.3 Previsione Notte 1-2 Marzo

Con SOC al 31% (ultimo dato ore 16:25) e Batt Low al 15%:
- SOC utilizzabile: 31% - 15% = 16% = ~2.7 kWh
- Consumo notturno stimato (a 350 W medi): ~4.9 kWh (14 ore, 17:00-07:00)
- **Deficit atteso: ~2.2 kWh da prelevare dalla rete** (circa 6-7 ore di prelievo rete)
- Costo stimato: ~0.55 EUR

Se il SOC continua a scendere nel pomeriggio (tendenza in atto), la batteria potrebbe raggiungere il Batt Low prima di mezzanotte.

---

## 5. Giudizio Complessivo

### Rating: SUFFICIENTE (5/10)

**Punti di forza:**
- Autoconsumo massimo della poca produzione disponibile (96.2%)
- Import contenuto a soli 0.4 kWh nonostante la bassa produzione
- La batteria ha compensato efficacemente il deficit di produzione
- Il sistema ha funzionato correttamente in modalita' "batteria-centrica"

**Punti di debolezza:**
- Produzione PV molto bassa (5.3 kWh vs 40 kWh possibili) - giornata nuvolosa
- SOC in forte calo (-29%), la batteria entra nella notte gia' scarica
- Notte successiva non coperta dalla batteria (servira' ~2.2 kWh da rete)
- Potenza PV massima solo 918 W su 10 kW disponibili (9.2%)

**Giudizio**: giornata tipica invernale nuvolosa. Il sistema ha fatto il suo meglio con le risorse disponibili. Non ci sono inefficienze evidenti - il problema e' semplicemente la mancanza di sole. La batteria da 16 kWh ha permesso di mantenere l'autosufficienza al 96% nonostante una produzione pari al 13% della capacita' dell'impianto.

---

## 6. Raccomandazioni

### 6.1 Per Giornate Nuvolose Come Questa

1. **Ridurre consumi differibili**: in giornate con previsione nuvolosa, evitare carichi pesanti (il picco di 2759 W alle 08:35 ha accelerato la scarica della batteria)
2. **Automazione HA "meteo-consapevole"**: creare un'automazione che, in base alle previsioni meteo, regoli il comportamento dei carichi differibili. Se domani e' nuvoloso, preferire il risparmio di batteria
3. **Pre-carica notturna dalla rete**: in F3 (notte/weekend, ~0.20 EUR/kWh) si potrebbe ricaricare parzialmente la batteria dalla rete per evitare di rimanere scoperti. Questo ha senso solo se la tariffa F3 e' significativamente inferiore alla F1

### 6.2 Strategiche (conferma analisi precedenti)

1. **Meter al POD** (priorita' alta): permetterebbe al Deye di gestire attivamente i flussi, inclusa la possibilita' di caricare la batteria dalla rete in fasce convenienti
2. **Time-shifting carichi** nelle giornate soleggiate rimane la priorita' #1 per il risparmio annuale
3. **Seconda batteria**: il valore della seconda batteria e' confermato. In giornate nuvolose come questa, 32 kWh coprirebbero 2 notti intere a 350 W (vs 1 notte incompleta con 16 kWh)

### 6.3 Rischio Batteria Scarica

Con SOC al 31% e tendenza in calo, se domani (2 marzo) e' ancora nuvoloso:
- La batteria iniziera' la giornata al 15% (Batt Low) o meno
- Il Deye passera' alla rete gia' dalla prima mattina
- Se la produzione resta bassa, l'import dalla rete potrebbe essere 5-8 kWh
- Costo: ~1.25-2.00 EUR per la giornata

Questo e' il comportamento corretto del sistema: la rete fa da backup quando il PV e' insufficiente. Il costo e' contenuto.

---

## 7. Riepilogo per il Team Lead

La giornata del 1 marzo 2026 e' stata una giornata nuvolosa tipica invernale:
- **Produzione**: 5.3 kWh (13% della capacita') - giornata molto nuvolosa
- **Consumo**: 10.4 kWh - moderato
- **Bilancio**: negativo, la batteria ha coperto il deficit (-4.8 kWh netti)
- **SOC**: da 60% a 31%, la notte successiva richiedera' ~2.2 kWh dalla rete
- **Autoconsumo**: 96.2% (ottimo, ma per mancanza di surplus, non per efficienza)
- **Import**: 0.4 kWh (contenuto grazie alla batteria)
- **Nessuna inefficienza rilevata**: il sistema ha funzionato correttamente

Il confronto con il 26 febbraio (giornata soleggiata, 40.1 kWh di produzione) mostra la forte variabilita' stagionale. Il sistema e' dimensionato per gestire entrambi gli estremi, ma nelle giornate nuvolose consecutive la rete diventa necessaria.

---

*Formule usate:*
- *Autoconsumo = (Produzione - Export) / Produzione = (5.3 - 0.2) / 5.3 = 96.2%*
- *Autosufficienza = (Consumo - Import) / Consumo = (10.4 - 0.4) / 10.4 = 96.2%*
- *SOC per kWh: ~0.171 kWh per 1% SOC (misurato il 22/02)*
- *Prezzi: Import 0.25 EUR/kWh (F1), Export 0.08 EUR/kWh (SSP/RD medio)*
