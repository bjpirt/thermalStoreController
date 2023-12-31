from .hardware_gateway import HardwareGateway
from .temperature_sensor import TemperatureSensor
try:
    from machine import Pin  # type: ignore
except ImportError:
    pass


class HardwareGatewayImpl(HardwareGateway):
    def __init__(self) -> None:
        test_sensor = TemperatureSensor(16)
        self._tank_sensors = [test_sensor,
                              test_sensor,
                              test_sensor,
                              test_sensor]
        self._outside_sensor = test_sensor
        self._immersion_state = False
        self._immersion_pin = Pin(15, mode=Pin.OUT)
        self._boiler_state = False
        self._boiler_pin = Pin(16, mode=Pin.OUT)

    def read_sensors(self):
        for sensor in self._tank_sensors:
            sensor.read()
        self._outside_sensor.read()

    @property
    def immersion(self):
        return self._immersion_state

    @immersion.setter
    def immersion(self, state: bool) -> None:
        self._immersion_state = state
        self._immersion_pin.value(state)

    @property
    def boiler(self):
        return self._boiler_state

    @boiler.setter
    def boiler(self, state: bool) -> None:
        self._boiler_state = state
        # The boiler control is inverted for fail-safe control by the thermostat
        self._boiler_pin.value(not state)

    @property
    def sensor_error(self):
        return any([sensor.error for sensor in self._tank_sensors]) or self._outside_sensor.error

    @property
    def outside_sensor(self):
        return self._outside_sensor.value

    @property
    def outside_sensor_error(self):
        return self._outside_sensor.error

    @property
    def tank_sensors(self):
        return [sensor.value for sensor in self._tank_sensors]

    @property
    def tank_sensor_errors(self):
        return [sensor.error for sensor in self._tank_sensors]
