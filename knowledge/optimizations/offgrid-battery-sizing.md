# Dimensionamento Batterie per Autosufficienza Off-Grid

> Data analisi: 27/02/2026
> Autore: Electrical Engineer Agent
> Richiesta da: Team Lead (proprietario vuole valutare off-grid completo)

---

## Dati di Input

| Parametro | Valore | Fonte |
|---|---|---|
| Impianto PV | 10 kWp SolarEdge SE10K-RWS | system-architecture.md |
| Inverter batteria | Deye SUN-12K-SG04LP3-EU | current-config.md |
| Batteria attuale | 1x Battery Queen 51.2V 314Ah (~16 kWh) | current-config.md |
| Costo Battery Queen | 1.200 EUR | analisi 26 feb |
| Produzione annua PVGIS | 13.986 kWh | solar-data-berbenno.md |
| Max accumulo Deye | ~60 kWh (240A max) | second-battery-connection.md |
| Consumo misurato (feb) | 13-19 kWh/giorno | energy-analysis 26 feb |
| Consumo base notturno | 0.38-0.40 kW | energy-analysis 26 feb |
| Prezzo import rete | 0.25 EUR/kWh (F1) | energy-analysis 26 feb |
| Prezzo export SSP/RD | ~0.08 EUR/kWh | energy-analysis 26 feb |

---

## 1. Bilancio Energetico Mensile

### Stima dei Consumi Mensili

I dati misurati di febbraio mostrano 13-19 kWh/giorno. Stimo un profilo annuale considerando:
- Inverno (nov-feb): consumi piu alti per riscaldamento, illuminazione (media ~18 kWh/giorno)
- Mezza stagione (mar-apr, set-ott): consumi medi (~15 kWh/giorno)
- Estate (mag-ago): consumi piu bassi, notti corte, meno riscaldamento (~13 kWh/giorno)

**Consumo annuo stimato: ~5.550 kWh/anno** (media 15.2 kWh/giorno)

### Bilancio Mensile Dettagliato

| Mese | Prod. PV (kWh/mese) | Prod. media (kWh/g) | Consumo stimato (kWh/g) | Consumo mensile (kWh) | Surplus/Deficit (kWh/g) | Surplus mensile (kWh) |
|---|---|---|---|---|---|---|
| Gennaio | 802 | 25.9 | 18 | 558 | **+7.9** | **+244** |
| Febbraio | 1.089 | 38.9 | 18 | 504 | **+20.9** | **+585** |
| Marzo | 1.443 | 46.6 | 15 | 465 | **+31.6** | **+978** |
| Aprile | 1.370 | 45.7 | 14 | 420 | **+31.7** | **+950** |
| Maggio | 1.315 | 42.4 | 13 | 403 | **+29.4** | **+912** |
| Giugno | 1.363 | 45.4 | 13 | 390 | **+32.4** | **+973** |
| Luglio | 1.508 | 48.7 | 13 | 403 | **+35.7** | **+1.105** |
| Agosto | 1.419 | 45.8 | 13 | 403 | **+32.8** | **+1.016** |
| Settembre | 1.249 | 41.6 | 14 | 420 | **+27.6** | **+829** |
| Ottobre | 1.114 | 35.9 | 15 | 465 | **+20.9** | **+649** |
| Novembre | 719 | 24.0 | 18 | 540 | **+6.0** | **+179** |
| Dicembre | 593 | 19.1 | 18 | 558 | **+1.1** | **+35** |
| **TOTALE** | **13.986** | **38.3** | **15.2** | **5.529** | **+23.1** | **+8.457** |

### Osservazioni Critiche sul Bilancio Mensile

**A livello MEDIO mensile, tutti i mesi sono in surplus.** Anche dicembre produce in media 19.1 kWh/giorno contro un consumo di 18 kWh/giorno, con un margine di +1.1 kWh/giorno.

Tuttavia, questa e una **media ingannevole**. Il problema dell'off-grid non e il bilancio medio, ma la **variabilita giornaliera**:

- A dicembre, la media di 19.1 kWh/giorno include giornate da 30+ kWh (sereno) e giornate da 2-5 kWh (neve/nebbia)
- Il deficit si accumula nei periodi di maltempo consecutivo
- La batteria deve colmare il gap tra i giorni "cattivi" e i giorni "buoni"

---

## 2. Analisi del Mese Critico: Dicembre

### Distribuzione Giornaliera Stimata della Produzione

A dicembre, la media PVGIS e 19.1 kWh/giorno. Stimo la distribuzione cosi:

| Tipo di giornata | Produzione (kWh) | Probabilita | N. giorni (su 31) |
|---|---|---|---|
| Sereno | 28-35 | 25% | ~8 |
| Parzialmente nuvoloso | 15-25 | 30% | ~9 |
| Nuvoloso | 5-12 | 25% | ~8 |
| Molto nuvoloso/nebbia | 2-5 | 15% | ~5 |
| Neve sui pannelli | 0-2 | 5% | ~1-2 |

### Scenario Worst Case: 7 Giorni Consecutivi di Maltempo

Questo e lo scenario realistico piu pessimistico per una valle alpina in dicembre:

| Giorno | Condizione | Produzione stimata (kWh) | Consumo (kWh) | Deficit giornaliero (kWh) | Deficit cumulato (kWh) |
|---|---|---|---|---|---|
| 1 | Nebbia + nuvole | 3 | 18 | -15 | -15 |
| 2 | Nebbia + nuvole | 4 | 18 | -14 | -29 |
| 3 | Neve | 1 | 18 | -17 | -46 |
| 4 | Neve residua + nuvole | 2 | 18 | -16 | -62 |
| 5 | Nuvoloso | 6 | 18 | -12 | -74 |
| 6 | Nuvoloso con schiarite | 10 | 18 | -8 | -82 |
| 7 | Parzialmente nuvoloso | 15 | 18 | -3 | -85 |

**Deficit cumulato in 7 giorni di maltempo: ~85 kWh**

Ma attenzione: questo e lo scenario estremo. Uno scenario piu realistico (5 giorni brutti):

| Giorno | Produzione (kWh) | Consumo (kWh) | Deficit (kWh) | Deficit cumulato (kWh) |
|---|---|---|---|---|
| 1 | 4 | 18 | -14 | -14 |
| 2 | 3 | 18 | -15 | -29 |
| 3 | 5 | 18 | -13 | -42 |
| 4 | 8 | 18 | -10 | -52 |
| 5 | 12 | 18 | -6 | -58 |

**Deficit cumulato in 5 giorni: ~58 kWh**

---

## 3. Scenari di Autonomia con Batteria

### Ipotesi di calcolo
- Consumo giornaliero invernale: **18 kWh**
- DOD (Depth of Discharge) utile: **90%** (LiFePO4, da 100% a 10%)
- Produzione residua nei giorni brutti: media **4 kWh/giorno** (conservativa)
- Fabbisogno netto giornaliero nei giorni brutti: **18 - 4 = 14 kWh/giorno**

### Tabella Dimensionamento

| Giorni senza sole | Fabbisogno netto (kWh) | Batteria utile (kWh) | Batteria lorda al 90% DOD (kWh) | N. Battery Queen (~16 kWh) | Costo batterie (EUR) |
|---|---|---|---|---|---|
| 2 giorni | 28 | 28 | 31 | 2 (32 kWh) | 2.400 |
| 3 giorni | 42 | 42 | 47 | 3 (48 kWh) | 3.600 |
| 5 giorni | 70 | 70 | 78 | 5 (80 kWh) | 6.000 |
| 7 giorni | 98 | 98 | 109 | 7 (112 kWh) | 8.400 |

### Con produzione residua zero (worst case assoluto: neve totale)

| Giorni senza sole | Fabbisogno (kWh) | Batteria lorda al 90% DOD (kWh) | N. Battery Queen | Costo (EUR) |
|---|---|---|---|---|
| 2 giorni | 36 | 40 | 3 (48 kWh) | 3.600 |
| 3 giorni | 54 | 60 | 4 (64 kWh) | 4.800 |
| 5 giorni | 90 | 100 | 7 (112 kWh) | 8.400 |
| 7 giorni | 126 | 140 | 9 (144 kWh) | 10.800 |

---

## 4. Limiti del Deye SUN-12K-SG04LP3-EU

### Capacita Massima di Accumulo

| Parametro | Valore |
|---|---|
| Max accumulo dichiarato | ~60 kWh |
| Max corrente batteria | 240A |
| Range tensione | 40-60V |
| Max batterie in parallelo (stima) | 3-4 unita |

### Con 4 Battery Queen in parallelo (massimo ragionevole)

| Parametro | Valore |
|---|---|
| Capacita totale | 4 x 16 = **64 kWh** |
| Capacita Ah | 4 x 314 = **1.256 Ah** |
| Capacita utile (90% DOD) | **57.6 kWh** |
| Corrente per batteria a 240A totali | 60A (molto conservativo) |
| Autonomia a 18 kWh/giorno (senza sole) | **3.2 giorni** |
| Autonomia con 4 kWh/g produzione residua | **4.1 giorni** |
| Costo 4 batterie | **4.800 EUR** (3 nuove + 1 esistente = 3.600 EUR) |

### Cosa succede se servono piu di 60 kWh?

Per superare i ~60 kWh del Deye, le opzioni sono:

1. **Secondo inverter ibrido**: un altro Deye o equivalente (~3.000-5.000 EUR) con le sue batterie
2. **Inverter batteria dedicato**: piu economico, solo per gestire batterie aggiuntive
3. **Sistema modulare**: rack batterie con BMS integrato (Pylontech, BYD, etc.)

Il costo e la complessita aumentano significativamente oltre i 60 kWh.

---

## 5. Analisi Economica: Off-Grid vs Grid-Tied

### Stima Costi e Ricavi Attuali (Grid-Tied con 1 batteria)

| Voce | Stima Annua | Note |
|---|---|---|
| Consumo totale casa | 5.550 kWh | ~15.2 kWh/giorno medio |
| Produzione PV | 13.986 kWh | Da PVGIS |
| Autoconsumo diretto + batteria | ~4.500 kWh | Stima ~80% dei consumi |
| Import da rete | ~1.050 kWh | ~20% dei consumi |
| Export in rete | ~9.486 kWh | Surplus non utilizzato |
| **Costo import** | **~263 EUR** | 1.050 kWh x 0.25 EUR |
| **Ricavo export (SSP/RD)** | **~759 EUR** | 9.486 kWh x 0.08 EUR |
| **Costi fissi contatore** | **~120 EUR/anno** | Quota fissa Enel + oneri di sistema |
| **Bolletta netta stimata** | **~-376 EUR** | Il ricavo SSP supera import + fissi |

**Nota importante**: con il SSP, la casa e gia in credito. Il conto economico e positivo.

### Scenario Off-Grid Completo

| Voce | Costo | Note |
|---|---|---|
| Batterie necessarie (5 gg autonomia) | 5x Battery Queen = 80 kWh | 4 nuove a 1.200 EUR |
| Ma il Deye gestisce max ~60 kWh | Serve secondo inverter | |
| Costo batterie (opzione max Deye) | 3.600 EUR (3 nuove) | 4 totali = 64 kWh |
| Costo batterie (5 gg reale) | 4.800 EUR + secondo inverter ~4.000 EUR | |
| **Totale investimento off-grid (opz. 64 kWh)** | **~3.600 EUR** | Solo batterie, senza secondo inverter |
| **Totale investimento off-grid (opz. 80 kWh)** | **~8.800 EUR** | Batterie + secondo inverter |
| Si perde: ricavo SSP/RD | -759 EUR/anno | Non si vende piu alla rete |
| Si risparmia: costi fissi contatore | +120 EUR/anno | Niente piu contatore Enel |
| Si risparmia: import da rete | +263 EUR/anno | Niente piu bollette |
| **Risparmio netto annuo off-grid** | **-376 EUR/anno** | Si PERDE denaro staccandosi dalla rete |

### Confronto Economico su 15 Anni

| Scenario | Investimento | Risparmio annuo netto | Costo/Guadagno su 15 anni |
|---|---|---|---|
| **Grid-tied (attuale, 1 batt)** | 0 EUR | +376 EUR/anno | **+5.640 EUR** |
| **Grid-tied + 2a batteria** | 1.200 EUR | +530 EUR/anno (*) | **+6.750 EUR** |
| **Off-grid (64 kWh, Deye solo)** | 3.600 EUR | -376 EUR/anno | **-9.240 EUR** |
| **Off-grid (80 kWh, 2 inverter)** | 8.800 EUR | -376 EUR/anno | **-14.440 EUR** |
| **Quasi off-grid (64 kWh, contatore backup)** | 3.600 EUR | +376 EUR/anno (**) | **+2.040 EUR** |

(*) La 2a batteria riduce l'import e aumenta l'autoconsumo di ~155 EUR/anno rispetto all'attuale.
(**) Si mantiene il contatore per vendere il surplus e come backup; le batterie servono per massimizzare l'autoconsumo.

### Risultato Chiave dell'Analisi Economica

**L'off-grid completo e economicamente SVANTAGGIOSO.** Il motivo e semplice:

1. La casa produce il **252% dei consumi** (13.986 vs 5.550 kWh). Il surplus e enorme.
2. Staccandosi dalla rete, si **perde il ricavo SSP/RD** di ~759 EUR/anno.
3. Il risparmio della bolletta (~383 EUR/anno di import + fissi) e **inferiore** al ricavo SSP perso.
4. Il risultato netto e una **perdita di ~376 EUR/anno** oltre all'investimento in batterie.

---

## 6. Scenario "Quasi Off-Grid" (RACCOMANDATO)

### Concetto

Mantenere il contatore Enel come backup e per vendere il surplus, ma dimensionare le batterie per avere massima autosufficienza (import quasi zero, export solo il surplus che non entra nelle batterie).

### Configurazione Consigliata: 3 Battery Queen (48 kWh totali)

| Parametro | Valore |
|---|---|
| Batterie | 3x Battery Queen 51.2V 314Ah |
| Capacita totale | 48 kWh |
| Capacita utile (90% DOD) | 43.2 kWh |
| Capacita Ah totale | 942 Ah |
| Corrente per batteria (a 240A max) | 80A (conservativo) |
| Costo (2 nuove + 1 esistente) | **2.400 EUR** |
| Entro limiti Deye | SI (~48 kWh < 60 kWh max) |

### Prestazioni Attese

| Metrica | Attuale (16 kWh) | Con 48 kWh | Miglioramento |
|---|---|---|---|
| Autonomia senza sole | ~0.7 giorni | **~2.4 giorni** | +240% |
| Autonomia con prod. residua 4 kWh/g | ~0.9 giorni | **~3.1 giorni** | +244% |
| Import annuo da rete stimato | ~1.050 kWh | **~200-350 kWh** | -67-81% |
| Costo import annuo | ~263 EUR | **~50-88 EUR** | -66-81% |
| Autosufficienza | ~80% | **~94-96%** | +14-16pp |
| Autoconsumo | ~58% | **~80-85%** | +22-27pp |
| Export in rete | ~9.486 kWh | **~6.000-7.000 kWh** | -26-37% |
| Ricavo SSP/RD | ~759 EUR | **~480-560 EUR** | -26-37% |

### Bilancio Economico Annuo

| Voce | Attuale | Con 48 kWh |
|---|---|---|
| Costo import | -263 EUR | -69 EUR |
| Ricavo SSP/RD | +759 EUR | +520 EUR |
| Costi fissi contatore | -120 EUR | -120 EUR |
| **Netto annuo** | **+376 EUR** | **+331 EUR** |

Il netto annuo e leggermente inferiore (-45 EUR/anno) perche si vende meno alla rete, ma:
- Il risparmio sull'import (194 EUR/anno) e superiore alla perdita di export (239 EUR/anno)... SOLO al prezzo attuale di 0.08 EUR/kWh per il SSP.
- Se il prezzo dell'energia aumenta (>0.12 EUR/kWh di SSP), il calcolo si ribalta a favore dell'accumulo.

### Payback del Quasi Off-Grid

- Investimento: 2.400 EUR (2 nuove batterie)
- Risparmio netto rispetto ad attuale: la 2a batteria migliora di ~155 EUR/anno (come gia calcolato), la 3a aggiunge altri ~50 EUR/anno.
- **Payback combinato 2a + 3a batteria: ~12 anni** (piu conservativo della sola 2a batteria perche il rendimento marginale diminuisce)
- Ma il valore reale e nell'**autosufficienza e resilienza**: 2-3 giorni di autonomia completa.

---

## 7. Limiti Pratici e Verifiche

### Corrente Batteria

| Config | Batterie | Ah totali | Corrente max Deye | Corrente per batt | Giudizio |
|---|---|---|---|---|---|
| Attuale | 1 | 314 | 200A | 200A | OK (Battery Queen supporta?) |
| 2 batterie | 2 | 628 | 240A | 120A | Conservativo, OK |
| 3 batterie | 3 | 942 | 240A | 80A | Molto conservativo, OK |
| 4 batterie | 4 | 1.256 | 240A | 60A | Ultra conservativo, OK |

Con 3-4 batterie, la corrente per ciascuna e molto bassa (60-80A). Questo e positivo:
- Minore stress sulle celle
- Minore riscaldamento
- Vita utile piu lunga
- Il BMS ha ampio margine

### Gestione BMS con 3+ Batterie

Il Deye ha **una sola porta BMS**. Con 3 batterie serve:
- **Daisy-chain BMS**: una batteria master comunica con l'inverter, le altre slave si collegano alla master
- **BMS indipendenti**: funziona ma meno ideale (vedi second-battery-connection.md)
- **Informazione critica mancante**: verificare con il produttore Battery Queen il supporto per 3+ unita in parallelo

### Picchi di Consumo

| Parametro | Valore | Verifica |
|---|---|---|
| Picco misurato | 5.4 kW | Serale, cucina/riscaldamento |
| Max potenza continua Deye (batteria) | 12 kW | Ampiamente sufficiente |
| Max scarica batteria (240A x 51.2V) | ~12.3 kW | Ampiamente sufficiente |
| Picco gestibile senza rete? | SI | Anche con sola batteria |

La potenza non e un problema. Anche il picco piu alto (5.4 kW) e ben entro i limiti del Deye e delle batterie.

### Spazio Fisico

3-4 Battery Queen richiedono spazio aggiuntivo. Ogni Battery Queen ha dimensioni da batteria server rack (~50x40x20 cm). Verificare la disponibilita di spazio vicino all'inverter.

---

## 8. Raccomandazione Finale

### Raccomandazione: Configurazione "Quasi Off-Grid" con 3 Battery Queen

**Dati di Input**: Produzione PVGIS 13.986 kWh/anno, consumo stimato 5.550 kWh/anno, produzione dicembre 19.1 kWh/g, worst case 7 giorni quasi zero.

**Metodologia**: Bilancio energetico mensile, analisi worst case invernale, analisi economica comparativa grid-tied vs off-grid.

**Risultati**:

| Parametro | Valore |
|---|---|
| Configurazione consigliata | **3x Battery Queen (48 kWh)** |
| Investimento | **2.400 EUR** (2 nuove batterie) |
| Autonomia senza sole | **2.4 giorni** |
| Autonomia con produzione residua | **3.1 giorni** |
| Autosufficienza annua | **~95%** |
| Import residuo annuo | **~250 kWh** (~63 EUR) |

**Raccomandazione**:

1. **NON staccarsi dalla rete.** L'off-grid completo e economicamente insensato per questa casa perche si perderebbe il ricavo SSP (~759 EUR/anno) che e superiore al costo della bolletta.

2. **Aggiungere 2 Battery Queen** (totale 3 batterie, 48 kWh) per massimizzare l'autosufficienza. Il Deye gestisce agevolmente 48 kWh (sotto il limite di 60 kWh).

3. **Mantenere il contatore Enel** per:
   - Vendere il surplus (ancora ~520 EUR/anno di SSP/RD)
   - Avere backup per i rari periodi invernali prolungati (>3 giorni senza sole)
   - Sicurezza: se le batterie si esauriscono, la rete copre

4. **Step intermedio consigliato**: iniziare con la 2a batteria (payback ~3.9 anni, gia analizzato), valutare la 3a dopo 6-12 mesi di dati con 32 kWh.

**Impatto Stimato**:
- Autoconsumo: 58% -> 80-85%
- Autosufficienza: 80% -> 94-96%
- Risparmio import: ~194 EUR/anno
- Import residuo: solo 200-350 kWh/anno (vs 1.050 attuali)

**Rischio**: **Medio-Basso**
- Il Deye supporta fino a 60 kWh e 240A (48 kWh e ben entro i limiti)
- Serve verificare il supporto BMS multi-batteria della Battery Queen
- L'installazione richiede professionista qualificato (Davide Duca)
- I 3-7 giorni di autonomia SENZA sole non sono coperti al 100%, ma la rete colma il gap

**Prossimi Passi**:
1. Contattare produttore Battery Queen per confermare supporto 3 batterie in parallelo
2. Verificare protocollo BMS e daisy-chain per 3 unita
3. Installare la 2a batteria come primo step (investimento 1.200 EUR, payback 3.9 anni)
4. Raccogliere 6-12 mesi di dati con 32 kWh
5. Valutare 3a batteria sulla base dei dati reali
6. Discutere con Davide Duca il progetto complessivo

**Verifica**:
- Monitorare autoconsumo e autosufficienza mensile dopo ogni aggiunta
- Verificare che l'import invernale (dic-gen) sia coperto
- Target: import annuo < 300 kWh con 3 batterie

---

## Appendice A: Perche NON Off-Grid Completo

| Argomento | A favore dell'off-grid | Contro l'off-grid |
|---|---|---|
| **Economico** | Risparmio fissi contatore (120 EUR/anno) | Perdita ricavo SSP (-759 EUR/anno) |
| **Autonomia** | Indipendenza totale dalla rete | Servono 80-140 kWh di batteria (7-12 unita!) |
| **Batterie** | | Il Deye gestisce max ~60 kWh: serve 2o inverter |
| **Investimento** | | 8.800+ EUR per off-grid reale (5 gg autonomia) |
| **Sicurezza** | | 7-10 giorni di maltempo = blackout domestico |
| **Normativa** | | Staccarsi dalla rete richiede pratiche burocratiche |
| **Manutenzione** | | Nessun backup se le batterie si guastano |
| **Bilancio** | Netto: -376 EUR/anno (si perde denaro) | Grid-tied: +376 EUR/anno (si guadagna) |

**Differenza su 15 anni: l'off-grid costa circa 14.000-20.000 EUR in piu rispetto al grid-tied ottimizzato.**

## Appendice B: Tabella Riassuntiva Scenari

| Scenario | Batterie | Capacita | Investimento | Autonomia | Import annuo | Netto annuo | Guadagno 15 anni |
|---|---|---|---|---|---|---|---|
| Attuale | 1 | 16 kWh | 0 | 0.7 gg | 1.050 kWh | +376 EUR | +5.640 EUR |
| **+1 batteria** | **2** | **32 kWh** | **1.200 EUR** | **1.5 gg** | **~500 kWh** | **+530 EUR** | **+6.750 EUR** |
| **+2 batterie** | **3** | **48 kWh** | **2.400 EUR** | **2.4 gg** | **~250 kWh** | **+331 EUR (*)** | **+2.565 EUR** |
| +3 batterie | 4 | 64 kWh | 3.600 EUR | 3.2 gg | ~100 kWh | +280 EUR | +600 EUR |
| Off-grid (64 kWh) | 4 | 64 kWh | 3.600 EUR | 3.2 gg | 0 | -376 EUR | -9.240 EUR |
| Off-grid (80 kWh) | 5+ | 80+ kWh | 8.800 EUR+ | 4.1 gg | 0 | -376 EUR | -14.440 EUR |

(*) Il rendimento marginale della 3a batteria e basso: il risparmio aggiuntivo sull'import e modesto (~50 EUR/anno) perche gia con 2 batterie l'import e ridotto drasticamente.

**Conclusione: la configurazione ottimale e 2 batterie (32 kWh)** per il miglior rapporto costi/benefici. La 3a batteria si giustifica solo se l'autosufficienza e la resilienza ai blackout prolungati hanno un valore soggettivo elevato per il proprietario.

---

*Fonti: PVGIS 5.3, dati reali impianto Pedemonte (23-26 feb 2026), datasheet Deye SUN-12K-SG04LP3-EU, analisi energetica 26/02/2026, tariffe energia ARERA 2025/2026*
