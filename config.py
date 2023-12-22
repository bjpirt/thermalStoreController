from lib import PersistentConfig
try:
    from initial_config import config   # type: ignore
except ImportError:
    config = {}


class Config(PersistentConfig):
    def __init__(self):
        # Initialise the defaults
        self.wifi_network = "WIFI_NETWORK"
        self.wifi_password = 'WIFI_PASSWORD'
        self.mqtt_address = "192.168.1.1"
        self.mqtt_publish_interval = 1.0
        self.mqtt_full_publish_interval = 60.0
        self.mqtt_topic_prefix = ""
        self.battery_immersion_on_soc = 81
        self.battery_immersion_off_soc = 80
        self.battery_immersion_min_soc = 50
        self.tank_temperature_setpoint = 50
        self.tank_temperature_cutoff = 80
        self.outside_temperature_low_setpoint = 12
        self.occupied_ac_power = 300
        self.occupied_time = 86400
        super().__init__(config)
