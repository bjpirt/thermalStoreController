from hardware_gateway_impl import HardwareGatewayImpl
from mqtt_gateway_impl import MqttGatewayImpl
from time import sleep
import network  # type: ignore
from config import config
from occupancy_impl import OccupancyImpl
from thermal_store_controller import ThermalStoreController


def setup_wifi():
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    if not nic.isconnected():
        nic.connect(config["wifi_network"], config["wifi_password"])
        while not nic.isconnected():
            print("Waiting for WiFi")
            sleep(0.5)
        print("WiFi Ready")


def main():
    setup_wifi()
    mqtt = MqttGatewayImpl(config)
    hardware = HardwareGatewayImpl()
    occupancy = OccupancyImpl(mqtt, config)
    controller = ThermalStoreController(config, mqtt, hardware, occupancy)
    while True:
        mqtt.handle_subscriptions()
        controller.update()
        mqtt.publish_status(controller.status)

        sleep(1)


if __name__ == "__main__":
    main()
