# 2026-02-22 - Modifica Backup Reserve (Raccomandazione Team)

## Modifiche Effettuate

| Parametro | Valore precedente | Nuovo valore |
|---|---|---|
| Batt Low % | 15% | **20%** |
| Batt Restart % | 50% | **35%** |
| TOU Batt % (tutte le 6 fasce) | 10% | **20%** |

## Motivazione
Analisi del team (deye-expert + electrical-engineer) in risposta al commento di Davide Duca sulla necessita di una riserva di backup. Il 20% offre ~4 ore di autonomia in blackout (copre 99.9% dei casi italiani) senza sacrificare troppo autoconsumo notturno.

## Documenti di Riferimento
- `knowledge/deye/backup-soc-analysis.md` - Analisi tecnica deye-expert
- `knowledge/optimizations/backup-reserve-vs-autoconsumo.md` - Analisi ingegneristica

## Verifica
Controllare lo storico consumi della notte 22-23/02/2026 per verificare che:
- La batteria si scarichi fino al 20% e poi passi alla rete
- L'autonomia notturna sia adeguata
- Non ci siano anomalie di comportamento
