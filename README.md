# Pedemonte Digital Home

Gestione della casa digitale di Pedemonte. L'obiettivo è rendere la casa autosufficiente dal punto di vista energetico e gestita in modo intelligente tramite Home Assistant e un team di agenti AI.

## Architettura Impianto

| Componente | Modello | Ruolo |
|---|---|---|
| **Inverter ibrido** | Deye SUN-12K-SG04LP3-EU | Batteria + backup (casa su uscita backup) |
| **Inverter PV** | SolarEdge SE10K-RWS | Produzione fotovoltaica |
| **Batteria** | Battery Queen 51.2V 314Ah | Accumulo LiFePO4 (~16 kWh) |
| **Stick Logger** | LSW-3-C | WiFi → Solarman cloud, Modbus TCP |
| **Domotica** | Home Assistant OS | Automazioni, monitoraggio, controllo |
| **EV Charger** | Tesla Wall Connector | Ricarica Biancaneve |

## Agenti AI

Il progetto utilizza 5 agenti Claude Code specializzati che lavorano in team:

### Team Energia
| Agente | Ruolo |
|---|---|
| `deye-expert` | Esperto inverter Deye: configurazione, batteria, backup, Modbus |
| `solaredge-expert` | Esperto inverter SolarEdge: ottimizzatori, StorEdge, monitoraggio |
| `electrical-engineer` | Ingegnere elettrico: analisi energetica, ottimizzazioni, dimensionamento |

### Team Domotica
| Agente | Ruolo |
|---|---|
| `homeassistant-expert` | Esperto HA: configurazione YAML, automazioni, API, integrazioni |
| `domotica-expert` | Esperto domotica: scenari, comfort, UX, logica di automazione |

Gli agenti condividono conoscenza tramite `knowledge/` e seguono pattern/anti-pattern nei file `.claude/agents/`.

## Struttura Repository

```
pedemonte-energy/              # Repo principale
├── knowledge/                 # Knowledge base condivisa
│   ├── knowledge.md           # Obiettivi e contesto
│   ├── system-architecture.md # Architettura multi-inverter
│   ├── deye/                  # Inverter Deye
│   ├── solaredge/             # Inverter SolarEdge
│   ├── optimizations/         # Strategie energetiche
│   ├── homeassistant/         # Conoscenza HA
│   ├── domotica/              # Scenari domotici
│   └── logs/                  # Storico decisioni
├── homeassistant/             # Submodule → pedemonte-homeassistant
└── .claude/agents/            # Definizione agenti AI
```

## Stato Attuale

Configurazione Deye ottimizzata per backup reserve (22/02/2026):
- Batt Low: 20% (riserva backup ~4 ore)
- Batt Restart: 35%
- TOU Batt: 20% su tutte le fasce
- Battery Capacity: 314 Ah (corretto da 340)
