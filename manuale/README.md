# Manuale di Casa Pedemonte

Sorgente del sito pubblicato su **sacredspace.it/spaces/pedemonte**.

## Com'è fatto

- `_meta.yaml` — il **framing**: aree, titoli, ledi, foto di testata, ordine delle sezioni.
- `ospiti/<slug>.<lang>.md` — i **contenuti**, uno per sezione e per lingua (`it`, `en`).
- `assets/` — immagini e video referenziati dai markdown come `../assets/nome.jpg`.

I markdown non sanno nulla di aree o di ordine: si riorganizza il sito toccando solo
`_meta.yaml`, si riscrive un contenuto toccando solo il suo markdown.

## Front-matter

```yaml
---
title: La cucina
audience: ospite        # 'ospite' = pubblicabile; qualsiasi altro valore = mai pubblicato
status: pubblicato      # 'pubblicato' | 'bozza'
updated: 2026-08-02
---
```

Le **bozze** non finiscono in produzione: si vedono solo con `--drafts`.

## Comandi

```bash
python3.12 scripts/build_site.py            # build in site/ (solo pubblicate)
python3.12 scripts/build_site.py --drafts   # anteprima con le bozze
python3.12 scripts/deploy_site.py           # build + deploy su Cloudflare Pages
```

Il Worker che monta il sito sotto `/spaces/pedemonte` sta in `cloudflare/worker/`
e si aggiorna solo se cambiano le route:

```bash
cd cloudflare/worker && npx wrangler@4 deploy
```

## Provenienza dei contenuti

Prima stesura ricavata dalla pagina Notion "Casa Pedemonte" (export completo in
`knowledge/notion/`). Il Notion resta la fonte storica; da qui in avanti la fonte di
verità è questa cartella.

Le foto ancora da fare sono elencate in `docs/foto-da-fare.md`.
