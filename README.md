# ProscenicQ8Tuya

A reverse-engineered controller for the **Proscenic Q8** robot vacuum, built on top of the [Tuya OpenAPI](https://developer.tuya.com/en/docs/cloud). It exposes both a CLI and an HTTP API to send the robot to clean specific map areas (rooms).

## Custom Q8 Mop Mode

This fork includes a custom Mop mode for the Proscenic Q8.

### Kitchen + Hallway Mop

The custom Mop command:

- Enables low water level
- Switches the Q8 into Mop mode
- Selects the Kitchen and Hallway partition
- Starts cleaning
- Skips the Lounge and Bathroom
- Returns the Q8 to the charging dock after approximately 23 minutes

This sequence was reverse-engineered and tested using the Smart Life app with the Q8.

The original room-cleaning controls remain available alongside the custom Mop function.


## How it works

The Proscenic Q8 accepts a `command_trans` data point whose value is a base64-encoded binary packet. By reverse-engineering the packets captured from the official SmartLife app, the packet format for single-room cleaning was identified:

```
AA 00 04 14 01 01 [room_id] [checksum]
checksum = (0x14 + 0x01 + 0x01 + room_id) & 0xFF
```

Room IDs are small integers (typically 1–N) assigned by the robot when it segments its map. They are **not exposed by any official Tuya API** — the only way to discover them is trial and error: send `clean 1`, `clean 2`, … and observe which area the robot moves to. The `ROOM_NAMES` dict in `robot_service.py` contains the mapping for my home as a concrete example.

## Running the application

### CLI mode (default)

```bash
python main.py
```

An interactive shell opens. Available commands:

| Command | Description |
|---|---|
| `clean <id\|name>` | Send the robot to clean a room (e.g. `clean 1` or `clean bathroom`) |
| `stop` | Return the robot to its charging base |
| `help` | Show available commands |
| `exit` | Quit |

### API mode

```bash
python main.py --mode api
```

Starts a FastAPI server on port `8111`. Endpoints:

| Method | Path | Description |
|---|---|---|
| `GET` | `/robot/clean/{room}` | Clean a room by numeric ID or name alias |
| `GET` | `/robot/stop` | Return to base |

Examples:

```bash
curl http://localhost:8111/robot/clean/1
curl http://localhost:8111/robot/clean/bathroom
curl http://localhost:8111/robot/stop
```

## Configuration

Copy `config.ini.example` to `config.ini` and fill in your values:

```bash
cp config.ini.example config.ini
```

```ini
[tuya]
access_id     = ...   # Tuya Cloud project Access ID
access_secret = ...   # Tuya Cloud project Access Secret
username      = ...   # SmartLife / Tuya app account email
password      = ...   # SmartLife / Tuya app account password
device_id     = ...   # Device ID of the robot

# Optional
endpoint      = https://openapi.tuyaeu.com   # EU endpoint (default)
country_code  = 39                           # Italy (default)
schema        = smartlife
```

Alternatively, every value can be set as an environment variable (takes precedence over `config.ini`):

| Variable | Description |
|---|---|
| `TUYA_ACCESS_ID` | Tuya Cloud Access ID |
| `TUYA_ACCESS_SECRET` | Tuya Cloud Access Secret |
| `TUYA_USERNAME` | App account email |
| `TUYA_PASSWORD` | App account password |
| `TUYA_DEVICE_ID` | Robot device ID |
| `TUYA_ENDPOINT` | API endpoint (optional) |
| `TUYA_COUNTRY_CODE` | Country phone prefix (optional) |
| `TUYA_SCHEMA` | App schema, `smartlife` or `tuyasmart` (optional) |

### How to obtain the credentials

| Credential | Where to find it |
|---|---|
| `access_id` / `access_secret` | [Tuya IoT Platform](https://iot.tuya.com) → Cloud → your project → Overview |
| `username` / `password` | The email and password you use to log in to the SmartLife app |
| `device_id` | Tuya IoT Platform → Cloud → your project → Devices, or SmartLife app → device → Device Info |
| `endpoint` | Choose the regional endpoint that matches your Tuya account region (EU: `openapi.tuyaeu.com`, US: `openapi.tuyaus.com`, CN: `openapi.tuyacn.com`) |

## Installation

```bash
pip install -r requirements.txt
```

## Notes

- `config.ini` and `.env` are excluded from version control via `.gitignore` — never commit them.
- Room IDs depend on the map saved on the robot. If the robot re-maps the house, IDs may change.
- The `ROOM_NAMES` dict in `robot_service.py` is optional metadata; only the numeric ID matters at the protocol level.
