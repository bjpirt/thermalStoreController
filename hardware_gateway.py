class HardwareGateway:
    def read_sensors(self):
        pass

    @property
    def immersion(self):
        pass

    @immersion.setter
    def immersion(self, state: bool) -> None:
        pass

    @property
    def boiler(self):
        pass

    def boiler(self, state: bool) -> None:
        pass

    @property
    def sensor_error(self):
        pass

    @property
    def outside_sensor(self):
        pass

    @property
    def outside_sensor_error(self):
        pass

    @property
    def tank_sensors(self):
        pass

    @property
    def tank_sensor_errors(self):
        pass
