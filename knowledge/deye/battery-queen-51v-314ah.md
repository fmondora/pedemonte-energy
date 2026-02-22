# Batteria - Battery Queen 51.2V 314Ah

> Fonte: [Alibaba product listing](https://www.alibaba.com/product-detail/Poland-stock-48V-51-2V-314ah_1601524374076.html)

## Identificazione

- **Brand**: Battery Queen (OEM cinese)
- **Modello**: 51.2V 314Ah
- **Chimica**: LiFePO4 (Litio Ferro Fosfato)
- **Configurazione celle**: 16S (16 celle in serie da 3.2V)
- **Stock**: Polonia

## Specifiche Tecniche

| Parametro | Valore |
|---|---|
| Tensione nominale | 51.2V |
| Capacità | 314 Ah |
| Energia | **~16 kWh** |
| Chimica | LiFePO4 |
| Tensione di carica | 57.6V (tipica) |
| Tensione di scarica minima | 44.8V (tipica) |
| BMS integrato | Sì |
| Corrente max carica | 150-200A (da verificare) |
| Corrente max scarica | 150-200A (da verificare) |
| Protocolli comunicazione | CAN / RS485 (tipici per questa classe) |
| Cicli vita | 6000-8000+ cicli (a 80% DOD, 80% SOH) |
| Montaggio | Wall-mount / Floor-mount |
| Protezione | IP65 (tipica) |

## Compatibilità con Deye SUN-12K-SG04LP3-EU

| Parametro Deye | Valore Configurato | Compatibilità |
|---|---|---|
| Batt Type | BMS Lithium Batt | OK - LiFePO4 con BMS |
| Battery Capacity | 340 Ah | **Da verificare** - nominale è 314Ah |
| Max A Charge | 200 A | Da verificare vs specifiche BMS batteria |
| Max A Discharge | 200 A | Da verificare vs specifiche BMS batteria |
| Tensione batteria | 40-60V | OK - 51.2V rientra nel range |
| Protocollo | CAN / RS485 | Da verificare quale è in uso |

## Note

- La capacità configurata nell'inverter (340 Ah) è diversa dalla capacità nominale della batteria (314 Ah). **Questo potrebbe causare errori nel calcolo del SOC da parte dell'inverter** — il SOC mostrato potrebbe non corrispondere al SOC reale
- Da verificare il datasheet esatto con il produttore per confermare corrente max carica/scarica e protocollo di comunicazione in uso
- La batteria comunica probabilmente via CAN bus con il BMS che gestisce bilanciamento celle, protezioni e limiti di corrente

## TODO

- [ ] Verificare il datasheet esatto del produttore
- [ ] Correggere Battery Capacity nell'inverter da 340Ah a 314Ah
- [ ] Verificare quale protocollo di comunicazione è in uso (CAN o RS485)
- [ ] Verificare corrente max carica/scarica del BMS
