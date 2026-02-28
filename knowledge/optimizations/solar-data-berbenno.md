# Dati Solari e Producibilita Fotovoltaica - Berbenno di Valtellina

## Posizione e Coordinate

| Parametro | Valore |
|-----------|--------|
| Indirizzo | Via Pedemonte 425, Berbenno di Valtellina (SO) |
| Coordinate | 46.17°N, 9.74°E |
| Altitudine | ~385 m s.l.m. |
| Zona climatica | Valle alpina (Valtellina) |
| Provincia | Sondrio, Lombardia |

## Impianto Fotovoltaico

| Parametro | Valore |
|-----------|--------|
| Inverter | SolarEdge SE10K-RWS |
| Potenza nominale | 10 kWp |
| Pannelli | Con ottimizzatori SolarEdge |
| Inclinazione stimata | ~35° |
| Orientamento | Sud (azimuth ~0°) |
| Perdite di sistema | 14% (stima PVGIS standard) |

## Produzione Mensile Stimata (PVGIS - con ombreggiamento montano)

Dati da PVGIS 5.3, database PVGIS-SARAH3, con profilo orizzonte calcolato dal DEM.
Configurazione: 10 kWp, inclinazione 35°, orientamento sud, perdite 14%.

| Mese | Produzione (kWh/mese) | Media giornaliera (kWh/giorno) | Irradiazione (kWh/m²/mese) | Ore sole equiv. (h/giorno) |
|------|----------------------|-------------------------------|---------------------------|--------------------------|
| Gennaio | 802 | 25.9 | 91.8 | 2.59 |
| Febbraio | 1,089 | 38.9 | 127.6 | 3.89 |
| Marzo | 1,443 | 46.6 | 173.9 | 4.66 |
| Aprile | 1,370 | 45.7 | 169.4 | 4.57 |
| Maggio | 1,315 | 42.4 | 165.3 | 4.24 |
| Giugno | 1,363 | 45.4 | 176.2 | 4.54 |
| Luglio | 1,508 | 48.7 | 197.6 | 4.87 |
| Agosto | 1,419 | 45.8 | 184.9 | 4.58 |
| Settembre | 1,249 | 41.6 | 159.7 | 4.16 |
| Ottobre | 1,114 | 35.9 | 136.5 | 3.59 |
| Novembre | 719 | 24.0 | 86.0 | 2.40 |
| Dicembre | 593 | 19.1 | 69.6 | 1.91 |
| **TOTALE ANNUO** | **13,986** | **38.3** | **1,738.5** | **3.83** |

### Ore di Sole Equivalenti (Peak Sun Hours)

Le ore di sole equivalenti rappresentano il numero di ore a 1 kW/m² che produrrebbero la stessa energia totale della giornata reale. Si calcolano come produzione giornaliera diviso la potenza di picco (10 kWp), corrette per le perdite.

| Mese | PSH (h/giorno) | Classificazione |
|------|----------------|-----------------|
| Gennaio | 2.59 | Basso |
| Febbraio | 3.89 | Medio-basso |
| Marzo | 4.66 | Medio |
| Aprile | 4.57 | Medio |
| Maggio | 4.24 | Medio |
| Giugno | 4.54 | Medio |
| Luglio | 4.87 | Medio-alto |
| Agosto | 4.58 | Medio |
| Settembre | 4.16 | Medio |
| Ottobre | 3.59 | Medio-basso |
| Novembre | 2.40 | Basso |
| Dicembre | 1.91 | Molto basso |

## Impatto dell'Ombreggiamento Montano

Il profilo orizzontale PVGIS mostra che le montagne circostanti hanno un impatto significativo sulla produzione, soprattutto in inverno quando il sole e basso.

### Profilo Orizzonte (dati PVGIS)

Le montagne creano un'ostruzione significativa:
- **Sud (0°)**: ostruzione di 13.8° - limita il sole invernale basso
- **Sud-Ovest (+7.5° a +30°)**: ostruzione 17-18° - montagne alte a SW
- **Est (-90°)**: ostruzione di soli 3.1° - orizzonte relativamente libero
- **Ovest (+75° a +90°)**: ostruzione 2.3-4.2° - orizzonte relativamente libero
- **Nord (±150° a ±180°)**: ostruzione 20-26° - non rilevante per il solare

### Perdita per Ombreggiamento Montano

Confronto tra produzione CON e SENZA profilo orizzonte (stesse impostazioni):

| Mese | Con orizzonte (kWh) | Senza orizzonte (kWh) | Perdita (%) |
|------|--------------------|-----------------------|-------------|
| Gennaio | 802 | 1,031 | **-22.2%** |
| Febbraio | 1,089 | 1,132 | **-3.8%** |
| Marzo | 1,443 | 1,444 | -0.1% |
| Aprile | 1,370 | 1,370 | 0.0% |
| Maggio | 1,315 | 1,315 | 0.0% |
| Giugno | 1,363 | 1,363 | 0.0% |
| Luglio | 1,508 | 1,508 | 0.0% |
| Agosto | 1,419 | 1,419 | 0.0% |
| Settembre | 1,249 | 1,249 | 0.0% |
| Ottobre | 1,114 | 1,120 | -0.5% |
| Novembre | 719 | 857 | **-16.1%** |
| Dicembre | 593 | 876 | **-32.3%** |
| **ANNUO** | **13,986** | **14,685** | **-4.8%** |

**Osservazioni chiave:**
- L'ombreggiamento montano impatta principalmente da novembre a gennaio
- A dicembre si perde il **32.3%** della produzione potenziale per le montagne
- A gennaio il 22.2%, a novembre il 16.1%
- Da marzo a settembre l'impatto e trascurabile (sole sufficientemente alto)
- L'impatto annuo complessivo e del 4.8% (~700 kWh/anno persi)

## Climatologia Invernale - Sondrio/Valtellina

### Ore di Sole

Dati climatologici per la provincia di Sondrio:

| Parametro | Valore |
|-----------|--------|
| Ore di sole annue | ~2,647 h |
| Media mensile | ~220 h |
| Gennaio (minimo) | ~151 h (media 5.0 h/giorno) |
| Luglio (massimo) | ~319 h (media 10.3 h/giorno) |

### Precipitazioni Invernali

| Mese | Precipitazione (mm) | Giorni di pioggia |
|------|---------------------|-------------------|
| Novembre | 90 | 6 |
| Dicembre | 50 | 4 |
| Gennaio | 50 | 5 |
| Febbraio | 45 | 4 |

### Caratteristiche Climatiche Invernali

- **Nebbia**: Frequente in fondovalle in autunno e inverno per inversione termica. L'aria fredda ristagna nella valle.
- **Neve**: Media annua ~45 cm. Copertura nevosa possibile da dicembre a febbraio.
- **Nuvolosita**: Il cielo e spesso nuvoloso in inverno, con periodi prolungati di copertura.

## Worst Case Invernale: Giorni Consecutivi con Produzione Minima

### Stima dei Giorni di Autonomia Necessari

Basandosi sui dati climatologici e sulla letteratura per valli alpine:

| Scenario | Giorni consecutivi | Produzione stimata | Note |
|----------|-------------------|--------------------|------|
| Nuvoloso persistente | 3-5 giorni | 10-25% del nominale | Copertura nuvolosa densa |
| Nebbia + nuvole | 5-7 giorni | 5-15% del nominale | Inversione termica prolungata |
| Neve sui pannelli | 1-3 giorni | 0-5% del nominale | Fino a completo scioglimento |
| Worst case combinato | 7-10 giorni | ~5-10% del nominale | Neve + nebbia + nuvole |

**Stima produzione worst case giornaliera a dicembre:**
- Media PVGIS: 19.1 kWh/giorno
- Giorno nuvoloso: ~3-5 kWh/giorno (15-25% del nominale)
- Giorno con neve sui pannelli: ~0-1 kWh/giorno
- Worst case (nebbia + neve): ~0.5-2 kWh/giorno

**Raccomandazione per dimensionamento batteria:**
Per una casa che consuma 15-25 kWh/giorno in inverno, servirebbero 4-7 giorni di autonomia, ovvero:
- Scenario conservativo (7 giorni, 20 kWh/giorno): **140 kWh** di capacita utile batteria
- Scenario moderato (4 giorni, 20 kWh/giorno): **80 kWh** di capacita utile batteria
- Con produzione residua (3-5 kWh/giorno anche nei giorni peggiori): si puo ridurre del 15-20%

## Fattori Locali Specifici di Berbenno

### Fattori Negativi
1. **Ombreggiamento montano**: Riduce la produzione invernale del 22-32% (novembre-gennaio)
2. **Nebbia di fondovalle**: Frequente per inversione termica, riduce ulteriormente la produzione
3. **Neve sui pannelli**: Possibile copertura per 1-3 giorni dopo nevicate significative
4. **Giornate corte**: A dicembre solo ~8.5 ore di luce astronomica, ulteriormente ridotte dalle montagne

### Fattori Positivi
1. **Albedo neve**: La neve al suolo riflette luce verso i pannelli, potenziale aumento del 5-15% nelle giornate serene invernali
2. **Temperature basse**: I pannelli hanno efficienza maggiore al freddo (coefficiente temperatura negativo del silicio)
3. **Aria limpida**: Nelle giornate serene invernali, l'aria secca di montagna permette irradiazione diretta molto efficiente
4. **Altitudine**: A 385 m, sopra le nebbie piu basse della pianura padana

## Validazione con Dati Reali (Febbraio 2026)

### Confronto Produzione Reale vs PVGIS

| Data | Produzione reale (kWh) | Media PVGIS feb (kWh/g) | Scostamento |
|------|----------------------|-------------------------|-------------|
| 23 febbraio 2026 | 34.26 | 38.9 | -11.9% |
| 26 febbraio 2026 | 40.11 | 38.9 | +3.1% |

**Picco di potenza registrato**: 6.62 kW (su 10 kWp nominali = 66.2% del picco)

### Analisi della Validazione

1. **Produzione giornaliera**: I valori reali (34-40 kWh) sono coerenti con la media PVGIS di febbraio (38.9 kWh/g). La variabilita giornaliera e normale.

2. **Picco di potenza**: Il picco di 6.62 kW su 10 kWp (66.2%) e plausibile per fine febbraio considerando:
   - Angolo solare ancora relativamente basso (~35° a mezzogiorno)
   - Possibile ombreggiamento parziale da montagne a SW che taglia il picco pomeridiano
   - Eventuali perdite per sporcizia/invecchiamento pannelli
   - L'ostruzione di 13.8° a sud e 17-18° a sud-ovest nel profilo orizzonte PVGIS spiega perfettamente il limite al picco

3. **Coerenza complessiva**: I dati reali confermano che le stime PVGIS sono attendibili per questa posizione. La produzione reale sembra leggermente inferiore alla media PVGIS, il che e coerente con eventuali perdite aggiuntive non modellate (sporcizia, cavi, efficienza inverter reale vs teorica).

## Riepilogo per il Dimensionamento

| Parametro | Valore |
|-----------|--------|
| Produzione annua stimata | 13,986 kWh |
| Produzione media giornaliera annua | 38.3 kWh |
| Produzione media dicembre (worst month) | 19.1 kWh/giorno |
| Produzione worst case giornaliero | 0.5-5 kWh/giorno |
| Giorni consecutivi a produzione quasi zero | 3-7 giorni (worst case 10) |
| Impatto ombreggiamento montano annuo | -4.8% (-700 kWh) |
| Impatto ombreggiamento montano dicembre | -32.3% |
| Ore sole equivalenti dicembre | 1.91 h/giorno |
| Ore sole equivalenti luglio | 4.87 h/giorno |
| Rapporto produzione estate/inverno | ~2.5:1 (luglio vs dicembre) |

---

*Fonti dati: PVGIS 5.3 (re.jrc.ec.europa.eu), database PVGIS-SARAH3, profilo orizzonte DEM*
*Dati climatologici: climieviaggi.it, stazione meteo Sondrio*
*Ultimo aggiornamento: febbraio 2026*
