#!/usr/bin/env python3
"""
Deye Cloud API Client per Deye SUN-12K-SG04LP3-EU

Recupera i dati dell'inverter Deye dal cloud ufficiale Deye e li stampa in JSON.
L'API Deye Cloud è self-service: puoi ottenere AppId e AppSecret direttamente
dal portale sviluppatori senza inviare email.

Setup:
  1. Registrati su https://www.deyecloud.com/login (o usa il tuo account esistente)
  2. Vai su https://developer.deyecloud.com/app e crea un'applicazione
  3. Copia AppId e AppSecret e aggiungili al file .env

Uso:
  python3 deye_cloud.py                  # Dati real-time del device
  python3 deye_cloud.py --discover       # Scopri stazioni e dispositivi
  python3 deye_cloud.py --station        # Dati della stazione
  python3 deye_cloud.py --json-flat      # Output piatto per HA command_line
  python3 deye_cloud.py --loop 300       # Loop ogni 300 secondi

Credenziali da file .env o variabili d'ambiente:
  DEYE_APPID          - AppId dal portale sviluppatori Deye
  DEYE_APPSECRET      - AppSecret dal portale sviluppatori Deye
  DEYE_EMAIL           - Email account Deye Cloud
  DEYE_PASSWORD        - Password account Deye Cloud
  DEYE_DEVICE_SN       - Serial number inverter (default: 2504221369)

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
    print(json.dumps({"error": "requests library not installed. Run: pip install requests"}))
    sys.exit(1)

# --- Configurazione ---

# Deye Cloud API endpoints per regione
API_REGIONS = {
    "eu": "https://eu1-developer.deyecloud.com/v1.0",
    "us": "https://us1-developer.deyecloud.com/v1.0",
}
DEFAULT_REGION = "eu"
DEFAULT_DEVICE_SN = "2504221369"  # Inverter Deye SUN-12K-SG04LP3-EU

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
    return {
        "appid": os.environ.get("DEYE_APPID", ""),
        "appsecret": os.environ.get("DEYE_APPSECRET", ""),
        "email": os.environ.get("DEYE_EMAIL", ""),
        "password": os.environ.get("DEYE_PASSWORD", ""),
        "device_sn": os.environ.get("DEYE_DEVICE_SN", DEFAULT_DEVICE_SN),
        "region": os.environ.get("DEYE_REGION", DEFAULT_REGION),
    }


def sha256_hash(text):
    """SHA256 hash della password (richiesto da Deye Cloud API)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class DeyeCloudAPI:
    """Client per Deye Cloud Open API v1.0.

    Documentazione: https://developer.deyecloud.com/api
    Sample code: https://github.com/DeyeCloudDevelopers/deye-openapi-client-sample-code
    """

    def __init__(self, appid, appsecret, email, password, region="eu"):
        self.appid = appid
        self.appsecret = appsecret
        self.email = email
        self.password_hash = sha256_hash(password) if password else ""
        self.base_url = API_REGIONS.get(region, API_REGIONS["eu"])
        self.token = None
        self.token_expiry = 0
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def authenticate(self):
        """Ottieni access token dall'API Deye Cloud."""
        url = "{}/account/token?appId={}".format(self.base_url, self.appid)
        payload = {
            "appSecret": self.appsecret,
            "email": self.email,
            "password": self.password_hash,
            "companyId": "0",
        }

        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success", True):
            code = data.get("code", "?")
            msg = data.get("msg", "unknown error")
            if code == 2101021:
                raise Exception("AppId non valido. Verifica DEYE_APPID nel .env")
            elif code == 2101019:
                raise Exception("AppSecret non valido. Verifica DEYE_APPSECRET nel .env")
            elif code == 2101025:
                raise Exception("Email o password non validi. Verifica DEYE_EMAIL e DEYE_PASSWORD")
            else:
                raise Exception("Auth failed: {} (code: {})".format(msg, code))

        # Estrai token dalla risposta (l'API usa camelCase: accessToken)
        self.token = (data.get("accessToken") or data.get("access_token")
                      or data.get("token"))
        if not self.token:
            # Il token potrebbe essere dentro data.data
            inner_data = data.get("data")
            if isinstance(inner_data, dict):
                self.token = (inner_data.get("accessToken")
                              or inner_data.get("access_token")
                              or inner_data.get("token"))

        if not self.token:
            raise Exception("Nessun token nella risposta: {}".format(json.dumps(data)))

        self.token_expiry = time.time() + 7000  # Token dura ~7200s (2 ore)
        self.session.headers["Authorization"] = "bearer " + self.token
        return self.token

    def _ensure_auth(self):
        """Garantisce che il token sia valido, rinnovandolo se necessario."""
        if not self.token or time.time() > self.token_expiry:
            self.authenticate()

    def _post(self, path, payload):
        """Esegue una POST autenticata."""
        self._ensure_auth()
        url = self.base_url + path
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # --- Account ---

    def get_account_info(self):
        """Informazioni sull'account."""
        return self._post("/account/info", {})

    # --- Stazioni ---

    def get_station_list(self, page=1, size=20):
        """Lista delle stazioni/impianti."""
        return self._post("/station/list", {"page": page, "size": size})

    def get_station_latest(self, station_ids):
        """Dati real-time delle stazioni (max 5)."""
        if isinstance(station_ids, (int, str)):
            station_ids = [str(station_ids)]
        return self._post("/station/latest", {"stationList": station_ids})

    def get_station_history(self, station_id, start_date, end_date):
        """Dati storici della stazione."""
        return self._post("/station/history", {
            "stationId": str(station_id),
            "startDate": start_date,
            "endDate": end_date,
        })

    def get_station_devices(self, station_id, page=1, size=20):
        """Lista dispositivi di una stazione."""
        return self._post("/station/device", {
            "stationId": str(station_id),
            "page": page,
            "size": size,
        })

    # --- Dispositivi ---

    def get_device_list(self, page=1, size=20):
        """Lista di tutti i dispositivi."""
        return self._post("/device/list", {"page": page, "size": size})

    def get_device_latest(self, device_sns):
        """Dati real-time dei dispositivi (max 10)."""
        if isinstance(device_sns, str):
            device_sns = [device_sns]
        return self._post("/device/latest", {"deviceList": device_sns})

    def get_device_history(self, device_sn, start_date, end_date):
        """Dati storici del dispositivo."""
        return self._post("/device/history", {
            "deviceSn": str(device_sn),
            "startDate": start_date,
            "endDate": end_date,
        })

    def get_device_measure_points(self, device_sn):
        """Punti di misura disponibili per il dispositivo."""
        return self._post("/device/measure/point", {
            "deviceSn": str(device_sn),
        })

    # --- Commissioning (controllo inverter) ---

    def get_control_result(self, device_sn, control_id):
        """Risultato di un comando di controllo."""
        return self._post("/commission/control/result", {
            "deviceSn": str(device_sn),
            "controlId": str(control_id),
        })


def flatten_device_data(raw_response):
    """Converte la risposta API in un dict piatto per HA.

    L'API Deye restituisce i dati in formato strutturato. Questa funzione
    li appiattisce in un dict semplice key:value per l'uso con
    command_line sensor di HA.
    """
    result = {"source": "deye_cloud", "timestamp": int(time.time())}

    data = (raw_response.get("deviceDataList")
            or raw_response.get("data")
            or raw_response)
    if isinstance(data, list) and len(data) > 0:
        data = data[0]

    if not isinstance(data, dict):
        result["error"] = "unexpected response format"
        return result

    # Metadati device
    for key in ["deviceSn", "deviceId", "deviceState", "deviceType",
                "collectionTime", "updateTime", "stationId"]:
        if key in data:
            result[key] = data[key]

    # Dati dal dataList (array di {key/name, value, unit})
    data_list = data.get("dataList", [])
    for item in data_list:
        key = item.get("key", item.get("name", ""))
        value = item.get("value", "")

        # Converti numeri
        try:
            if "." in str(value):
                value = float(value)
            else:
                value = int(value)
        except (ValueError, TypeError):
            pass

        if key:
            result[key] = value

    return result


def discover(api):
    """Scopri stazioni e dispositivi."""
    print("=" * 60)
    print("DEYE CLOUD - Discovery")
    print("=" * 60)

    # Account info
    try:
        account = api.get_account_info()
        print("\nAccount:")
        print(json.dumps(account, indent=2, ensure_ascii=False))
    except Exception as e:
        print("  Account info error: {}".format(e))

    # Stazioni
    print("\nStazioni:")
    stations = api.get_station_list()
    station_list = stations.get("stationList", stations.get("data", []))
    if isinstance(station_list, dict):
        station_list = station_list.get("stationList", [])

    if not station_list:
        print("  Nessuna stazione trovata.")
        print("  Risposta raw: {}".format(json.dumps(stations, indent=2, ensure_ascii=False)))
        return

    for s in station_list:
        sid = s.get("id", s.get("stationId", "?"))
        name = s.get("name", s.get("stationName", "?"))
        print("  - {} (id: {})".format(name, sid))

        # Dispositivi della stazione
        try:
            devices = api.get_station_devices(sid)
            dev_list = devices.get("deviceListItems", devices.get("data", []))
            if isinstance(dev_list, dict):
                dev_list = dev_list.get("deviceListItems", [])
            for d in dev_list:
                dsn = d.get("deviceSn", d.get("sn", "?"))
                dtype = d.get("deviceType", d.get("type", "?"))
                print("    Device: SN={}, type={}".format(dsn, dtype))
        except Exception as e:
            print("    Error listing devices: {}".format(e))

    # Dispositivi diretti
    print("\nTutti i dispositivi:")
    devices = api.get_device_list()
    dev_data = devices.get("deviceListItems", devices.get("data", []))
    if isinstance(dev_data, dict):
        dev_data = dev_data.get("deviceListItems", [])

    if dev_data:
        for d in dev_data:
            dsn = d.get("deviceSn", d.get("sn", "?"))
            dtype = d.get("deviceType", d.get("type", "?"))
            dname = d.get("deviceName", d.get("name", "?"))
            print("  - {} (SN: {}, type: {})".format(dname, dsn, dtype))
    else:
        print("  Nessun dispositivo trovato.")
        print("  Risposta raw: {}".format(json.dumps(devices, indent=2, ensure_ascii=False)))


def print_setup_instructions():
    """Stampa le istruzioni per configurare le credenziali."""
    instructions = """
╔══════════════════════════════════════════════════════════════╗
║              DEYE CLOUD API - Setup                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Registrati su https://www.deyecloud.com/login            ║
║     (o accedi con il tuo account esistente)                  ║
║                                                              ║
║  2. Vai su https://developer.deyecloud.com/app               ║
║     e crea una nuova applicazione                            ║
║                                                              ║
║  3. Copia AppId e AppSecret                                  ║
║                                                              ║
║  4. Aggiungi al file .env:                                   ║
║                                                              ║
║     DEYE_APPID=<il tuo AppId>                                ║
║     DEYE_APPSECRET=<il tuo AppSecret>                        ║
║     DEYE_EMAIL=<email account Deye Cloud>                    ║
║     DEYE_PASSWORD=<password account Deye Cloud>              ║
║     DEYE_DEVICE_SN=2504221369                                ║
║                                                              ║
║  5. Esegui: python3 deye_cloud.py --discover                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(instructions)


def main():
    config = get_config()

    # Validazione credenziali
    missing = []
    for key in ["appid", "appsecret", "email", "password"]:
        if not config[key]:
            missing.append("DEYE_" + key.upper())

    if missing:
        print_setup_instructions()
        result = {
            "error": "Missing credentials",
            "missing_vars": missing,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    api = DeyeCloudAPI(
        config["appid"], config["appsecret"],
        config["email"], config["password"],
        config["region"]
    )

    # Parsing argomenti
    args = sys.argv[1:]
    flat_output = "--json-flat" in args
    loop_interval = 0
    if "--loop" in args:
        idx = args.index("--loop")
        if idx + 1 < len(args):
            try:
                loop_interval = int(args[idx + 1])
            except ValueError:
                loop_interval = 300

    try:
        if "--discover" in args:
            discover(api)
            return

        if "--station" in args:
            stations = api.get_station_list()
            station_list = stations.get("stationList", stations.get("data", []))
            if isinstance(station_list, dict):
                station_list = station_list.get("stationList", [])

            if station_list:
                sid = station_list[0].get("id", station_list[0].get("stationId"))
                data = api.get_station_latest([str(sid)])
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(json.dumps({"error": "No stations found"}))
            return

        if "--measure-points" in args:
            data = api.get_device_measure_points(config["device_sn"])
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return

        # Default: device latest data
        while True:
            data = api.get_device_latest(config["device_sn"])

            if flat_output:
                flat = flatten_device_data(data)
                print(json.dumps(flat, ensure_ascii=False))
            else:
                print(json.dumps(data, indent=2, ensure_ascii=False))

            if loop_interval <= 0:
                break

            sys.stdout.flush()
            time.sleep(loop_interval)

    except requests.exceptions.ConnectionError:
        print(json.dumps({"error": "Cannot connect to Deye Cloud API"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
