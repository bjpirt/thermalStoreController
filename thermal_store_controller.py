from mqtt_connection import MQTTConnection
from temperature_sensor import TemperatureSensor
from machine import Pin  # type: ignore


class ThermalStoreController:
    def __init__(self, config, mqtt: MQTTConnection):
        self._config = config
        self._mqtt = mqtt
        test_sensor = TemperatureSensor(18)
        self._sensors = [test_sensor,
                         test_sensor,
                         test_sensor,
                         test_sensor]
        self._immersion_value = False
        self._immersion = Pin(17, mode=Pin.OUT)
        self._boiler_value = False
        self._boiler = Pin(16, mode=Pin.OUT)

    def read_sensors(self):
        for sensor in self._sensors:
            sensor.read()

    def update(self):
        self.read_sensors()

        if self.error:
            self.immersion(False)
            self.boiler(True)
            return

        min_temp = min([sensor.value for sensor in self._sensors])
        if min_temp < self._config["temperature_cutoff"]:
            if self._mqtt.battery_soc >= self._config["battery_immersion_on_level"]:
                self.immersion(True)
            elif self._mqtt.battery_soc <= self._config["battery_immersion_off_level"]:
                self.immersion(False)
        else:
            self.immersion(False)
            self.boiler(False)

    @property
    def status(self):
        output = {"error": 1 if self.error else 0,
                  "soc_error": 1 if self._mqtt.battery_soc_error else 0,
                  "sensor_error": 1 if self.sensor_error else 0}

        for (index, sensor) in enumerate(self._sensors):
            if not sensor.error:
                output[f"temp{index+1}"] = sensor.value
        output["immersion"] = 1 if self._immersion_value else 0
        output["boiler"] = 1 if self._boiler_value else 0
        return output

    def immersion(self, state: bool) -> None:
        self._immersion_value = state
        self._immersion.value(state)

    def boiler(self, state: bool) -> None:
        self._boiler_value = state
        # The boiler control is inverted for fail-safe control by the thermostat
        self._boiler.value(not state)

    @property
    def sensor_error(self):
        return any([sensor.error for sensor in self._sensors])

    @property
    def error(self):
        return self.sensor_error or self._mqtt.battery_soc_error
