#!/usr/bin/env python3.12
"""Build + deploy del sito Casa Pedemonte su Cloudflare Pages.

Genera il sito con build_site.py e lo pubblica alla radice del progetto Pages
`pedemonte`. Il dominio pubblico sacredspace.it/spaces/pedemonte è servito da un
Worker (cloudflare/worker/) che mappa quel path alla radice del progetto.

    python3.12 scripts/deploy_site.py            # PRODUZIONE (solo sezioni pubblicate)
    python3.12 scripts/deploy_site.py --drafts   # ANTEPRIMA (include le bozze)

Richiede in .env (o nell'ambiente):
    CLOUDFLARE_API_TOKEN   (Pages: Edit)
    CLOUDFLARE_ACCOUNT_ID
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = "pedemonte"


def load_env() -> dict:
    """Ambiente per wrangler: solo le variabili CLOUDFLARE_* da .env.

    Non passiamo gli altri segreti del progetto (HA_TOKEN, credenziali Deye, ...)
    a un CLI esterno: least-privilege.
    """
    env = os.environ.copy()
    envfile = ROOT / ".env"
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip().startswith("CLOUDFLARE_"):
                    env[k.strip()] = v.strip()
    return env


def main() -> int:
    ap = argparse.ArgumentParser(description="Build + deploy del sito Casa Pedemonte.")
    ap.add_argument("--drafts", action="store_true", help="include le bozze")
    args = ap.parse_args()

    env = load_env()
    for k in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"):
        if not env.get(k):
            sys.exit(f"Manca {k} in .env")

    # 1) build -> site/
    build = [sys.executable, str(ROOT / "scripts" / "build_site.py")]
    if args.drafts:
        build.append("--drafts")
    print("== build ==")
    subprocess.run(build, check=True, cwd=ROOT)

    # 2) deploy su Cloudflare Pages (radice del progetto)
    if args.drafts:
        print("ATTENZIONE: deploy con BOZZE incluse (anteprima privata).")
    print(f"\n== deploy Pages (progetto {PROJECT}) ==")
    subprocess.run(
        ["npx", "--yes", "wrangler@4", "pages", "deploy", str(ROOT / "site"),
         "--project-name", PROJECT, "--branch", "main", "--commit-dirty=true"],
        check=True, cwd=ROOT, env=env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
