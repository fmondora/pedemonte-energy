# SolarEdge SE10K-RWS StorEdge - Scheda Tecnica

> Ultimo aggiornamento: 2026-02-22
> Fonte: Datasheet ufficiale SolarEdge (DS-000087-EU, April 2022)

## Identificazione

- **Modello**: SE10K-RWS
- **Tipo**: StorEdge Three Phase Hybrid Inverter
- **Part number**: SEXK-XXS48XXXX
- **Garanzia**: 12 anni (estendibile a 25)

## Specifiche Output AC

| Parametro | Valore |
|---|---|
| Potenza nominale AC | 10.000 VA |
| Potenza massima AC | 10.000 VA |
| Tensione AC (L-L / L-N) | 380/220 ; 400/230 Vac |
| Range tensione L-N | 184 - 264.5 Vac |
| Frequenza | 50/60 ± 5 Hz |
| Corrente max continua (per fase) | 16 A |
| RCD / RCD Step | 300 / 30 mA |
| Grid supportate | 3 / N / PE (WYE con Neutro) |
| Islanding Protection | Sì |
| Power Factor configurabile | Sì |

## Specifiche Input PV

| Parametro | Valore |
|---|---|
| Potenza DC max (STC) | 13.500 W |
| Tensione max input | 900 Vdc |
| Tensione nominale DC | 750 Vdc |
| Corrente max input | 16.5 Adc |
| Transformer-less | Sì |
| Protezione inversione polarità | Sì |
| Ground-Fault Isolation | 700kΩ |
| Efficienza max inverter | 98% |
| Efficienza pesata europea | 97.6% |
| Input PV | 2 x MC4 pair |

## Specifiche Input Batteria

| Parametro | Valore |
|---|---|
| Batterie supportate | SolarEdge Home Battery 48V, LG Chem RESU, BYD Battery-Box LV/LVS |
| Numero batterie per inverter | 1 |
| Potenza DC max batteria | 5.000 W |
| Range tensione batteria | 40-62 Vdc |
| Corrente max continua batteria | 130 Adc |
| Efficienza scarica batteria→rete | 96.1% |
| Comunicazione batteria | CAN |

## Comunicazione

| Interfaccia | Note |
|---|---|
| 2 x RS485 | Meter, comunicazione |
| Ethernet | Monitoraggio cloud |
| ZigBee | Smart Energy |
| Wi-Fi | Richiede antenna esterna |
| Cellular | Opzionale (built-in) |

## Specifiche Fisiche

| Parametro | Valore |
|---|---|
| Dimensioni (H x W x D) | 853 x 316 x 193 mm |
| Peso | 37 kg |
| Temperatura operativa | -40 a +60 °C |
| Raffreddamento | Ventole interne ed esterne |
| Rumore | < 50 dBA |
| Protezione | IP65 (indoor/outdoor) |
| Montaggio | Staffe incluse |

## Certificazioni

| Standard | Riferimento |
|---|---|
| Sicurezza | IEC-62109 |
| Grid Connection | VDE 0126-1-1, VDE-AR-N-4105, G98/G99 |
| Emissioni | IEC61000-6-2, IEC61000-6-3, IEC61000-3-11, IEC61000-3-12 |
| RoHS | Sì |

## Caratteristiche Chiave

- **DC-coupled**: l'energia solare va direttamente in batteria senza conversione AC, meno perdite
- **SafeDC**: tensione DC a livello sicuro quando l'inverter è spento (sicurezza per installazione/manutenzione)
- **Monitoraggio a livello di modulo**: grazie agli ottimizzatori SolarEdge
- **SetApp**: commissioning via smartphone
- **Batterie 48V low voltage**: compatibile con batterie di diversi produttori

## Confronto con Deye SUN-12K-SG04LP3-EU

| Parametro | SolarEdge SE10K-RWS | Deye SUN-12K |
|---|---|---|
| Potenza AC | 10 kW | 12 kW |
| Potenza PV max | 13.5 kW | 18 kW (2 MPPT) |
| Potenza batteria max | 5 kW | ~9.6 kW (200A x 48V) |
| Efficienza max | 98% | ~97.6% |
| Efficienza batteria→rete | 96.1% | N/A |
| Tensione batteria | 40-62V | 40-60V |
| Corrente max batteria | 130A | 200A |
| Comunicazione batteria | CAN | CAN / RS485 |
| Backup integrato | Con accessori | Sì (ATS integrato) |
| Monitoraggio modulo | Sì (ottimizzatori) | No |
| Protezione | IP65 | IP65 |

## Documentazione

- `datasheet-storedge-three-phase-rws.pdf` - Datasheet ufficiale EN
- `datasheet-storedge-three-phase-it.pdf` - Datasheet ufficiale IT
- `installation-guide-storedge-three-phase.pdf` - Guida installazione

## Configurazione Attuale

> TODO: Esportare e documentare la configurazione attuale del SolarEdge (profilo StorEdge, backup reserve, limiti export, ecc.)

## Note

- Il SolarEdge ha un limite di **5 kW sulla potenza batteria**, significativamente inferiore al Deye (che può gestire ~9.6 kW). Questo impatta la velocità di carica/scarica della batteria collegata al SolarEdge
- La comunicazione batteria è **solo CAN** (il Deye supporta anche RS485)
- Il backup richiede accessori aggiuntivi (sul Deye è integrato con ATS)
