# 2026-02-22 - Modifica Batt Low %

## Modifica Effettuata
- **Parametro**: Batt Low %
- **Valore precedente**: 35%
- **Nuovo valore**: 15%
- **Batt Shutdown %**: 10% (invariato, margine di sicurezza di 5%)

## Motivazione
L'analisi dei dati notturni del 22/02/2026 ha mostrato che la batteria smetteva di scaricarsi al 35% di SOC (alle 05:10) e l'inverter passava alla rete. Con un consumo notturno medio di ~0.41 kW, la batteria aveva energia residua inutilizzata.

## Impatto Atteso
- SOC utilizzabile: da 65% (100→35%) a **85% (100→15%)**
- Energia notturna disponibile: da ~11 kWh a **~14.5 kWh**
- Autonomia notturna a 0.41 kW: da ~27h a **~35h**
- Riduzione significativa del prelievo notturno dalla rete

## Dati di Riferimento (notte 22/02/2026)
- Consumo medio notturno: 0.41 kW
- SOC inizio notte: 51%
- SOC al momento dello switch a rete: 35% (ore 05:10)
- Energia scaricata dalla batteria: 2.57 kWh
- Energia prelevata da rete: 0.93 kWh (da 05:10 a 06:50)

## Verifica
Controllare i dati della notte successiva (23/02/2026) per verificare che:
- La batteria si scarichi fino al 15% prima di passare alla rete
- Non si verifichino shutdown indesiderati
- Il consumo dalla rete notturno sia ridotto o azzerato
