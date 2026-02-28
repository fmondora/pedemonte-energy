# Batteria - Battery Queen 51.2V 314Ah

> Fonti:
> - [Alibaba product listing](https://www.alibaba.com/product-detail/Poland-stock-48V-51-2V-314ah_1601524374076.html)
> - [Deligreen product page (Seplos V4)](https://deligreencs.com/products/pre-assembled-16kwh-51-2v-lifepo4-solar-battery-pack)
> - [Deligreen product page (JK V19)](https://deligreencs.com/products/eu-stock-jk-v19-51-2v-280ah-314ah-battery-pack-floor-standing-diy-kits-%E5%89%AF%E6%9C%AC)
> - [Deligreen V4 Datasheet](https://www.lithium-solarbattery.com/photo/lithium-solarbattery/document/89519/Deligreen%20V4%20%EF%BC%8851.2V-314AH%EF%BC%89datasheet%20.pdf)
> - [Deligreen su Made-in-China](https://deligreen.en.made-in-china.com/product/sZSTEgbAZfMX/)
> - [Seplos inverter compatibility](https://www.seplos.com/how-to-determine-if-an-inverter-can-communicate-with-seplos-bms.html)

## Identificazione

- **Brand**: Battery Queen (marchio commerciale)
- **Produttore**: **Changsha Deligreen Power Co., Ltd.** (Hunan, Cina)
  - Diamond Member su Alibaba dal 2019, Audited Supplier, Trading Company
  - Responsabile EU: E-CrossStu GmbH (Francoforte, Germania)
- **Negozi online**:
  - [Battery Queen Official Store (AliExpress)](https://batteryqueenofficial.aliexpress.com/store/1102244341)
  - [Battery Queen Energy Store (AliExpress)](https://batteryqueenenergy.aliexpress.com/store/1102273057)
  - [Deligreencs.com](https://deligreencs.com/)
  - [Deligreen su Made-in-China](https://deligreen.en.made-in-china.com/)
- **Modello**: 51.2V 314Ah (16kWh)
- **Chimica**: LiFePO4 (Litio Ferro Fosfato)
- **Configurazione celle**: 16S (16 celle in serie da 3.2V)
- **Celle utilizzate**: CALB A+ Grade (nella variante Seplos) o EVE MB31 Grade A+ (nella variante JK)
- **Stock**: Polonia (magazzino EU)

## Varianti Disponibili

Deligreen vende la batteria con due diverse opzioni BMS:

### Variante 1: Con Seplos V4 BMS
- BMS: Seplos Mason V4 (BMS 3.0) con bilanciamento attivo e ventole di raffreddamento
- Celle: CALB A+ Grade
- Touch screen integrato
- Protocolli: CAN & RS485
- Interruttore: 250A Air Circuit Breaker (tempo di risposta 0.1ms)
- Sistema antincendio: aerosol estinguente integrato

### Variante 2: Con JK V19 BMS
- BMS: JK-PB2A16S20P V19 con modulo limitazione corrente parallelo 10A integrato
- Celle: EVE MB31 Grade A+ o CALB
- Bluetooth integrato per monitoraggio
- Protocolli: CAN & RS485
- Interruttore: 250A Air Circuit Breaker (tempo di risposta 0.1ms)
- 500+ log di guasto per diagnostica

> **NOTA**: Non e' ancora confermato quale variante BMS sia installata a Pedemonte. Verificare fisicamente sulla batteria (touch screen = Seplos V4, app Bluetooth = JK V19).

## Specifiche Tecniche (Confermate)

| Parametro | Valore |
|---|---|
| Tensione nominale | 51.2V |
| Range operativo | 42V - 58.4V |
| Capacita' | 314 Ah |
| Energia nominale | **16 kWh** |
| Chimica | LiFePO4 |
| Corrente carica nominale | **100A** @ 25+/-2C |
| Corrente carica massima | **200A** @ 25+/-2C |
| Corrente scarica nominale | **200A** @ 25+/-2C |
| Corrente scarica massima | **200A** @ 25+/-2C |
| Protocolli comunicazione | **CAN & RS485** |
| Cicli vita | **8000 cicli** @ 25C, 50A carica/scarica, 80% DOD |
| Temperatura carica | 0C - 40C |
| Temperatura scarica | -20C - 60C |
| Dimensioni | 797 x 415 x 270 mm |
| Peso | ~132 kg (variante Seplos con celle CALB), ~32 kg (peso kit JK senza celle?) |
| Protezione | IP20 |
| Certificazione | CE |
| Montaggio | Floor-standing (a pavimento) |

## Connessione Parallelo Multi-Batteria

### Massimo batterie in parallelo: **16 unita'** (capacita' max: 256 kWh)

### Con Seplos V4 BMS:
- Le batterie in parallelo comunicano tra loro via **RS485** (daisy-chain)
- La batteria **master** si collega all'inverter via **CAN** (porta CAN)
- La comunicazione RS485 e' usata per il bus master-slave tra batterie
- **Importante**: Se l'inverter legge via CAN, il master NON e' leggibile via RS485 contemporaneamente (il DIP switch del master occupa l'RS485 per la comunicazione con gli slave)

#### Configurazione DIP Switch Seplos (parallelo):
- **1 sola batteria**: tutti i DIP switch OFF
- **2 batterie**: Master = DIP 1 ON, resto OFF; Slave = DIP 5 ON, resto OFF
- Bit 1-4: indirizzo del pack
- Bit 5-8: numero di slave packs

### Con JK V19 BMS:
- Supporta fino a **10 JK-BMS** (1 Master + 9 Slave) connessi via **CAN bus** al Deye
- Modulo limitazione corrente parallelo da 10A integrato

## Compatibilita' con Deye SUN-12K-SG04LP3-EU

### Compatibilita' Confermata

Il Deye SUN-12K-SG04LP3-EU e' **ufficialmente compatibile** con il BMS Seplos:
- Nella lista ufficiale Seplos: **Entry #28** - Deye SUN-12K-SG04LP3-EU via **RS485** (9600 baud)
- Nella lista ufficiale Seplos: **Entry #15** - Deye SUN-3/6K-SG03LP1-EU via **CAN**

### Configurazione Deye per Seplos BMS:
| Parametro Deye | Valore da impostare |
|---|---|
| Lithium Mode | **00** (Pylontech/CAN) oppure **12** (Modbus/RS485) |
| Batt Type | BMS Lithium Batt |
| Battery Capacity | **314 Ah** (attualmente impostato 340Ah - DA CORREGGERE) |
| Max A Charge | 200A (confermato dal datasheet) |
| Max A Discharge | 200A (confermato dal datasheet) |
| Connessione | CAN (COM1/COM2) oppure RS485 (COM3) |

### Configurazione Deye per JK BMS:
| Parametro Deye | Valore da impostare |
|---|---|
| Lithium Mode | **00** (CAN) |
| Protocollo JK BMS | Selezionare "Deye" nell'app Bluetooth JK |
| Connessione | CAN (cavo ethernet nella porta CAN dell'inverter + porta BMS del JK) |

### Opzioni di Connessione:
1. **CAN bus** (consigliato per singola batteria):
   - Porta CAN del Deye (COM1 o COM2) <-> Porta CAN del BMS
   - Lithium Mode: 00
   - Baud rate: 500K
2. **RS485** (alternativa):
   - Porta RS485 del Deye (COM3) <-> Porta RS485 del BMS
   - Lithium Mode: 12
   - Baud rate: 9600
3. **CAN + RS485** (per parallelo con Seplos):
   - CAN: master BMS <-> inverter Deye
   - RS485: daisy-chain tra batterie (master -> slave1 -> slave2 -> ...)

## Manuale di Installazione

**Non e' stato trovato un manuale specifico "Battery Queen"** - essendo un brand white-label di Deligreen, il manuale da seguire e' quello del BMS installato:

### Per Seplos V4:
- [Seplos Mason Installation Guide](https://www.seplos.com/article-5428374183056845.html)
- [Seplos V4 DIY Kit Manual (Fogstar)](https://www.fogstar.co.uk/a/knowledge-hub/seplos-diy-kits/seplos-v4-48v-diy-kit-user-manual)
- [Seplos BMS User Manual PDF](https://badenergy.dk/wp-content/uploads/2023/10/Seplos-48v-200A-8S-16S-BMS-User-Manual.pdf)
- [Seplos Communication Protocol v2.0](https://us.v-cdn.net/6034073/uploads/OJ8IDWBXR179/seplos-bms-communication-protocol-v2-0.pdf)

### Per JK V19:
- [JK BMS User Manual (PB series)](https://www.jkbms.com/wp-content/uploads/2024/06/JK-BMS-User-Manual-for-PB-series-jkbms.com_.pdf)

### Contatti Deligreen (supporto tecnico):
- Email: sales15@deligreenpower.com
- WhatsApp: +86 151 1640 9506

## Note Importanti

1. **Capacita' nell'inverter errata**: La capacita' configurata nel Deye (340 Ah) e' diversa dalla capacita' nominale della batteria (314 Ah). **Questo causa errori nel calcolo del SOC** - il SOC mostrato non corrisponde al SOC reale. DA CORREGGERE a 314Ah.

2. **Protocollo CAN con Seplos**: Il protocollo CAN di default Seplos e' compatibile con Pylontech, Goodwe, **Deye**, TBB. Opzionalmente supporta anche Growatt, Victron, SMA, Sofar, Solis, Studer.

3. **Peso**: Il dato di 132 kg nella variante Seplos e' plausibile per un pacco 16kWh LiFePO4 con case metallico. Il dato di 32 kg nella variante JK potrebbe riferirsi solo al kit senza celle.

4. **Garanzia**: Deligreen offre 3 anni di garanzia (standard), 10 anni sulla variante pre-assemblata premium.

## TODO

- [x] ~~Verificare il datasheet esatto del produttore~~ -> Identificato come Deligreen Power, datasheet trovato
- [x] ~~Verificare corrente max carica/scarica del BMS~~ -> 200A carica/200A scarica (confermato)
- [ ] **Correggere Battery Capacity nell'inverter da 340Ah a 314Ah**
- [ ] **Verificare fisicamente quale BMS e' installato** (Seplos V4 con touch screen OPPURE JK V19 con Bluetooth)
- [ ] **Verificare quale protocollo e' in uso** (CAN o RS485) controllando i cavi collegati all'inverter
- [ ] Verificare se il Deye Lithium Mode e' configurato correttamente (00 per CAN, 12 per RS485)
- [ ] Contattare Deligreen per il manuale specifico del prodotto acquistato
- [ ] Pianificare espansione parallelo se necessario (fino a 16 unita' supportate)
