# Deye SUN-12K-SG04LP3-EU - Configurazione Corrente

> Ultimo aggiornamento: 2026-02-22
> Fonte: deye_inverter_config.xlsx + modifica manuale Batt Low %

## Battery Setting

| Parametro | Valore | Unit | Note |
|---|---|---|---|
| Batt Type | BMS Lithium Batt | | |
| Battery Capacity | 340 | Ah | |
| Max A Charge | 200 | A | |
| Max A Discharge | 200 | A | |
| Batt Shutdown % | 10 | % | |
| **Batt Restart %** | **35** | **%** | **Modificato il 22/02/2026 (era 50%, raccomandazione team)** |
| **Batt Low %** | **20** | **%** | **Modificato 2x il 22/02/2026: 35%→15%→20% (raccomandazione team)** |
| Activate Battery | Enable | | |
| Lithium Mode | 0 | | |
| Batt Charge Efficiency | 99 | % | |
| Batt Resistance | 12 | mΩ | |

### Grid / Generator Charge Settings

| Parametro | Valore | Unit | Note |
|---|---|---|---|
| Grid Charge | Disable | | |
| Gen Charge | Enable | | |
| Grid Signal | Enable | | |
| Gen Signal | Disable | | |
| Gen Start % | 30 | % | |
| Gen Charge Ampere | 40 | A | |
| Gen Max Run Time | 24 | h | |
| Gen Down Time | 0 | h | |
| Gen Force | Disable | | |

## System Work Mode

| Parametro | Valore | Unit |
|---|---|---|
| System Work Mode | Selling First | |
| Solar Sell | Enable | |
| Max Solar Power | 13200 | W |
| Max Sell Power | 12000 | W |
| Energy Pattern | Load First | |
| Zero Export Power | 10 | W |
| Setup Days | Mon-Sun | |

### Time of Use (6 fasce)

| Fascia | Grid Charge | Gen | Start | End | Power (W) | Batt % |
|---|---|---|---|---|---|---|
| Time 1 | No | No | 01:00 | 05:00 | 12000 | **20** |
| Time 2 | No | No | 05:00 | 09:00 | 12000 | **20** |
| Time 3 | No | No | 09:00 | 13:00 | 12000 | **20** |
| Time 4 | No | No | 13:00 | 17:00 | 12000 | **20** |
| Time 5 | No | No | 17:00 | 21:00 | 12000 | **20** |
| Time 6 | No | No | 21:00 | 01:00 | 12000 | **20** |

> NOTA: Le 6 fasce sono tutte identiche - il Time of Use non è effettivamente utilizzato.

## Grid Settings

| Parametro | Valore | Unit |
|---|---|---|
| Grid Mode | General Standard | |
| Grid Frequency | 50Hz | |
| IT System | Disable | |
| Phase Type | 0 240 120 | |
| Grid Level | LN:230VAC LL:400VAC | |

### Reconnect Settings

| Parametro | Valore | Unit |
|---|---|---|
| Normal Ramp Rate | 10 | s |
| Grid V High (Reconnect) | 263 | V |
| Grid V Low (Reconnect) | 187 | V |
| Grid Hz High (Reconnect) | 51.3 | Hz |
| Grid Hz Low (Reconnect) | 48.2 | Hz |
| Reconnect Ramp Rate | 36 | s |
| PF | 1 | |
| Grid Reconnection Time | 60 | s |

### IP Protection

| Parametro | Valore | Unit |
|---|---|---|
| Over Voltage U | 260 | V |
| U< 1 / Trip Delay | 185V | 0.1s |
| U> 1 / Trip Delay | 265V | 0.1s |
| F< 1 / Trip Delay | 48Hz | 0.1s |
| F> 1 / Trip Delay | 51.5Hz | 0.1s |
| U< 2 / Trip Delay | 185V | 0.1s |
| U> 2 / Trip Delay | 265V | 0.1s |
| F< 2 / Trip Delay | 48Hz | 0.1s |
| F> 2 / Trip Delay | 51.5Hz | 0.1s |
| U< 3 | 185V | |
| U> 3 | 265V | |
| F< 3 | 48Hz | |
| F> 3 | 51.5Hz | |

### Grid Advanced

| Parametro | Valore |
|---|---|
| F(W) | UnderFre Disable / OverFre Disable |
| Mincosphi | 0.4 |
| V(W) | Disable |
| V(Q) | Disable |
| Fixed Q | 0% |
| Q R.T (3Tau) | 10s |
| P(Q) | Disable |
| P(F) | Disable |
| LVRT | Disable |
| HVRT | Disable |
| Zero I | Enable |

## SmartLoad & Advanced

| Parametro | Valore | Unit |
|---|---|---|
| SmartLoad Setup | MicInv Input | |
| OFF % | 70 | % |
| ON % | 65 | % |
| MI Export to Grid Cutoff | Disable | |
| AC Couple Setup | Disable | |

### Advanced Functions

| Parametro | Valore | Unit |
|---|---|---|
| ARC Setup | OFF | |
| Gen Peak-Shaving | Disable | |
| Generator Peak-Shaving Power | 8000 | W |
| Grid Peak-Shaving | Disable | |
| Grid Peak-Shaving Power | 8000 | W |
| BMS-stop | Disable | |
| Parallel | Disable | |
| DRM | Disable | |
| Signal Island Mode | Disable | |
| Backup Delay | 0 | s |
| CT Ratio | 2000:1 | |
| EX_MeterCT | Disable | |
| Grid Tie Meter2 | Disable | |
| Meter Select | No Meter | |
| Asymmetric Phase Feeding | Disable | |
| MPPT Scan | Disable | |
| DC 1 for Wind Turbine | Disable | |
| DC 2 for Wind Turbine | Disable | |

## Problemi Aperti

1. **Grid Code "General Standard"** - Dovrebbe essere CEI 0-21 per impianti connessi alla rete in Italia
2. **Meter Select "No Meter"** - Senza meter esterno, le funzioni Selling First e Zero Export non possono misurare accuratamente i flussi al POD
3. **Selling First + Zero Export 10W** - Configurazione contraddittoria: Selling First vuole vendere, Zero Export a 10W lo impedisce
4. **Time of Use non configurato** - Le 6 fasce sono identiche, nessun vantaggio dalle fasce orarie
5. **Grid Charge Disable** - In inverno potrebbe convenire caricare da rete nelle ore F3
