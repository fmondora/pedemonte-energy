#!/usr/bin/env python3
"""
Deye Stick Logger Local Scraper

Scraping dei dati dallo stick logger LSW-3 via interfaccia web locale.
Estrae le variabili JavaScript da status.html e le restituisce in JSON.

Questo scraper funziona SENZA credenziali cloud — accede direttamente
allo stick logger sulla rete locale.

Uso:
  python3 deye_local_scraper.py              # Dati base da status.html
  python3 deye_local_scraper.py --verbose    # Tutti i dati raw
  python3 deye_local_scraper.py --monitor    # Loop continuo ogni 60s

Configurazione (da .env o variabili d'ambiente):
  DEYE_LOGGER_IP=192.168.86.69  (default)
  DEYE_LOGGER_USER=admin         (default)
  DEYE_LOGGER_PASS=admin         (default)

Autore: Pedemonte Energy Team
"""

import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print(json.dumps({"error": "requests library not installed"}))
    sys.exit(1)

# --- Configurazione ---

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

DEFAULT_IP = "192.168.86.69"
DEFAULT_USER = "admin"
DEFAULT_PASS = "admin"


def load_env():
    """Carica variabili da .env se esiste."""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = value


def get_config():
    load_env()
    return {
        "ip": os.environ.get("DEYE_LOGGER_IP", DEFAULT_IP),
        "user": os.environ.get("DEYE_LOGGER_USER", DEFAULT_USER),
        "password": os.environ.get("DEYE_LOGGER_PASS", DEFAULT_PASS),
    }


def parse_js_variables(html):
    """Estrai variabili JavaScript dal contenuto HTML dello status.html.

    Le variabili sono nel formato:
      var webdata_sn = "2504221369";
      var webdata_now_p = "61109";
    """
    variables = {}

    # Pattern per variabili JavaScript: var nome = "valore";
    pattern = re.compile(r'var\s+(\w+)\s*=\s*"([^"]*)"')
    for match in pattern.finditer(html):
        key = match.group(1)
        value = match.group(2)
        variables[key] = value

    return variables


def interpret_raw_data(raw_vars):
    """Interpreta i valori raw dello stick logger in dati significativi.

    Lo stick logger espone dati grezzi che richiedono interpretazione:
    - webdata_now_p: Potenza attuale (può essere valore signed 16-bit o raw Modbus)
    - webdata_today_e: Energia prodotta oggi (kWh)
    - webdata_total_e: Energia totale prodotta (kWh)
    - status_a/b/c: Stato connessione ai server
    """
    result = {
        "timestamp": int(time.time()),
        "source": "local_stick_logger",
    }

    # Dati identificativi
    if "webdata_sn" in raw_vars:
        result["inverter_sn"] = raw_vars["webdata_sn"]
    if "cover_mid" in raw_vars:
        result["logger_sn"] = raw_vars["cover_mid"]
    if "cover_ver" in raw_vars:
        result["firmware"] = raw_vars["cover_ver"]

    # Potenza attuale
    if "webdata_now_p" in raw_vars:
        try:
            raw_p = int(raw_vars["webdata_now_p"])
            # Se il valore è > 32767, potrebbe essere un valore signed 16-bit
            if raw_p > 32767:
                signed_p = raw_p - 65536
                result["power_raw"] = raw_p
                result["power_w"] = signed_p
                result["power_kw"] = round(signed_p / 1000.0, 3)
            else:
                result["power_raw"] = raw_p
                result["power_w"] = raw_p
                result["power_kw"] = round(raw_p / 1000.0, 3)
        except ValueError:
            result["power_raw"] = raw_vars["webdata_now_p"]

    # Energia oggi e totale
    for field, key in [("energy_today_kwh", "webdata_today_e"),
                       ("energy_total_kwh", "webdata_total_e")]:
        if key in raw_vars:
            try:
                result[field] = float(raw_vars[key])
            except ValueError:
                result[field] = raw_vars[key]

    # Stato connessioni server
    for s in ["a", "b", "c"]:
        key = "status_" + s
        if key in raw_vars:
            result["server_" + s + "_connected"] = raw_vars[key] == "1"

    # Upload counter
    if "webdata_utime" in raw_vars:
        try:
            result["upload_count"] = int(raw_vars["webdata_utime"])
        except ValueError:
            result["upload_count"] = raw_vars["webdata_utime"]

    # WiFi signal
    if "cover_sta_rssi" in raw_vars:
        result["wifi_rssi_percent"] = raw_vars["cover_sta_rssi"]

    return result


def scrape_status(ip, user, password):
    """Scrape della pagina status.html dello stick logger."""
    url = "http://{}/status.html".format(ip)
    auth = HTTPBasicAuth(user, password)

    resp = requests.get(url, auth=auth, timeout=10)
    resp.raise_for_status()

    raw_vars = parse_js_variables(resp.text)
    return raw_vars


def scrape_hidden_config(ip, user, password):
    """Scrape della configurazione nascosta (hide_set_edit.html)."""
    url = "http://{}/hide_set_edit.html".format(ip)
    auth = HTTPBasicAuth(user, password)

    resp = requests.get(url, auth=auth, timeout=10)
    resp.raise_for_status()

    # Estrai configurazione server
    config = {}
    for match in re.finditer(r'var\s+(\w+)\s*=\s*"([^"]*)"', resp.text):
        config[match.group(1)] = match.group(2)

    return config


def main():
    config = get_config()
    args = sys.argv[1:]
    verbose = "--verbose" in args
    monitor = "--monitor" in args

    try:
        while True:
            raw_vars = scrape_status(config["ip"], config["user"], config["password"])

            if verbose:
                # Tutti i dati raw
                output = {
                    "raw": raw_vars,
                    "interpreted": interpret_raw_data(raw_vars),
                }
            else:
                output = interpret_raw_data(raw_vars)

            print(json.dumps(output, indent=2, ensure_ascii=False))

            if not monitor:
                break

            sys.stdout.flush()
            time.sleep(60)

    except requests.exceptions.ConnectionError:
        print(json.dumps({
            "error": "Cannot connect to stick logger",
            "ip": config["ip"],
            "hint": "Verifica che lo stick logger sia raggiungibile sulla rete locale"
        }))
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(json.dumps({"error": "Connection timeout", "ip": config["ip"]}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
