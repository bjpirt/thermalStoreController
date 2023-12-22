from hardware import HardwareGateway
from mqtt import MqttGateway
from .occupancy import Occupancy


class ThermalStoreController:
    def __init__(self, config, mqtt: MqttGateway, hardware: HardwareGateway, occupancy: Occupancy):
        self._config = config
        self._mqtt = mqtt
        self._hardware = hardware
        self._occupancy = occupancy

    def calculate_relay_state(self):
        # If there's an error at all, default to the external thermostat control
        if self.error:
            return {"immersion": False, "boiler": True}

        # If the temperature is too high, turn everything off
        min_temp = min(self._hardware.tank_sensors)
        if min_temp >= self._config.tank_temperature_cutoff:
            return {"immersion": False, "boiler": False}

        # If the battery is above the threshold, turn on the immersion
        if self._mqtt.battery_soc >= self._config.battery_immersion_on_soc:
            return {"immersion": True, "boiler": False}

        if self._occupancy.occupied or self.heating_required:
            # Keep the tank at the minimum temperature level
            if self._hardware.tank_sensors[2] < self._config.tank_temperature_setpoint:
                if self._mqtt.battery_soc >= self._config.battery_immersion_min_soc:
                    # If we have battery capacity, use that first
                    return {"immersion": True, "boiler": False}
                # Fall back to the boiler thermostat
                return {"immersion": False, "boiler": True}

        # Fall back to no heating if not required
        state = {"boiler": False}
        if self._mqtt.battery_soc <= self._config.battery_immersion_off_soc:
            state["immersion"] = False
        return state

    def update(self):
        self._hardware.read_sensors()
        self._occupancy.update()
        relay_state = self.calculate_relay_state()
        self._hardware.boiler = relay_state["boiler"]
        if "immersion" in relay_state:
            self._hardware.immersion = relay_state["immersion"]

    @property
    def status(self):
        output = {"error": int(self.error),
                  "error/soc": int(self._mqtt.battery_soc_error),
                  "error/sensor": int(self._hardware.sensor_error),
                  "error/occupancy": int(self.occupancy_error)}

        tank_sensor_errors = self._hardware.tank_sensor_errors
        for (index, sensor) in enumerate(self._hardware.tank_sensors):
            if not tank_sensor_errors[index]:
                output[f"temperature/tank/{index}"] = sensor

        if not self._hardware.outside_sensor_error:
            output["temperature/outside"] = self._hardware.outside_sensor

        output["immersion"] = int(self._hardware.immersion)
        output["boiler"] = int(self._hardware.boiler)
        output["occupied"] = int(self._occupancy.occupied)
        return output

    @property
    def occupancy_error(self):
        return self._mqtt.ac_power_error

    @property
    def error(self):
        return self._hardware.sensor_error or self._mqtt.battery_soc_error

    @property
    def heating_required(self):
        return self._hardware.outside_sensor <= self._config.outside_temperature_low_setpoint
