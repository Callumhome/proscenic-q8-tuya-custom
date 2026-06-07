import os
import configparser
from pathlib import Path

# 1. Load .env if present (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 2. Load config.ini from the same directory as this script
_config_file = Path(__file__).parent / "config.ini"
_ini = configparser.ConfigParser()
_ini.read(_config_file)


def _get(env_key: str, ini_key: str, section: str = "tuya", default: str = None) -> str:
    """Returns the env var if set, otherwise the config.ini value, otherwise the default."""
    return os.getenv(env_key) or _ini.get(section, ini_key, fallback=default)


ENDPOINT     = _get("TUYA_ENDPOINT",      "endpoint",      default="https://openapi.tuyaeu.com")
DEVICE_ID    = _get("TUYA_DEVICE_ID",     "device_id")
ACCESS_ID    = _get("TUYA_ACCESS_ID",     "access_id")
ACCESS_SECRET = _get("TUYA_ACCESS_SECRET", "access_secret")
USERNAME     = _get("TUYA_USERNAME",      "username")
PASSWORD     = _get("TUYA_PASSWORD",      "password")
COUNTRY_CODE = _get("TUYA_COUNTRY_CODE",  "country_code",  default="39")
SCHEMA       = _get("TUYA_SCHEMA",        "schema",        default="smartlife")

_missing = [
    label for label, val in [
        ("TUYA_ACCESS_ID / [tuya] access_id",       ACCESS_ID),
        ("TUYA_ACCESS_SECRET / [tuya] access_secret", ACCESS_SECRET),
        ("TUYA_USERNAME / [tuya] username",          USERNAME),
        ("TUYA_PASSWORD / [tuya] password",          PASSWORD),
        ("TUYA_DEVICE_ID / [tuya] device_id",        DEVICE_ID),
    ]
    if not val
]

if _missing:
    raise ValueError(
        "Missing configuration. Set the following via environment variables or config.ini:\n  "
        + "\n  ".join(_missing)
    )
