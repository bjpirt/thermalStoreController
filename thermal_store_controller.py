from mqtt_connection import MQTTConnection
from temperature_sensor import TemperatureSensor
from machine import Pin  # type: ignore
from timeout import Timeout


class ThermalStoreController:
    def __init__(self, config, mqtt: MQTTConnection):
        self._config = config
        self._mqtt = mqtt
        test_sensor = TemperatureSensor(18)
        self._tank_sensors = [test_sensor,
                              test_sensor,
                              test_sensor,
                              test_sensor]
        self._outside_sensor = test_sensor
        self._immersion_state = False
        self._immersion = Pin(17, mode=Pin.OUT)
        self._boiler_state = False
        self._boiler = Pin(16, mode=Pin.OUT)
        self._occupancy_timer = Timeout()
        self._occupancy_timer.set(self._config["occupied_time"])
        self.occupied = False

    def read_sensors(self):
        for sensor in self._tank_sensors:
            sensor.read()
        self._outside_sensor.read()

    def update_occupancy(self):
        if self._mqtt.ac_level and self._mqtt.ac_level > self._config["occupied_ac_level"]:
            self._occupancy_timer.reset()
        self.occupied = not self._occupancy_timer.ready

    def update(self):
        self.read_sensors()
        self.update_occupancy()

        # If there's an error at all, default to the external thermostat control
        if self.error:
            self.immersion(False)
            self.boiler(True)
            return

        # If the temperature is too high, turn everything off
        min_temp = min([sensor.value for sensor in self._tank_sensors])
        if min_temp >= self._config["temperature_cutoff"]:
            self.immersion(False)
            self.boiler(False)
            return

        # If the battery is above the threshold, turn on the immersion
        if self._mqtt.battery_soc >= self._config["battery_immersion_on_level"]:
            self.immersion(True)
            self.boiler(False)
            return

        if self.occupied or self.heating_required:
            # Keep the tank at the minimum temperature level
            if self._tank_sensors[2].value < self._config["temperature_min"]:
                if self._mqtt.battery_soc >= self._config["battery_immersion_min_level"]:
                    # If we have battery capacity, use that first
                    self.immersion(True)
                    self.boiler(False)
                else:
                    # Fall back to the boiler thermostat
                    self.immersion(False)
                    self.boiler(True)
            else:
                if self._mqtt.battery_soc <= self._config["battery_immersion_off_level"]:
                    # Turn off the immersion if the battery is at or under the off level
                    self.immersion(False)
                self.boiler(False)
        else:
            # Fall back to the boiler thermostat
            if self._mqtt.battery_soc <= self._config["battery_immersion_off_level"]:
                self.immersion(False)
            self.boiler(True)

    @property
    def status(self):
        output = {"error": 1 if self.error else 0,
                  "soc_error": 1 if self._mqtt.battery_soc_error else 0,
                  "sensor_error": 1 if self.sensor_error else 0,
                  "occupancy_error": 1 if self.occupancy_error else 0}

        for (index, sensor) in enumerate(self._tank_sensors):
            if not sensor.error:
                output[f"tank_temp{index+1}"] = sensor.value

        if not self._outside_sensor.error:
            output["outside_temp"] = self._outside_sensor.value

        output["immersion"] = 1 if self._immersion_state else 0
        output["boiler"] = 1 if self._boiler_state else 0
        output["occupied"] = 1 if self.occupied else 0
        return output

    def immersion(self, state: bool) -> None:
        self._immersion_state = state
        self._immersion.value(state)

    def boiler(self, state: bool) -> None:
        self._boiler_state = state
        # The boiler control is inverted for fail-safe control by the thermostat
        self._boiler.value(not state)

    @property
    def sensor_error(self):
        return any([sensor.error for sensor in self._tank_sensors]) or self._outside_sensor.error

    @property
    def occupancy_error(self):
        return self._mqtt.ac_level_error

    @property
    def error(self):
        return self.sensor_error or self._mqtt.battery_soc_error

    @property
    def heating_required(self):
        return self._outside_sensor.value <= self._config["outside_temperature_low_setpoint"]
