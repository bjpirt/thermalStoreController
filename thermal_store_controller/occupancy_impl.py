from mqtt import MqttGateway
from lib import Timeout
from .occupancy import Occupancy


class OccupancyImpl(Occupancy):
    def __init__(self, mqtt: MqttGateway, config) -> None:
        self._mqtt = mqtt
        self._config = config
        self._timer = Timeout()
        self._timer.set(self._config.occupied_time)
        super().__init__()

    def update(self):
        if self._mqtt.ac_power and self._mqtt.ac_power > self._config.occupied_ac_power:
            self._timer.reset()
        self.occupied = not self._timer.ready
