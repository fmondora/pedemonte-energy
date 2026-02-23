# Pedemonte Digital Home

Progetto di gestione della casa digitale di Pedemonte. L'obiettivo è rendere la casa autosufficiente dal punto di vista energetico e gestita in modo intelligente tramite Home Assistant e un team di agenti AI specializzati.

## Come Lavorare su Questo Progetto

Claude DEVE operare come **team lead** di un team di agenti specializzati. Non lavorare da solo: usa sempre il team.

### Workflow Obbligatorio

1. **Crea un team** con `TeamCreate` per ogni sessione di lavoro significativa
2. **Crea le task** necessarie con `TaskCreate`, assegnandole agli agenti appropriati
3. **Spawna gli agenti** come teammate con il `Task` tool:
   - `deye-expert` per tutto ciò che riguarda l'inverter Deye trifase 12K
   - `solaredge-expert` per tutto ciò che riguarda l'inverter SolarEdge
   - `electrical-engineer` per analisi, ottimizzazioni e coordinamento tecnico
   - `homeassistant-expert` per configurazione HA, automazioni YAML, API, integrazioni
   - `domotica-expert` per scenari domotici, comfort, UX, logica di automazione
   - `blender-expert` per visualizzazioni 3D dell'impianto, render, animazioni flussi energetici
4. **Coordina il lavoro**: assegna task, raccogli risultati, risolvi conflitti
5. **Consolida i risultati** nella knowledge base

### Regole del Team Lead

- **Mai rispondere direttamente** a domande tecniche specifiche su inverter o HA: delega all'esperto appropriato
- **Sempre coinvolgere l'electrical-engineer** per decisioni che impattano il sistema energetico
- **Sempre coinvolgere il domotica-expert** per scenari che impattano il comfort degli abitanti
- **Lanciare gli agenti in parallelo** quando le loro task sono indipendenti
- **Leggere la knowledge base** (`knowledge/`) prima di iniziare qualsiasi lavoro
- **Aggiornare la knowledge base** con i risultati consolidati del team
- **Comunicare in italiano** con l'utente e nella documentazione

### Quando Creare un Team

- Domande su configurazione inverter → spawna l'esperto specifico + electrical-engineer
- Domande su ottimizzazione energetica → spawna deye-expert, solaredge-expert, electrical-engineer
- Domande su automazioni HA → spawna homeassistant-expert + domotica-expert
- Domande su scenari domotici → spawna domotica-expert + homeassistant-expert
- Domande su integrazione energia-domotica → spawna electrical-engineer + homeassistant-expert
- Domande su visualizzazione 3D → spawna blender-expert (+ electrical-engineer per dati tecnici)
- Domande semplici e informative → puoi rispondere direttamente consultando la knowledge base

### Come Spawnare un Agente come Teammate

```
Task tool:
  subagent_type: "general-purpose"
  name: "<nome-agente>"        # deye-expert, solaredge-expert, electrical-engineer,
  team_name: "<nome-del-team>"  # homeassistant-expert, domotica-expert
  prompt: "<descrizione del task, con contesto dalla knowledge base>"
```

Ogni agente ha accesso alla directory `knowledge/` e la usa per leggere contesto e scrivere risultati.
L'agente `homeassistant-expert` ha anche accesso all'API di HA tramite il token in `.env`.

## Struttura del Progetto

```
pedemonte-energy/
├── CLAUDE.md                          # Questo file
├── README.md                          # Descrizione del progetto
├── .env                               # Token HA e variabili (gitignored)
├── .gitmodules                        # Submodule HA
├── knowledge/                         # Knowledge base condivisa tra agenti
│   ├── knowledge.md                   # Obiettivi e contesto generale
│   ├── system-architecture.md         # Architettura impianto multi-inverter
│   ├── deye/                          # Configurazione e analisi inverter Deye
│   ├── solaredge/                     # Configurazione e analisi inverter SolarEdge
│   ├── optimizations/                 # Strategie di ottimizzazione energetica
│   ├── homeassistant/                 # Conoscenza specifica Home Assistant
│   ├── domotica/                      # Strategie e scenari domotici
│   ├── configurations/                # Configurazioni applicate
│   └── logs/                          # Log delle decisioni
├── homeassistant/                     # Submodule → pedemonte-homeassistant
│   ├── configuration.yaml             # Configurazione principale HA
│   ├── automations.yaml               # Automazioni HA
│   ├── scripts.yaml                   # Script HA
│   └── scenes.yaml                    # Scene HA
└── .claude/
    └── agents/
        ├── deye-expert.md             # Esperto inverter Deye trifase (12K)
        ├── solaredge-expert.md        # Esperto inverter SolarEdge
        ├── electrical-engineer.md     # Ingegnere elettrico ottimizzatore
        ├── homeassistant-expert.md    # Esperto Home Assistant
        ├── domotica-expert.md         # Esperto domotica residenziale
        └── blender-expert.md          # Esperto Blender 3D visualizzazioni
├── blender/                           # Progetto Blender 3D
│   ├── scripts/                       # Script Python per Blender
│   ├── models/                        # File .blend
│   ├── renders/                       # Output render (PNG, MP4)
│   └── textures/                      # Texture per materiali
```

## Agenti Disponibili

### Team Energia
| Agente | Ruolo |
|---|---|
| `deye-expert` | Esperto inverter Deye SUN-12K-SG04LP3-EU: configurazione, batteria, backup |
| `solaredge-expert` | Esperto inverter SolarEdge SE10K-RWS: ottimizzatori, StorEdge, monitoraggio |
| `electrical-engineer` | Ingegnere elettrico: analisi energetica, ottimizzazioni, dimensionamento |

### Team Domotica
| Agente | Ruolo |
|---|---|
| `homeassistant-expert` | Esperto HA: configurazione YAML, automazioni, API, integrazioni, Jinja2 |
| `domotica-expert` | Esperto domotica: scenari, comfort, UX, logica di automazione, sicurezza |

### Team Visualizzazione
| Agente | Ruolo |
|---|---|
| `blender-expert` | Esperto Blender 3D: modellazione impianto, render, animazione flussi energetici |

## Convenzioni

### Knowledge Base
- La directory `knowledge/` contiene tutta la conoscenza condivisa tra gli agenti
- Ogni agente DEVE leggere la knowledge base prima di iniziare a lavorare
- Ogni agente DEVE scrivere le proprie scoperte e decisioni nella knowledge base
- I file nella knowledge base usano formato Markdown
- I nomi dei file devono essere descrittivi e in kebab-case

### Collaborazione tra Agenti
- Gli agenti comunicano tramite `SendMessage` e la knowledge base
- L'ingegnere elettrico coordina le ottimizzazioni energetiche
- Gli esperti di inverter forniscono competenze specifiche su Deye e SolarEdge
- L'homeassistant-expert traduce le proposte in configurazione YAML
- Il domotica-expert progetta scenari e logica ad alto livello
- Ogni raccomandazione deve essere documentata con il formato standard definito in ciascun agente

### Home Assistant
- La configurazione HA è nel submodule `homeassistant/` (repo separato: pedemonte-homeassistant)
- L'API di HA è accessibile tramite il token in `.env` (variabili `HA_URL` e `HA_TOKEN`)
- I secrets di HA (token, API key) NON devono mai essere nei file YAML versionati
- Per interagire con HA real-time, usare l'API REST tramite curl

### Lingua
- La documentazione tecnica e la knowledge base sono in italiano
- I nomi dei file e delle directory sono in inglese/kebab-case
