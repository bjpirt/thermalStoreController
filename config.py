import os
import json
from initial_config import config


def exists(filename: str) -> bool:
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


class Config:
    def __init__(self, file="config.json"):
        self.__file = file
        # Initialise the defaults
        self.wifi_network = "WIFI_NETWORK"
        self.wifi_password = 'WIFI_PASSWORD'
        self.mqtt_address = "192.168.1.1"
        self.battery_immersion_on_soc = 81
        self.battery_immersion_off_soc = 80
        self.battery_immersion_min_soc = 50
        self.tank_temperature_setpoint = 50
        self.tank_temperature_cutoff = 80
        self.outside_temperature_low_setpoint = 12
        self.occupied_ac_power = 300
        self.occupied_time = 86400

        self.update(config)

        self.read()

    def get_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def read(self):
        data = None
        if exists(self.__file):
            with open(self.__file, 'r', encoding="UTF-8") as file:
                data = file.read()
                if data:
                    new_config = json.loads(data)
                    self.update(new_config)

    def set_value(self, key: str, value):
        if hasattr(self, key):
            if type(getattr(self, key)) == type(value) or type(value) == type(None):
                setattr(self, key, value)
            else:
                print(f"Config types did not match: {key} ({type(getattr(self, key))}) ({type(value)})")
        else:
            print("Attribute does not exist")

    def update(self, new_config: dict) -> None:
        for (key, value) in new_config.items():
            self.set_value(key, value)

    def save(self):
        with open(self.__file, 'w', encoding="utf-8") as file:
            json.dump(self.get_dict(), file)
