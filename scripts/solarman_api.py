#!/usr/bin/env python3
"""
Solarman Cloud API Client per Deye SUN-12K-SG04LP3-EU

Recupera i dati dell'inverter Deye dal cloud Solarman e li stampa in JSON.
Può essere usato come command_line sensor in Home Assistant.

Prerequisiti:
  - Account SolarmanSmart (email/password)
  - API credentials (appid/appsecret) da richiedere a service@solarmanpv.com

Uso:
  python3 solarman_api.py                    # Dati real-time del device
  python3 solarman_api.py --discover         # Scopri stationId e deviceSn
  python3 solarman_api.py --station          # Dati della stazione/impianto
  python3 solarman_api.py --json-flat        # Output piatto per HA command_line

Credenziali da file .env o variabili d'ambiente:
  SOLARMAN_APPID, SOLARMAN_APPSECRET, SOLARMAN_EMAIL, SOLARMAN_PASSWORD
  SOLARMAN_DEVICE_SN (opzionale, default: 2504221369)

Autore: Pedemonte Energy Team
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests library not installed"}))
    sys.exit(1)

# --- Configurazione ---

API_BASE = "https://api.solarmanpv.com"
DEFAULT_DEVICE_SN = "2504221369"  # Inverter Deye SUN-12K-SG04LP3-EU

# Percorso .env relativo alla posizione dello script
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"


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
    """Legge la configurazione da environment variables."""
    load_env()
    config = {
        "appid": os.environ.get("SOLARMAN_APPID", ""),
        "appsecret": os.environ.get("SOLARMAN_APPSECRET", ""),
        "email": os.environ.get("SOLARMAN_EMAIL", ""),
        "password": os.environ.get("SOLARMAN_PASSWORD", ""),
        "device_sn": os.environ.get("SOLARMAN_DEVICE_SN", DEFAULT_DEVICE_SN),
        "station_id": os.environ.get("SOLARMAN_STATION_ID", ""),
    }
    return config


def sha256_hash(text):
    """SHA256 hash della password (richiesto da Solarman API)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SolarmanAPI:
    """Client per Solarman Cloud API v1.0."""

    def __init__(self, appid, appsecret, email, password):
        self.appid = appid
        self.appsecret = appsecret
        self.email = email
        self.password_hash = sha256_hash(password) if password else ""
        self.token = None
        self.token_expiry = 0
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _url(self, path):
        return "{}/{}?language=en".format(API_BASE, path.lstrip("/"))

    def authenticate(self):
        """Ottieni access token dall'API."""
        url = "{}/account/v1.0/token?appId={}&language=en".format(
            API_BASE, self.appid
        )
        payload = {
            "appSecret": self.appsecret,
            "email": self.email,
            "password": self.password_hash,
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success", False):
            raise Exception(
                "Auth failed: {} (code: {})".format(
                    data.get("msg", "unknown"), data.get("code", "?")
                )
            )

        self.token = data.get("access_token") or data.get("token")
        if not self.token:
            # Alcuni endpoint restituiscono i dati in modo diverso
            if "data" in data and isinstance(data["data"], dict):
                self.token = data["data"].get("access_token")

        if not self.token:
            raise Exception("No access_token in response: {}".format(json.dumps(data)))

        self.token_expiry = time.time() + 7000  # Token dura ~7200s
        self.session.headers["Authorization"] = "Bearer " + self.token
        return self.token

    def _ensure_auth(self):
        if not self.token or time.time() > self.token_expiry:
            self.authenticate()

    def get_station_list(self):
        """Lista delle stazioni/impianti."""
        self._ensure_auth()
        url = self._url("/station/v1.0/list")
        payload = {"page": 1, "size": 20}
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_station_realtime(self, station_id):
        """Dati real-time della stazione."""
        self._ensure_auth()
        url = self._url("/station/v1.0/realTime")
        payload = {"stationId": int(station_id)}
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_device_current_data(self, device_sn):
        """Dati correnti del dispositivo (inverter/logger)."""
        self._ensure_auth()
        url = self._url("/device/v1.0/currentData")
        payload = {"deviceSn": str(device_sn)}
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_device_list(self, station_id):
        """Lista dispositivi di una stazione."""
        self._ensure_auth()
        url = self._url("/station/v1.0/device")
        payload = {"stationId": int(station_id), "page": 1, "size": 20}
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()


def flatten_device_data(raw_response):
    """Converte la risposta API in un dict piatto per HA command_line sensor."""
    result = {}
    data = raw_response.get("data") or raw_response
    if not isinstance(data, dict):
        return {"error": "unexpected response format"}

    # Metadati device
    for key in ["deviceSn", "deviceId", "deviceType", "deviceState",
                "collectionTime", "updateTime"]:
        if key in data:
            result[key] = data[key]

    # Dati da dataList (array di {key, value, unit, name})
    data_list = data.get("dataList", [])
    for item in data_list:
        key = item.get("key", "")
        value = item.get("value", "")
        name = item.get("name", key)
        unit = item.get("unit", "")

        # Converti valore numerico se possibile
        try:
            if "." in str(value):
                value = float(value)
            else:
                value = int(value)
        except (ValueError, TypeError):
            pass

        # Usa key come nome del campo (più stabile di name)
        if key:
            result[key] = value
            if unit:
                result[key + "_unit"] = unit

    return result


def discover_devices(api):
    """Scopri stazioni e dispositivi associati."""
    print("Discovering stations...")
    stations = api.get_station_list()
    station_list = []

    if stations.get("success"):
        for s in stations.get("stationList", []):
            station_info = {
                "id": s.get("id"),
                "name": s.get("name"),
                "location": s.get("locationAddress", ""),
                "installedCapacity": s.get("installedCapacity", ""),
                "createDate": s.get("createDate", ""),
            }
            station_list.append(station_info)
            print("  Station: {} (id: {})".format(
                station_info["name"], station_info["id"]
            ))

            # Cerca dispositivi nella stazione
            try:
                devices = api.get_device_list(s["id"])
                if devices.get("success"):
                    for d in devices.get("deviceListItems", []):
                        print("    Device: {} (SN: {}, type: {})".format(
                            d.get("deviceType", "?"),
                            d.get("deviceSn", "?"),
                            d.get("deviceId", "?"),
                        ))
            except Exception as e:
                print("    Error listing devices: {}".format(e))

    return station_list


def main():
    config = get_config()

    # Validazione credenziali
    missing = []
    for key in ["appid", "appsecret", "email", "password"]:
        if not config[key]:
            missing.append("SOLARMAN_" + key.upper())

    if missing:
        msg = {
            "error": "Missing credentials",
            "missing_vars": missing,
            "hint": (
                "Aggiungi le seguenti variabili al file .env:\n"
                "  SOLARMAN_APPID=<appid da Solarman>\n"
                "  SOLARMAN_APPSECRET=<appsecret da Solarman>\n"
                "  SOLARMAN_EMAIL=<email account SolarmanSmart>\n"
                "  SOLARMAN_PASSWORD=<password account SolarmanSmart>\n"
                "  SOLARMAN_DEVICE_SN=2504221369  (opzionale)\n"
                "\n"
                "Per ottenere appid/appsecret, invia una mail a:\n"
                "  service@solarmanpv.com\n"
                "Richiedi: API access per app_id e app_secret"
            ),
        }
        print(json.dumps(msg, indent=2, ensure_ascii=False))
        sys.exit(1)

    api = SolarmanAPI(
        config["appid"], config["appsecret"],
        config["email"], config["password"]
    )

    # Parsing argomenti
    args = sys.argv[1:]
    flat_output = "--json-flat" in args

    try:
        if "--discover" in args:
            discover_devices(api)
            return

        if "--station" in args:
            if not config["station_id"]:
                # Scopri automaticamente
                stations = api.get_station_list()
                if stations.get("success") and stations.get("stationList"):
                    config["station_id"] = str(stations["stationList"][0]["id"])
                else:
                    print(json.dumps({"error": "No stations found"}))
                    sys.exit(1)

            data = api.get_station_realtime(config["station_id"])
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return

        # Default: device current data
        data = api.get_device_current_data(config["device_sn"])

        if flat_output:
            flat = flatten_device_data(data)
            print(json.dumps(flat, ensure_ascii=False))
        else:
            print(json.dumps(data, indent=2, ensure_ascii=False))

    except requests.exceptions.ConnectionError:
        print(json.dumps({"error": "Cannot connect to Solarman API"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
