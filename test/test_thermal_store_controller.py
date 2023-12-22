import unittest
from thermal_store_controller import ThermalStoreController
from config import Config


class FakeHardwareGateway:
    def __init__(self) -> None:
        self.value = 25.0
        self.error = False
        self.immersion = False
        self.boiler = False
        self.sensor_error = False
        self.outside_sensor = 18.3
        self.outside_sensor_error = False
        self.tank_sensors = [23.0, 36.2, 55.9, 62.8]
        self.tank_sensor_errors = [False, False, False, False]

    def read_sensors(self):
        pass


class FakeMqttGateway:
    def __init__(self) -> None:
        self.battery_soc = 79
        self.battery_soc_error = False

    def publish_status(self, payload):
        pass

    def handle_subscriptions(self):
        pass


class FakeOccupancy:
    def __init__(self) -> None:
        self.occupied = False

    def update(self):
        pass


class ThermalStoreControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.hardware = FakeHardwareGateway()
        self.mqtt = FakeMqttGateway()
        self.occupancy = FakeOccupancy()
        self.controller = ThermalStoreController(self.config, self.mqtt, self.hardware, self.occupancy)

    def testSensorErrorBehaviour(self):
        self.hardware.sensor_error = True
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": True})

    def testSocErrorBehaviour(self):
        self.mqtt.battery_soc_error = True
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": True})

    def testHighTempBehaviour(self):
        self.hardware.tank_sensors = [81, 81, 81, 81]
        state = self.controller.calculate_relay_state()
        self.mqtt.battery_soc = 99
        self.assertEqual(state, {"immersion": False, "boiler": False})

    def testImmersionBasedOnBatterySoc(self):
        self.mqtt.battery_soc = 79
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": False})
        self.mqtt.battery_soc = 81
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": True, "boiler": False})
        self.mqtt.battery_soc = 80.1
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"boiler": False})
        self.mqtt.battery_soc = 80
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": False})

    def testHeatingWhenOccupied(self):
        self.occupancy.occupied = True
        self.mqtt.battery_soc = 79
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": False})
        self.hardware.tank_sensors[2] = 49.9
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": True, "boiler": False})
        self.mqtt.battery_soc = 49.9
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": True})

    def testHeatingWhenCold(self):
        self.occupancy.occupied = False
        self.hardware.outside_sensor = 10
        self.mqtt.battery_soc = 79
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": False})
        self.hardware.tank_sensors[2] = 49.9
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": True, "boiler": False})
        self.mqtt.battery_soc = 49.9
        state = self.controller.calculate_relay_state()
        self.assertEqual(state, {"immersion": False, "boiler": True})
