# Foto da fare — Casa Pedemonte

Stato al 2026-08-02. Il sito è già online con le foto recuperate da Notion, ma quelle
sono quasi tutte **scatti funzionali da telefono** (filtri, valvole, armadietti): vanno
benissimo per spiegare, non per accogliere.

Questa lista è divisa per **urgenza**. La prima sezione è quella che cambia davvero il
sito; le altre migliorano sezioni già leggibili.

---

## 1. Le sei foto d'area — le uniche davvero mancanti

Sono le **immagini a tutta pagina** che aprono la home e ciascuna delle cinque sezioni.
Oggi cinque su sei sono segnaposto presi da altre foto: funzionano ma sono improprie.

Formato: **orizzontali**, minimo **2000 px** di lato lungo. Vengono ritagliate al centro
e coperte da una velatura scura con testo bianco sopra, quindi servono immagini con
**spazio "vuoto" nella metà bassa** (cielo, prato, pavimento) dove appoggiare il titolo.

| File | Cosa serve | Oggi c'è |
|---|---|---|
| `aree/hero.jpg` | **La casa vista da fuori**, possibilmente dal basso con i terrazzamenti o la valle dietro. È la prima immagine che vede chi apre il sito. | terrazza col tinozza (bella, ma già usata per *L'acqua*) |
| `aree/casa.jpg` | Un **interno vissuto**: la cucina-sala da pranzo con la luce del giorno, o la scala tra i piani. | foto della cucina, verticale e stretta |
| `aree/acqua.jpg` | **La terrazza sul tetto al tramonto**, con la tinozza accesa e il fumo del camino. | ✅ va già bene (stessa della hero) |
| `aree/fuori.jpg` | **Il giardino d'insieme**: l'orto, la vasca dei pesci, la montagna dietro. | primo piano di orchidee |
| `aree/pratico.jpg` | **L'ingresso o il garage aperto** con le bici in fila. | interno garage, buio |
| `aree/dintorni.jpg` | ✅ Piramidi di Postalesio — funziona bene | ✅ ok |

**Se puoi farne solo una: la hero.** È l'unica che non ha un sostituto decente.

---

## 2. Foto che sostituirebbero scatti poveri

Sezioni già complete, ma con immagini brutte o poco leggibili.

| Sezione | Foto | Perché |
|---|---|---|
| **La cucina** | La cucina intera, in orizzontale, con la luce naturale | Le due attuali sono strette e scure |
| **La tinozza** | La tinozza **accesa**, dettaglio della stufa a legna | Manca del tutto: si spiega come accenderla senza mostrarla |
| **Camere e biancheria** | Le camere (mansarda + secondo piano) | Ci sono solo gli armadi aperti |
| **Il garage** | Le bici in fila, e **dove sono i lucchetti** | Il testo cita "vicino alle finestre / armadio grigio" senza mostrarli |
| **Il giardino** | L'orto in stagione, e la **vasca dei pesci** d'insieme | C'è solo un dettaglio ravvicinato |
| **Le gatte** | **Paola e Ciaparat** | Non c'è nessuna foto delle gatte, e sono citate con affetto |

---

## 3. Foto istruttive che mancano

Sono passaggi in cui il testo dice "qui" senza poter mostrare dove.

- **Arrivo**: la facciata dalla strada, per riconoscerla arrivando in auto; e **dove si
  parcheggia**.
- **Rifiuti**: la **cassetta di legno con i sacchi**, e le **campane verdi vicino al
  parco giochi**. Oggi c'è solo un video.
- **Acqua**: i **due rubinetti in giardino** — il testo insiste che non sono potabili,
  ma non si vedono.
- **Corrente**: una **foto ferma del quadro** con gli interruttori principali indicati.
  Oggi c'è solo un video verticale girato di fretta.
- **La casa**: una **lampada di sale** accesa — è il primo dettaglio che raccontiamo e
  non si vede da nessuna parte. *(Si intravede in
  `armadietto-cloro-sportello.jpg`, ma di sfuggita.)*

---

## Come consegnarle

Mettile in `manuale/assets/` con il nome che vedi nelle tabelle (per le aree:
`manuale/assets/aree/hero.jpg` e simili), sovrascrivendo. Poi:

```bash
python3.12 scripts/deploy_site.py
```

Il build ridimensiona nulla in automatico: se la foto pesa più di ~1,5 MB, prima passala
con `sips -Z 2000 foto.jpg`.

---

## Nota sulle foto già recuperate da Notion

Attenzione ai nomi: **i filename dell'export Notion mentivano**. Il file che si chiamava
`Screenshot ... 11.35.48.png` non era uno screenshot ma **la foto della terrazza**, ed è
diventato la hero; le due immagini che sembravano "la tinozza" erano in realtà
**lo sportello e l'interno dell'armadietto del cloro**. Sono state rinominate di
conseguenza. Se aggiungi altre foto dall'export, **guardale prima di intitolarle**.
