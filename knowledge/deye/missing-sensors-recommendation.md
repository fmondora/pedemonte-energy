# Sensori Deye Mancanti - Analisi e Raccomandazioni

> Data: 2026-03-01
> Autore: deye-expert
> Task: #2 - Verifica configurazione sensori Deye e contatori giornalieri mancanti

## Situazione Attuale

Il `command_line` sensor `sensor.deye_inverter` gia' recupera dalla Deye Cloud API **tutti i datapoint necessari** come `json_attributes`. Tuttavia, per 6 di questi attributi **non esistono template sensors** che li espongano come entity HA utilizzabili.

### Attributi GIA' recuperati ma SENZA template sensor

| Attributo API | Descrizione | Tipo |
|---|---|---|
| `TotalSolarPower` | Potenza PV Deye istantanea | W, measurement |
| `LoadPowerL1` | Potenza carico fase L1 | W, measurement |
| `LoadPowerL2` | Potenza carico fase L2 | W, measurement |
| `LoadPowerL3` | Potenza carico fase L3 | W, measurement |
| `DailyChargingEnergy` | Energia caricata batteria oggi | kWh, daily |
| `DailyDischargingEnergy` | Energia scaricata batteria oggi | kWh, daily |
| `DailyGridFeedIn` | Energia esportata in rete oggi | kWh, daily |
| `DailyEnergyPurchased` | Energia importata dalla rete oggi | kWh, daily |

### Template sensors ESISTENTI (13 totali, funzionanti)

- 5 sensori energia cumulativa (kWh, total_increasing) -> Energy Dashboard
- 3 sensori potenza (W, measurement) -> monitoraggio real-time
- 3 sensori stato (SOC, voltage, temperature)
- 2 sensori giornalieri (DailyActiveProduction, DailyConsumption)

## Raccomandazione 1: Nuovi Template Sensors (priorita' ALTA)

Aggiungere i seguenti template sensors in `configuration.yaml`, nella sezione template esistente dei sensori Deye Cloud.

### A) Sensori potenza mancanti

```yaml
  # --- Deye Cloud: potenza PV e carico per fase ---
  - sensor:
      - name: "Deye PV Power"
        unique_id: deye_pv_power
        state: "{{ state_attr('sensor.deye_inverter', 'TotalSolarPower') | float(0) }}"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        icon: mdi:solar-panel-large
      - name: "Deye Load Power L1"
        unique_id: deye_load_power_l1
        state: "{{ state_attr('sensor.deye_inverter', 'LoadPowerL1') | float(0) }}"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        icon: mdi:flash
      - name: "Deye Load Power L2"
        unique_id: deye_load_power_l2
        state: "{{ state_attr('sensor.deye_inverter', 'LoadPowerL2') | float(0) }}"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        icon: mdi:flash
      - name: "Deye Load Power L3"
        unique_id: deye_load_power_l3
        state: "{{ state_attr('sensor.deye_inverter', 'LoadPowerL3') | float(0) }}"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        icon: mdi:flash
      - name: "Deye Load Power Total"
        unique_id: deye_load_power_total
        state: >
          {% set l1 = state_attr('sensor.deye_inverter', 'LoadPowerL1') | float(0) %}
          {% set l2 = state_attr('sensor.deye_inverter', 'LoadPowerL2') | float(0) %}
          {% set l3 = state_attr('sensor.deye_inverter', 'LoadPowerL3') | float(0) %}
          {{ (l1 + l2 + l3) | round(0) }}
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        icon: mdi:home-lightning-bolt
```

### B) Sensori giornalieri mancanti

```yaml
  # --- Deye Cloud: contatori giornalieri aggiuntivi ---
  - sensor:
      - name: "Deye Daily Grid Import"
        unique_id: deye_daily_grid_import
        state: "{{ state_attr('sensor.deye_inverter', 'DailyEnergyPurchased') | float(0) }}"
        unit_of_measurement: "kWh"
        device_class: energy
        icon: mdi:transmission-tower-import
      - name: "Deye Daily Grid Export"
        unique_id: deye_daily_grid_export
        state: "{{ state_attr('sensor.deye_inverter', 'DailyGridFeedIn') | float(0) }}"
        unit_of_measurement: "kWh"
        device_class: energy
        icon: mdi:transmission-tower-export
      - name: "Deye Daily Battery Charge"
        unique_id: deye_daily_battery_charge
        state: "{{ state_attr('sensor.deye_inverter', 'DailyChargingEnergy') | float(0) }}"
        unit_of_measurement: "kWh"
        device_class: energy
        icon: mdi:battery-plus
      - name: "Deye Daily Battery Discharge"
        unique_id: deye_daily_battery_discharge
        state: "{{ state_attr('sensor.deye_inverter', 'DailyDischargingEnergy') | float(0) }}"
        unit_of_measurement: "kWh"
        device_class: energy
        icon: mdi:battery-minus
```

## Raccomandazione 2: Utility Meter NON necessari

I contatori giornalieri dalla Deye Cloud API (`DailyChargingEnergy`, `DailyDischargingEnergy`, `DailyGridFeedIn`, `DailyEnergyPurchased`) vengono **resettati automaticamente a mezzanotte dall'inverter**. Non serve creare utility_meter HA per questi valori.

Se in futuro si volessero contatori settimanali o mensili, si potrebbe creare un `utility_meter` sopra i sensori cumulativi `total_increasing`:

```yaml
# OPZIONALE: utility_meter per statistiche settimanali/mensili
utility_meter:
  weekly_grid_import:
    source: sensor.deye_grid_import_energy
    cycle: weekly
  monthly_grid_import:
    source: sensor.deye_grid_import_energy
    cycle: monthly
  monthly_grid_export:
    source: sensor.deye_grid_export_energy
    cycle: monthly
  monthly_battery_cycles:
    source: sensor.deye_battery_charge_energy
    cycle: monthly
```

Ma questo e' di bassa priorita' dato che HA tiene gia' le statistiche a lungo termine per i sensori `total_increasing`.

## Raccomandazione 3: Sensore PV Power combinato (SolarEdge + Deye)

Attualmente `sensor.deye_pv_power` (proposto sopra) restituisce la potenza PV del Deye. Se si vuole un sensore combinato che sommi SolarEdge + Deye:

```yaml
  - sensor:
      - name: "Total PV Power"
        unique_id: total_pv_power
        state: >
          {% set deye = state_attr('sensor.deye_inverter', 'TotalSolarPower') | float(0) %}
          {% set se = states('sensor.solaredge_current_power') | float(0) %}
          {{ (deye + se) | round(0) }}
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        icon: mdi:solar-power-variant
```

**Nota**: questo va coordinato con l'electrical-engineer per capire se ha senso nel contesto dell'architettura multi-inverter.

## Riepilogo Sensori Proposti

| Entity ID | Attributo API | Unita' | Priorita' |
|---|---|---|---|
| `sensor.deye_pv_power` | TotalSolarPower | W | ALTA |
| `sensor.deye_load_power_total` | L1+L2+L3 calcolato | W | ALTA |
| `sensor.deye_daily_grid_import` | DailyEnergyPurchased | kWh | ALTA |
| `sensor.deye_daily_grid_export` | DailyGridFeedIn | kWh | ALTA |
| `sensor.deye_daily_battery_charge` | DailyChargingEnergy | kWh | MEDIA |
| `sensor.deye_daily_battery_discharge` | DailyDischargingEnergy | kWh | MEDIA |
| `sensor.deye_load_power_l1` | LoadPowerL1 | W | BASSA |
| `sensor.deye_load_power_l2` | LoadPowerL2 | W | BASSA |
| `sensor.deye_load_power_l3` | LoadPowerL3 | W | BASSA |
| `sensor.total_pv_power` | Deye+SolarEdge | W | DA DISCUTERE |

## Nessun Datapoint Mancante nell'API

L'API Deye Cloud restituisce circa 75 datapoint per device. Tutti i dati necessari sono gia' presenti negli attributi del `command_line` sensor. Non servono modifiche allo script `deye_cloud_sensor.py` ne' nuovi datapoint da richiedere.

## Prossimi Passi

1. **Applicare i template sensors** proposti in Raccomandazione 1 a `configuration.yaml`
2. **Riavviare HA** per attivare i nuovi sensori
3. **Verificare** che i nuovi sensori mostrino valori corretti
4. **Aggiornare la dashboard** per visualizzare i nuovi dati giornalieri e la potenza PV
5. **Coordinare con electrical-engineer** per il sensore PV combinato
