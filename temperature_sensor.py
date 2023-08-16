from timeout import Timeout
from machine import Pin  # type: ignore
import onewire  # type: ignore
from ds18x20 import DS18X20  # type: ignore


class TemperatureSensor:
    def __init__(self, pin: int) -> None:
        ow = onewire.OneWire(Pin(pin))
        self._sensor = DS18X20(ow)
        self._value = None
        self.setup()
        self._timeout = Timeout()
        self._timeout.set(60)

    def setup(self) -> None:
        self._roms = self._sensor.scan()

    def read(self) -> float:
        if len(self._roms) > 0:
            try:
                self._sensor.convert_temp()
                self._value = self._sensor.read_temp(self._roms[0])
                self._timeout.reset()
            except onewire.OneWireError:
                pass
        else:
            self.setup()

    @property
    def value(self):
        return self._value

    @property
    def error(self) -> bool:
        return self._timeout.ready
