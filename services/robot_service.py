from tuya_iot import TuyaOpenAPI, TUYA_LOGGER
import config

class RobotService:
    ROOM_PAYLOAD = {
        "bathroom": "qgAEFAEBBhw=",
        "bedroom": "qgAEFAEBAhg=",
        "kitchen": "qgAEFAEBBBo=",
        "hallway": "qgAEFAEBBRs=",
        "living_room_center": "qgAEFAEBAxk=",
        "living_room_north": "qgAEFAEBARc=",
        "living_room_south": "qgAEFAEBBx0=",
    }

    def __init__(self):
        TUYA_LOGGER.setLevel("DEBUG")
        self.openapi = TuyaOpenAPI(config.ENDPOINT, config.ACCESS_ID, config.ACCESS_SECRET)
        self.openapi.connect(config.USERNAME, config.PASSWORD, config.COUNTRY_CODE, config.SCHEMA)

    def clean_room(self, room_key: str):
        if room_key not in self.ROOM_PAYLOAD:
            return {"success": False, "error": "Room not found"}
            
        payload = self.ROOM_PAYLOAD[room_key]
        cmd = {"commands": [{"code": "command_trans", "value": payload}]}
        return self.openapi.post(f"/v1.0/iot-03/devices/{config.DEVICE_ID}/commands", cmd)

    def return_to_base(self):
        cmd = {"commands": [{"code": "switch_charge", "value": True}]}
        return self.openapi.post(f"/v1.0/iot-03/devices/{config.DEVICE_ID}/commands", cmd)

robot_service = RobotService()
