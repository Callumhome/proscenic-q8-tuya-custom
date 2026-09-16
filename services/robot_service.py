import base64

from tuya_iot import TuyaOpenAPI, TUYA_LOGGER

import config


def make_room_payload(room_id: int) -> str:
    """
    Generate the base64 command_trans payload for a given numeric room ID.

    Proscenic Q8 packet format (reverse-engineered):
    AA 00 04 14 01 01 [room_id] [checksum]
    """
    checksum = (0x14 + 0x01 + 0x01 + room_id) & 0xFF
    prefix = bytes((0xAA, 0x00, 0x04, 0x14, 0x01, 0x01))
    return base64.b64encode(
        prefix + bytes((room_id, checksum))
    ).decode()


class RobotService:
    ROOM_NAMES = {
        1: "living_room_north",
        2: "bedroom",
        3: "living_room_center",
        4: "kitchen",
        5: "hallway",
        6: "bathroom",
        7: "living_room_south",
    }

    def __init__(self):
        TUYA_LOGGER.setLevel("DEBUG")

        self.openapi = TuyaOpenAPI(
            config.ENDPOINT,
            config.ACCESS_ID,
            config.ACCESS_SECRET,
        )

        self.openapi.connect(
            config.USERNAME,
            config.PASSWORD,
            config.COUNTRY_CODE,
            config.SCHEMA,
        )

    def clean_room(self, room: int | str):
        """
        Clean a room by numeric ID or name.
        """

        try:
            room_id = int(room)
        except (ValueError, TypeError):
            name_to_id = {
                v: k for k, v in self.ROOM_NAMES.items()
            }

            if room not in name_to_id:
                return {
                    "success": False,
                    "error": f"Unknown room '{room}'. Use one of: {', '.join(name_to_id)}",
                }

            room_id = name_to_id[room]

        payload = make_room_payload(room_id)

        cmd = {
            "commands": [
                {
                    "code": "command_trans",
                    "value": payload,
                }
            ]
        }

        return self.openapi.post(
            f"/v1.0/iot-03/devices/{config.DEVICE_ID}/commands",
            cmd,
        )

    def mop(self):
        """
        Mop Kitchen + Hallway only.
        Confirmed smart Life sequence: Kitchen (room5) + Hallway (room3) -> return to dock after 23 minutes.
        """
        import time

        commands_url = f"/v1.0/iot-03/devices/{config.DEVICE_ID}/commands"
        water = self.openapi.post(commands_url, {"commands": [{"code": "cistern", "value": "low"}]})
        mop_mode = self.openapi.post(commands_url, {"commands": [{"code": "command_trans", "value": "qgABFxc="}]})
        partition = self.openapi.post(commands_url, {"commands": [{"code": "command_trans", "value": "qgAUGwEABPtzArL+OQKy/jn8z/tz/M9o"}]})
        mode = self.openapi.post(commands_url, {"commands": [{"code": "mode", "value": "select_room"}]})
        start = self.openapi.post(commands_url, {"commands": [{"code": "power_go", "value": True}]})
        time.sleep(23 * 60)
        return_home = self.openapi.post(commands_url, {"commands": [{"code": "switch_charge", "value": True}]})
        return {"water": water, "mop_mode": mop_mode, "partition": partition, "mode": mode, "start": start, "return_home": return_home}


    def return_to_base(self):
        cmd = {
            "commands": [
                {
                    "code": "switch_charge",
                    "value": True,
                }
            ]
        }

        return self.openapi.post(
            f"/v1.0/iot-03/devices/{config.DEVICE_ID}/commands",
            cmd,
        )


robot_service = RobotService()
