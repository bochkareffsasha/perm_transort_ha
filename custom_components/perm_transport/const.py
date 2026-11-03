"""Константы интеграции Perm Transport."""
from __future__ import annotations

DOMAIN = "perm_transport"
PLATFORMS = ["sensor"]

API_URL = "https://www.map.gortransperm.ru/json/arrival-times-vehicles/{stop_id}"

CONF_STOP_ID = "stop_id"
CONF_STOP_NAME = "stop_name"
CONF_ROUTES = "routes"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 60   # секунд
MIN_SCAN_INTERVAL = 15       # чтобы не получить бан от API
MAX_SCAN_INTERVAL = 3600
REQUEST_TIMEOUT = 15         # секунд

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:159.0) Gecko/20100101 Firefox/159.0",
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.map.gortransperm.ru/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}