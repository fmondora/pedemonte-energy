# Pedemonte Energy

Gestione energetica della casa di Pedemonte. L'obiettivo è rendere la casa il più possibile autosufficiente dal punto di vista energetico, massimizzando l'autoconsumo fotovoltaico e ottimizzando l'uso delle batterie di accumulo.

## Impianto

- **Inverter**: Deye SUN-12K-SG04LP3-EU (trifase, 12 kW)
- **Batteria**: BMS Lithium, 340 Ah (~17 kWh)
- **Modalità**: Selling First, Load First

## Agenti AI

Il progetto utilizza tre agenti Claude Code specializzati che lavorano in team:

| Agente | Ruolo |
|---|---|
| `deye-expert` | Esperto inverter Deye trifase 12K: configurazione, commissioning, troubleshooting |
| `solaredge-expert` | Esperto inverter SolarEdge: ottimizzatori, StorEdge, monitoraggio |
| `electrical-engineer` | Ingegnere elettrico: analisi energetica, ottimizzazioni, dimensionamento |

Gli agenti condividono conoscenza tramite la directory `knowledge/` e seguono pattern/anti-pattern documentati nei rispettivi file in `.claude/agents/`.

## Knowledge Base

```
knowledge/
├── knowledge.md              # Obiettivi e contesto generale
├── deye/                     # Configurazione e analisi inverter Deye
├── solaredge/                # Configurazione e analisi inverter SolarEdge
├── optimizations/            # Strategie di ottimizzazione energetica
├── configurations/           # Configurazioni applicate
└── logs/                     # Storico delle modifiche e decisioni
```

## Stato Attuale

Configurazione Deye ottimizzata per backup reserve (22/02/2026):
- Batt Low: 20% (riserva backup ~4 ore)
- Batt Restart: 35%
- TOU Batt: 20% su tutte le fasce
