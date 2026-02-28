# Analisi Batteria - 26 Febbraio 2026

> Analista: deye-expert
> Data analisi: 2026-02-27
> Fonte dati: PlantsDetails-History-26-feb-2026.xlsx (Solarman Cloud, intervallo 5 min)
> Batteria: Battery Queen 51.2V 314Ah (~16 kWh), LiFePO4
> Inverter: Deye SUN-12K-SG04LP3-EU

## Riepilogo Giornata

| Parametro | Valore |
|---|---|
| SOC inizio (00:00) | 55% |
| SOC minimo | 30% alle 08:55 |
| SOC massimo | 100% alle 12:55 |
| SOC fine (00:00+1) | 66% |
| Scarica totale | 9.75 kWh |
| Carica totale | 11.42 kWh |
| Bilancio netto | +1.67 kWh (la batteria ha guadagnato energia) |
| Prelievo rete | 0.41 kWh |
| Immissione rete | 16.77 kWh |

## 1. Ciclo Batteria

### Depth of Discharge (DOD)

| Metrica | Valore |
|---|---|
| DOD ciclo completo | **70%** (da 100% a 30%) |
| DOD in energia | 11.20 kWh |
| Cicli equivalenti | 0.71 |

**Valutazione**: DOD del 70% classificato come **pesante ma entro i limiti**. Le batterie LiFePO4 sono progettate per 6000+ cicli all'80% DOD. Un DOD del 70% e' conservativo e non impatta significativamente la vita utile.

### C-Rate

| Metrica | Scarica | Carica |
|---|---|---|
| **Picco** | **0.319C** (5.10 kW, 99.6A) alle 18:20 | **0.317C** (5.07 kW, 99.0A) alle 11:55 |
| **Medio** | 0.039C (0.63 kW) | 0.156C (2.49 kW) |
| **Limite batteria** | ~0.64C (200A) | ~0.64C (200A) |
| **% del limite** | 50% | 50% |

**Valutazione**: C-rate molto conservativi. Il picco di 0.32C e' la meta' del limite della batteria. Stress termico minimo.

## 2. Efficienza Round-Trip

| Metrica | Valore |
|---|---|
| Energia scaricata | 9.75 kWh |
| Energia caricata | 11.42 kWh |
| **Efficienza** | **85.3%** |
| Verifica SOC | +11% (55% -> 66%) = +1.76 kWh netti |
| Perdite stimate | ~1.67 kWh |

**Valutazione**: Efficienza dell'85.3% che include le perdite dell'inverter Deye (conversione DC-AC bidirezionale). Per un sistema inverter+batteria, un'efficienza dell'85% e' nella norma (tipico 83-90% per sistemi LiFePO4).

**Nota**: La differenza tra carica e scarica (1.67 kWh) e' coerente con il guadagno netto di SOC (+11% = 1.76 kWh teorici). La leggera discrepanza (0.09 kWh) rientra nella precisione delle misure e nell'arrotondamento del SOC.

## 3. Analisi Picco Serale (18:15-18:30)

### Dettaglio minuto per minuto

| Ora | Consumo | Batteria | Rete | SOC |
|---|---|---|---|---|
| 18:00 | 0.47 kW | 0.56 kW | 0.00 kW | 98% |
| 18:05 | 0.53 kW | 0.65 kW | 0.00 kW | 97% |
| 18:10 | 0.35 kW | 0.55 kW | 0.00 kW | 97% |
| **18:15** | **5.38 kW** | **5.08 kW** | **0.48 kW** | **96%** |
| **18:20** | **5.44 kW** | **5.10 kW** | **0.51 kW** | **93%** |
| 18:25 | 3.79 kW | 3.91 kW | 0.01 kW | 92% |
| 18:30 | 4.48 kW | 4.58 kW | 0.00 kW | 90% |
| 18:35 | 1.20 kW | 1.28 kW | 0.01 kW | 89% |

### Analisi del picco

- **Picco batteria**: 5.10 kW alle 18:20 (corrente: 99.6A)
- **Picco consumo**: 5.44 kW alle 18:20
- **SOC perso**: 6 punti percentuali in 15 minuti (96% -> 90%)
- **Rete intervenuta**: si, per 0.48-0.51 kW alle 18:15-18:20 (la batteria non copriva tutto il carico)
- **Causa probabile**: accensione forno elettrico, scaldabagno, o piastre induzione

**Valutazione**: La batteria ha retto bene il picco. La corrente di 99.6A e' il **50% del limite** di 200A. Il Deye ha comunque prelevato ~0.5 kW dalla rete durante il picco, probabilmente per la latenza nella rampa di potenza della batteria (tempo di risposta dell'inverter). Alle 18:25 e 18:30, con carichi ancora alti (3.8-4.5 kW), la rete e' tornata a 0 kW, confermando che la batteria poteva coprire il carico da sola.

## 4. Margine SOC

| Soglia | Valore | Margine dal minimo (30%) |
|---|---|---|
| SOC minimo raggiunto | 30% | - |
| **Batt Low** (soglia operativa) | **20%** | **10 punti % (1.60 kWh)** |
| Batt Shutdown | 10% | 20 punti % (3.20 kWh) |

**Valutazione**: Margine di 10 punti percentuali (1.60 kWh) rispetto al Batt Low del 20%. Questo significa che al momento del SOC minimo (08:55), rimanevano ancora:
- ~1.60 kWh prima di raggiungere il Batt Low e iniziare a prelevare dalla rete
- ~3.20 kWh prima dello shutdown
- A un consumo medio di 0.40 kW, avrebbe coperto **4 ore aggiuntive** prima di raggiungere il Batt Low

Il margine e' **adeguato** per la stagione. La produzione solare ha iniziato a contribuire proprio quando il SOC era al minimo, garantendo una transizione fluida dalla scarica alla carica.

## 5. Valutazione Complessiva

### Fasi della giornata

| Fase | Periodo | SOC | Energia | Descrizione |
|---|---|---|---|---|
| 1. Scarica notturna | 00:00-09:10 | 55% -> 30% | 4.15 kWh scaricati | Carico base ~0.40 kW + spike 06:30 |
| 2. Carica solare | 09:10-12:55 | 30% -> 100% | 11.28 kWh caricati | Ricarica completa in 3h 45min |
| 3. Batteria piena | 12:55-17:25 | 100% | 16.21 kWh esportati in rete | Eccesso PV immesso in rete |
| 4. Scarica serale | 17:30-00:00 | 99% -> 66% | 5.58 kWh scaricati | Consumo serale + picco 18:15 |

### Consumo notturno (00:00-07:00)

- Consumo medio: 0.40 kW
- Copertura batteria: **98.2%**
- Energia rete: solo 0.06 kWh (praticamente zero)
- La batteria ha gestito autonomamente tutto il fabbisogno notturno

### Spike 06:30

- Consumo: 2.19 kW (probabilmente accensione elettrodomestico)
- Batteria: 2.28 kW (corrente: 44.5A)
- SOC: 36% al momento dello spike
- Gestito **interamente dalla batteria**, senza alcun prelievo dalla rete

### Giudizio finale

| Criterio | Valore | Giudizio |
|---|---|---|
| DOD | 70% | Moderato-Pesante (ma entro limiti LiFePO4) |
| C-rate picco | 0.32C | Conservativo (50% del limite) |
| Corrente picco | 99.6A / 200A | 50% della capacita' |
| Efficienza | 85.3% | Nella norma |
| Margine SOC | 10% sopra Batt Low | Adeguato |
| Autosufficienza notturna | 98.2% | Eccellente |

**Giornata di difficolta' MODERATA per la batteria**. Il DOD del 70% e' significativo ma ben entro le specifiche LiFePO4. I C-rate sono sempre rimasti conservativi. La batteria ha gestito senza problemi sia il consumo notturno base sia i picchi (spike 06:30 e picco serale 18:15-18:30). Il sistema ha funzionato in modo ottimale, con la batteria che ha coperto quasi il 100% del fabbisogno notturno e il fotovoltaico che ha ricaricato completamente la batteria entro mezzogiorno.

### Nota sulla longevita'

Con un DOD medio del 70% e C-rate sotto 0.3C, la Battery Queen LiFePO4 dovrebbe raggiungere facilmente 6000-8000 cicli prima di scendere all'80% SOH. Se questa giornata fosse rappresentativa (0.71 cicli equivalenti/giorno), la vita utile stimata sarebbe di **8450-11270 giorni** (23-31 anni), ben oltre la vita utile attesa di 15-20 anni per questa tecnologia.
