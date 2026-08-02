#!/usr/bin/env python3.12
"""Genera il sito statico di Casa Pedemonte da manuale/ + manuale/_meta.yaml.

Il FRAMING (aree, titoli, ledi, foto, materiali) viene da _meta.yaml; i CONTENUTI
delle sezioni dai markdown bilingui manuale/ospiti/<slug>.<lang>.md.

Output: una pagina per lingua con navigazione ad aree (client-side), foto di
testata, identità materica e motivo rododendro. HTML statico, CSS inline,
immagini e video referenziati da site/assets/ (nessun base64). Il toggle lingua è un link
tra site/index.html (default) e site/<lang>/index.html.

Uso:
    python3.12 scripts/build_site.py            # solo sezioni pubblicate
    python3.12 scripts/build_site.py --drafts   # include anche le bozze (anteprima)
    python3.12 scripts/build_site.py --out dist
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "manuale" / "ospiti"
ASSETS = ROOT / "manuale" / "assets"
META = ROOT / "manuale" / "_meta.yaml"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def L(node, lang):
    """Ritorna il valore localizzato (node[lang]) o node se non è un dict lingua."""
    if isinstance(node, dict) and (lang in node):
        return node[lang]
    return node


def parse_note(slug: str, lang: str) -> dict | None:
    path = SRC / f"{slug}.{lang}.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        raise ValueError(f"Front-matter mancante in {path.name}")
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(
            f"Front-matter YAML non valido in {path.name}: {e}\n"
            f"  (i valori con ':' vanno tra virgolette, es. title: \"Clima: ...\")") from e
    return {"meta": fm, "body": m.group(2).strip(), "path": path}


def publishable(fm: dict, drafts: bool) -> bool:
    if fm.get("audience", "ospite") != "ospite":
        return False
    return drafts or fm.get("status") == "pubblicato"


def md_html(body: str) -> str:
    m = markdown.Markdown(extensions=["extra", "sane_lists"])
    return m.convert(body)


# ---------------------------------------------------------------- render blocks
def render_entry(sec: dict, lang: str, drafts: bool, prefix: str) -> str | None:
    note = parse_note(sec["slug"], lang)
    if note is None or not publishable(note["meta"], drafts):
        return None
    title = html.escape(note["meta"].get("title", sec["slug"]))
    mat = L(sec.get("mat"), lang)
    mat_html = f'<span class="mat">{html.escape(mat)}</span>' if mat else ""
    body = md_html(note["body"])
    # I body markdown referenziano le immagini come ../assets/... (relativo a
    # manuale/ospiti/); normalizza al percorso corretto per la pagina generata.
    body = re.sub(r'src="(?:\.\./)*assets/', f'src="{prefix}assets/', body)
    return (f'<div class="entry"><div class="side">{mat_html}<h3>{title}</h3></div>'
            f'<div class="body">{body}</div></div>')


def render_area(area: dict, lang: str, drafts: bool, prefix: str, empty_txt: str,
                all_areas: str) -> str:
    entries = [render_entry(s, lang, drafts, prefix) for s in area.get("sections", [])]
    entries = [e for e in entries if e]
    body = "\n".join(entries) or f'<p class="empty">{html.escape(empty_txt)}</p>'
    cls = "area dark" if area.get("dark") else "area"
    photo = f"{prefix}assets/{area['photo']}"
    mat = html.escape(L(area["mat"], lang))
    return f"""<section id="{area['key']}" class="{cls}">
  <div class="banner area-banner" style="--img:url('{photo}')">
    <svg class="sprig" aria-hidden="true"><use href="#vite"/></svg>
    <div class="wrap">
      <button class="back" data-go="home">&larr; {html.escape(all_areas)}</button>
      <span class="mat">{mat}</span>
      <h2>{html.escape(L(area['title'], lang))}</h2>
      <p class="lede">{html.escape(L(area['lede'], lang))}</p>
    </div>
  </div>
  <div class="wrap entries">
{body}
  </div>
</section>"""


def render_home(meta: dict, lang: str, prefix: str) -> str:
    h = meta["home"]
    cards = []
    for a in meta["areas"]:
        tags = "".join(f"<span>{html.escape(str(t))}</span>" for t in L(a["tags"], lang))
        cards.append(
            f'<button class="card" data-go="{a["key"]}"><span class="n">{a["n"]}</span>'
            f'<h3>{html.escape(L(a["title"], lang))}</h3>'
            f'<p>{html.escape(L(a["card"], lang))}</p>'
            f'<div class="tags">{tags}</div></button>')
    return f"""<section id="home" class="area on">
  <div class="banner hero" style="--img:url('{prefix}assets/{h['photo']}')">
    <svg class="sprig" aria-hidden="true"><use href="#vite"/></svg>
    <div class="ember" aria-hidden="true"></div>
    <div class="wrap">
      <p class="place">{html.escape(L(h['eyebrow'], lang))}</p>
      <h1>{L(h['h1'], lang)}</h1>
      <p class="sub">{html.escape(L(h['sub'], lang))}</p>
    </div>
  </div>
  <div class="wrap">
    <div class="cards">{''.join(cards)}</div>
    <p class="intro">{L(h['intro'], lang)}</p>
  </div>
</section>"""


def render_page(meta: dict, lang: str, drafts: bool, prefix: str, other_href: str) -> str:
    s = meta["strings"][lang]
    nav = "".join(
        f'<button data-go="{a["key"]}">{html.escape(L(a["title"], lang))}</button>'
        for a in meta["areas"])
    areas_html = "\n".join(
        render_area(a, lang, drafts, prefix, s["empty"], s["all_areas"])
        for a in meta["areas"])
    other_lang = html.escape(s["lang_label"])
    lang_ctrl = (f'<a class="lang" href="{other_href}"><b>IT</b> &middot; EN</a>'
                 if lang == "it" else
                 f'<a class="lang" href="{other_href}">IT &middot; <b>EN</b></a>')
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
<title>{html.escape(s['title'])} &mdash; {'Guida della casa' if lang=='it' else 'House guide'}</title>
<style>{CSS}</style>
</head>
<body>
{SVG_DEFS}
<header class="topbar">
  <div class="wrap">
    <button class="brand" data-go="home">{html.escape(s['title'])}<small>{html.escape(meta['place'])}</small></button>
    <nav class="areas" aria-label="aree">{nav}</nav>
    <button class="iconbtn" id="searchBtn" aria-label="{html.escape(s['search_label'])}"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></button>
    {lang_ctrl}
  </div>
</header>
<div class="search-overlay" id="searchOverlay" hidden>
  <div class="search-box" role="dialog" aria-modal="true" aria-label="{html.escape(s['search_label'])}">
    <input type="search" id="searchInput" placeholder="{html.escape(s['search'])}" autocomplete="off" spellcheck="false">
    <div class="search-results" id="searchResults" data-empty="{html.escape(s['search_empty'])}"></div>
  </div>
</div>
<main>
{render_home(meta, lang, prefix)}
{areas_html}
</main>
<div class="wrap"><footer>
  <span><svg class="sprig" aria-hidden="true"><use href="#vite"/></svg>Casa Pedemonte &middot; Berbenno &middot; <span class="mono">sacredspace.it/spaces/pedemonte</span></span>
  <span>{html.escape(s['footer'])}</span>
</footer></div>
<script>{NAV_JS}{SEARCH_JS}</script>
</body>
</html>
"""


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Genera il sito statico di Casa Pedemonte.")
    ap.add_argument("--drafts", action="store_true", help="includi le sezioni in bozza")
    ap.add_argument("--out", default="site", help="cartella di output (default: site)")
    args = ap.parse_args()

    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    languages = meta["site"]["languages"]
    default = meta["site"].get("default_language", languages[0])
    out_root = ROOT / args.out

    for lang in languages:
        if lang == default:
            page_dir, prefix = out_root, ""
            other = [l for l in languages if l != lang][0]
            other_href = f"{other}/"
        else:
            page_dir, prefix = out_root / lang, "../"
            other_href = "../"
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            render_page(meta, lang, args.drafts, prefix, other_href), encoding="utf-8")
        # conteggio sezioni incluse
        n = sum(1 for a in meta["areas"] for s in a["sections"]
                if (note := parse_note(s["slug"], lang)) and publishable(note["meta"], args.drafts))
        print(f"[{lang}] {n} sezioni -> {(page_dir / 'index.html').relative_to(ROOT)}")

    if ASSETS.is_dir():
        shutil.copytree(ASSETS, out_root / "assets", dirs_exist_ok=True)
        print(f"[assets] {ASSETS.relative_to(ROOT)} -> {(out_root / 'assets').relative_to(ROOT)}")
    (out_root / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out_root / "favicon.svg").write_text(FAVICON, encoding="utf-8")

    print(f"\nFatto. Apri: {out_root / 'index.html'}")
    return 0


# ================================================================ assets (CSS/SVG/JS)
CSS = """
  :root{
    --bg:#e9e3d5; --panel:#f3eee1; --panel-2:#ece5d5;
    --ink:#26241f; --muted:#6e6a5c; --line:#d5cdb9;
    --rame:#8c5a3c; --uva:#8d5b7a; --uva-scuro:#6d4059; --uva-luce:#d8bcd0;
    --vt-leaf:#6f8a52; --vt-vein:#4d6339;
    --serp:#22211d; --serp-panel:#2b2a25; --serp-ink:#ece6d8;
    --serp-muted:#a09a89; --serp-line:#3b382f; --serp-rame:#c08a5e;
    --overlay-ink:#f4efe4; --overlay-soft:#e7dfd0;
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
    --sans:ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif;
    --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --maxw:70rem;
  }
  @media (prefers-color-scheme:dark){
    :root:not([data-theme="light"]){--bg:#191814;--panel:#221f1a;--panel-2:#272319;
      --ink:#ece6d8;--muted:#9d9787;--line:#332f27;--rame:#bb8459;}
  }
  :root[data-theme="dark"]{--bg:#191814;--panel:#221f1a;--panel-2:#272319;
    --ink:#ece6d8;--muted:#9d9787;--line:#332f27;--rame:#bb8459;}
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
    font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
  .wrap{max-width:var(--maxw);margin:0 auto;padding:0 clamp(1.1rem,4vw,2.5rem)}
  .topbar{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--bg) 88%,transparent);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .topbar .wrap{display:flex;align-items:center;gap:1.4rem;height:62px}
  .brand{font-family:var(--serif);font-size:1.5rem;font-weight:600;background:none;border:0;
    color:var(--ink);cursor:pointer;padding:0;line-height:1}
  .brand small{display:block;font-family:var(--sans);font-size:.6rem;letter-spacing:.28em;
    text-transform:uppercase;color:var(--muted);margin-top:.2rem;font-weight:600}
  nav.areas{margin-left:auto;display:flex;gap:.15rem;flex-wrap:wrap}
  nav.areas button{font-family:var(--sans);font-size:.83rem;color:var(--muted);background:none;
    border:0;cursor:pointer;padding:.5rem .7rem;border-radius:999px;text-transform:lowercase}
  nav.areas button:hover{color:var(--ink)}
  nav.areas button[aria-current="true"]{color:var(--ink);background:color-mix(in srgb,var(--rame) 16%,transparent)}
  .lang{font-family:var(--mono);font-size:.72rem;color:var(--muted);border:1px solid var(--line);
    border-radius:999px;padding:.3rem .6rem;text-decoration:none;white-space:nowrap}
  .lang:hover{color:var(--ink)} .lang b{color:var(--rame)}
  .area{display:none;animation:rise .5s ease both}
  .area.on{display:block}
  @keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
  @media (prefers-reduced-motion:reduce){.area{animation:none}}
  .mat{font-family:var(--sans);font-size:.68rem;font-weight:700;letter-spacing:.18em;
    text-transform:uppercase;color:var(--rame);display:inline-block;margin-bottom:.5rem}
  h1,h2,h3{font-family:var(--serif);font-weight:600;text-wrap:balance;line-height:1.12;margin:0}
  .lede{font-size:1.15rem;line-height:1.6;max-width:34em}
  .banner{position:relative;display:flex;align-items:flex-end;overflow:hidden;isolation:isolate;background:var(--serp)}
  .banner.hero{min-height:clamp(76vh,82vh,90vh)}
  .banner.area-banner{min-height:clamp(42vh,50vh,58vh)}
  .banner::before{content:"";position:absolute;inset:0;z-index:-2;
    background-image:var(--img);background-size:cover;background-position:center}
  .banner::after{content:"";position:absolute;inset:0;z-index:-1;
    background:linear-gradient(180deg,rgba(14,18,13,.26),rgba(14,18,13,.5) 55%,rgba(14,18,13,.9))}
  .banner .wrap{padding-top:clamp(2rem,6vw,4rem);padding-bottom:clamp(1.8rem,5vw,3.2rem);
    color:var(--overlay-ink);width:100%}
  .banner h1,.banner h2{color:var(--overlay-ink)}
  .banner .lede,.banner .sub{color:var(--overlay-soft)}
  .banner .mat{color:var(--serp-rame)}
  .hero h1{font-size:clamp(3rem,10vw,6rem)}
  .hero .place{font-family:var(--mono);font-size:.76rem;letter-spacing:.22em;text-transform:uppercase;
    color:var(--serp-rame);margin:0 0 1.1rem}
  .hero .sub{font-size:1.2rem;max-width:32em;margin:1.2rem 0 0}
  .ember{position:absolute;inset:auto 0 -40% 0;height:70%;z-index:-1;pointer-events:none;
    background:radial-gradient(55% 100% at 50% 100%,rgba(210,130,55,.5),rgba(200,110,40,.1) 45%,transparent 70%);
    animation:flick 6s ease-in-out infinite}
  @keyframes flick{0%,100%{opacity:.8}50%{opacity:1}}
  @media (prefers-reduced-motion:reduce){.ember{animation:none}}
  .area-banner h2{font-size:clamp(2rem,6vw,3.2rem)}
  .area-banner .lede{margin-top:.9rem}
  .back{font-family:var(--sans);font-size:.82rem;color:var(--overlay-soft);background:none;border:0;
    cursor:pointer;padding:.3rem 0;margin-bottom:.4rem}
  .back:hover{color:#fff}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1px;
    background:var(--line);border:1px solid var(--line);margin:clamp(2.2rem,5vw,3.5rem) 0}
  .card{background:var(--panel);border:0;text-align:left;cursor:pointer;padding:1.6rem 1.5rem 1.7rem;
    display:flex;flex-direction:column;gap:.5rem;transition:background .25s;color:inherit;font:inherit}
  .card:hover{background:var(--panel-2)}
  .card .n{font-family:var(--mono);font-size:.72rem;color:var(--rame);letter-spacing:.1em}
  .card h3{font-size:1.55rem}
  .card p{margin:0;color:var(--muted);font-size:.95rem;line-height:1.5}
  .card .tags{margin-top:.4rem;display:flex;flex-wrap:wrap;gap:.35rem}
  .card .tags span{font-size:.72rem;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:.12rem .55rem}
  .card:hover h3{color:var(--rame)}
  .intro{max-width:38rem;margin:clamp(2.2rem,6vw,3.6rem) 0 0;font-size:1.15rem;color:var(--muted)}
  .intro b{color:var(--ink);font-weight:600}
  .entries{padding-bottom:1rem}
  .entry{border-top:1px solid var(--line);padding:2.1rem 0;display:grid;
    grid-template-columns:minmax(0,13rem) minmax(0,1fr);gap:clamp(1rem,4vw,3rem)}
  .entry:last-child{border-bottom:1px solid var(--line)}
  .entry h3{font-size:1.5rem}
  .entry .body :is(h2,h3,h4){font-family:var(--serif);font-size:1.05rem;margin:1.4rem 0 .3rem}
  .entry .body p{margin:.2rem 0 .9rem}
  .entry .body p:last-child{margin-bottom:0}
  .entry .body strong{color:var(--ink)}
  .entry .body ul,.entry .body ol{margin:.2rem 0 .9rem;padding-left:1.2rem}
  .entry .body li{margin:.2rem 0}
  .entry .body code{font-family:var(--mono);font-size:.9em;background:var(--panel);
    border:1px solid var(--line);border-radius:.35rem;padding:.05rem .35rem}
  /* Le foto del manuale sono spesso verticali (scatti da telefono): senza un tetto
     all'altezza riempirebbero lo schermo e spezzerebbero la lettura. width:auto
     lascia che sia l'altezza a vincolare i ritratti, la larghezza i panorami. */
  .entry .body img{max-width:100%;width:auto;height:auto;max-height:34rem;
    border-radius:8px;margin:.7rem 0;display:block}
  .entry .body video{max-width:100%;width:auto;height:auto;max-height:34rem;
    border-radius:8px;margin:.7rem 0;background:#000;display:block}
  .entry .body img[src$=".svg"]{width:150px;max-height:none;border-radius:0;margin:1rem 0}
  .entry .body img[src$=".svg"]{width:150px;border-radius:0;margin:1rem 0}
  @media (max-width:640px){.entry{grid-template-columns:1fr;gap:.6rem}}
  .empty{color:var(--muted)}
  .dark{background:var(--serp);color:var(--serp-ink)}
  .dark .entries .entry{border-color:var(--serp-line)}
  .dark .entry .body p,.dark .empty{color:var(--serp-muted)}
  .dark .entry h3,.dark .entry .body strong,.dark .entry .body :is(h2,h3,h4){color:var(--serp-ink)}
  .dark .mat{color:var(--serp-rame)}
  .dark .entry .body code{background:var(--serp-panel);border-color:var(--serp-line);color:var(--serp-ink)}
  footer{border-top:1px solid var(--line);color:var(--muted);font-size:.82rem;
    padding:2.5rem 0 3.5rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem}
  footer .mono{font-family:var(--mono)}
  a{color:var(--rame)}
  :focus-visible{outline:2px solid var(--rame);outline-offset:2px;border-radius:3px}
  .sprig{display:inline-block;color:var(--vt-leaf)}
  .banner .sprig{position:absolute;right:clamp(1rem,5vw,3.5rem);top:1.4rem;
    width:clamp(52px,8vw,88px);opacity:.95;pointer-events:none;z-index:1}
  footer .sprig{width:24px;height:28px;opacity:.75;vertical-align:-6px;margin-right:.5rem}
  .iconbtn{display:inline-grid;place-items:center;width:32px;height:32px;border-radius:999px;
    border:1px solid var(--line);background:none;color:var(--muted);cursor:pointer;flex:none}
  .iconbtn:hover{color:var(--ink)}
  .search-overlay{position:fixed;inset:0;z-index:50;background:rgba(10,14,10,.5);
    backdrop-filter:blur(4px);display:flex;justify-content:center;padding:12vh 1rem 1rem}
  .search-overlay[hidden]{display:none}
  .search-box{width:min(94vw,40rem);height:fit-content;max-height:76vh;display:flex;flex-direction:column;
    background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;
    box-shadow:0 24px 70px rgba(0,0,0,.35)}
  .search-box input{border:0;padding:1.1rem 1.3rem;font-size:1.15rem;font-family:var(--serif);
    background:transparent;color:var(--ink);outline:none}
  .search-results{overflow:auto;border-top:1px solid var(--line)}
  .search-results:empty{display:none}
  .sr{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;width:100%;text-align:left;
    background:none;border:0;border-bottom:1px solid var(--line);padding:.85rem 1.3rem;cursor:pointer;color:inherit;font:inherit}
  .sr:last-child{border-bottom:0}
  .sr:hover{background:var(--panel-2)}
  .sr b{font-family:var(--serif);font-weight:600;font-size:1.05rem}
  .sr span{color:var(--rame);font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;white-space:nowrap}
  .sr-empty{padding:1rem 1.3rem;color:var(--muted);margin:0}
  @media (max-width:720px){
    nav.areas{display:none}          /* su mobile si naviga da home/ricerca/back */
    #searchBtn{margin-left:auto}
    .brand{font-size:1.35rem}
    .hero h1{font-size:clamp(2.6rem,15vw,3.4rem)}
    .entry{padding:1.6rem 0}
  }
"""

SVG_DEFS = """<svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs>
  <g id="vt-acino">
    <circle r="4.6" fill="var(--uva)" stroke="var(--uva-scuro)" stroke-width=".9"/>
    <circle cx="-1.4" cy="-1.6" r="1.5" fill="var(--uva-luce)" opacity=".55"/>
  </g>
  <symbol id="vite" viewBox="0 0 120 140">
    <!-- tralcio -->
    <path d="M60 138 C 57 116 59 100 63 88" fill="none" stroke="var(--vt-leaf)" stroke-width="2.2" stroke-linecap="round"/>
    <!-- viticcio -->
    <path d="M63 96 C 78 92 84 84 79 78 C 74 73 68 78 72 83"
          fill="none" stroke="var(--vt-leaf)" stroke-width="1.7" stroke-linecap="round"/>
    <!-- foglia di vite, palmata a cinque lobi -->
    <path d="M40 84 C 24 80 18 66 24 56 C 30 47 42 46 46 38 C 50 46 62 47 68 56
             C 74 66 66 80 52 84 C 49 88 43 88 40 84 Z"
          fill="var(--vt-leaf)" opacity=".92"/>
    <path d="M46 84 C 46 72 46 60 46 40" fill="none" stroke="var(--vt-vein)" stroke-width="1.1" opacity=".7"/>
    <path d="M46 66 C 38 62 32 58 28 54 M46 66 C 54 62 60 58 64 54" fill="none"
          stroke="var(--vt-vein)" stroke-width="1" opacity=".6"/>
    <!-- grappolo -->
    <use href="#vt-acino" transform="translate(76 96)"/>
    <use href="#vt-acino" transform="translate(86 99)"/>
    <use href="#vt-acino" transform="translate(81 105)"/>
    <use href="#vt-acino" transform="translate(91 108)"/>
    <use href="#vt-acino" transform="translate(80 114)"/>
    <use href="#vt-acino" transform="translate(89 118)"/>
    <use href="#vt-acino" transform="translate(84 125)"/>
  </symbol>
</defs></svg>"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="7" fill="#2a2620"/>
<path d="M16 7 C 12 10 9 13 9 17 C 9 21 12 23 16 23 C 20 23 23 21 23 17 C 23 13 20 10 16 7 Z"
      fill="#6f8a52" opacity=".9"/>
<g fill="#8d5b7a" stroke="#6d4059" stroke-width=".6">
  <circle cx="16" cy="19" r="3"/><circle cx="12.6" cy="16.4" r="2.7"/><circle cx="19.4" cy="16.4" r="2.7"/>
  <circle cx="16" cy="13.6" r="2.7"/>
</g>
<circle cx="15" cy="18" r=".9" fill="#c7a7bd" opacity=".6"/>
</svg>"""

NAV_JS = """
  var areas = Array.prototype.slice.call(document.querySelectorAll('.area'));
  var navBtns = Array.prototype.slice.call(document.querySelectorAll('nav.areas button'));
  function go(id){
    areas.forEach(function(a){ a.classList.toggle('on', a.id === id); });
    navBtns.forEach(function(b){ b.setAttribute('aria-current', String(b.dataset.go === id)); });
    window.scrollTo({top:0});
    if(history.replaceState) history.replaceState(null,'','#'+id);
  }
  document.addEventListener('click', function(e){
    var t = e.target.closest('[data-go]'); if(!t) return;
    e.preventDefault(); go(t.dataset.go);
  });
  window.addEventListener('hashchange', function(){
    var h = (location.hash||'').replace('#','');
    if(h && document.getElementById(h)) go(h);
  });
  var start = (location.hash||'').replace('#','');
  if(start && document.getElementById(start)) go(start);
"""

SEARCH_JS = """
  (function(){
    var overlay = document.getElementById('searchOverlay');
    var input = document.getElementById('searchInput');
    var results = document.getElementById('searchResults');
    var btn = document.getElementById('searchBtn');
    if(!overlay || !input || !results || !btn) return;
    var idx = [];
    Array.prototype.forEach.call(document.querySelectorAll('main .area'), function(area){
      if(area.id === 'home') return;
      var h2 = area.querySelector('h2');
      var at = h2 ? h2.textContent : area.id;
      Array.prototype.forEach.call(area.querySelectorAll('.entry'), function(entry, i){
        if(!entry.id) entry.id = 's-' + area.id + '-' + i;
        var h3 = entry.querySelector('h3');
        idx.push({id: entry.id, area: area.id, at: at,
          title: h3 ? h3.textContent : at, text: (entry.textContent || '').toLowerCase()});
      });
    });
    function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function open(){ overlay.hidden = false; input.value=''; results.innerHTML=''; input.focus(); }
    function close(){ overlay.hidden = true; }
    btn.addEventListener('click', open);
    overlay.addEventListener('click', function(e){ if(e.target === overlay) close(); });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape' && !overlay.hidden) close(); });
    input.addEventListener('input', function(){
      var q = this.value.trim().toLowerCase();
      if(q.length < 2){ results.innerHTML = ''; return; }
      var ms = idx.filter(function(it){ return it.text.indexOf(q) !== -1; }).slice(0, 12);
      if(!ms.length){ results.innerHTML = '<p class="sr-empty">' + esc(results.dataset.empty || '') + '</p>'; return; }
      results.innerHTML = ms.map(function(m){
        return '<button class="sr" data-t="' + m.id + '" data-a="' + m.area + '">' +
               '<b>' + esc(m.title) + '</b><span>' + esc(m.at) + '</span></button>';
      }).join('');
    });
    results.addEventListener('click', function(e){
      var b = e.target.closest('.sr'); if(!b) return;
      close();
      go(b.getAttribute('data-a'));
      var el = document.getElementById(b.getAttribute('data-t'));
      if(el) setTimeout(function(){ el.scrollIntoView({behavior:'smooth', block:'center'}); }, 80);
    });
  })();
"""

if __name__ == "__main__":
    raise SystemExit(main())
