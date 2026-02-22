# Pedemonte Energy - Knowledge Base

## Obiettivo del Progetto

L'obiettivo principale di questo progetto è configurare la casa di Pedemonte in modo che sia **il più possibile autosufficiente dal punto di vista energetico**.

## Contesto

La casa è equipaggiata con un sistema fotovoltaico e accumulo a batteria. L'obiettivo è massimizzare l'autoconsumo dell'energia prodotta dai pannelli solari, minimizzare i prelievi dalla rete elettrica e ottimizzare i flussi energetici tra produzione, consumo, accumulo e rete.

## Principi Guida

1. **Autoconsumo prima di tutto**: l'energia prodotta deve essere consumata localmente prima di essere immessa in rete
2. **Accumulo intelligente**: le batterie devono essere caricate e scaricate in modo ottimale per massimizzare l'autonomia
3. **Riduzione dei costi**: minimizzare il costo della bolletta elettrica sfruttando fasce orarie e incentivi
4. **Sicurezza dell'impianto**: ogni configurazione deve rispettare le normative CEI e garantire la sicurezza dell'impianto
5. **Resilienza**: l'impianto deve poter funzionare anche in caso di blackout (se supportato dall'inverter)

## Componenti del Sistema

- **Inverter**: il cuore del sistema, gestisce la conversione DC/AC e i flussi energetici
- **Pannelli fotovoltaici**: producono energia elettrica dal sole
- **Batterie di accumulo**: immagazzinano l'energia in eccesso per uso successivo
- **Rete elettrica**: fonte di backup e destinazione per l'energia in eccesso
- **Carichi domestici**: tutti i dispositivi che consumano energia in casa

## Metriche di Successo

- **Tasso di autoconsumo** (%) - energia autoconsumata / energia prodotta
- **Tasso di autosufficienza** (%) - energia autoconsumata / energia totale consumata
- **Risparmio in bolletta** (EUR/anno)
- **Cicli batteria** - ottimizzare per prolungare la vita delle batterie
- **Potenza di picco immessa in rete** - minimizzare per evitare limitazioni

## Struttura della Knowledge Base

Questa directory contiene tutta la conoscenza condivisa tra gli agenti:

- `knowledge.md` - questo file, obiettivi e contesto generale
- `deye/` - conoscenza specifica sugli inverter Deye
- `solaredge/` - conoscenza specifica sugli inverter SolarEdge
- `optimizations/` - strategie di ottimizzazione e risultati
- `configurations/` - configurazioni applicate e loro effetti
- `logs/` - log delle decisioni prese e motivazioni
