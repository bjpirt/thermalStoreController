from mqtt_connection import MQTTConnection
from time import sleep
import network  # type: ignore
from config import config
from thermal_store_controller import ThermalStoreController

nic = network.WLAN(network.STA_IF)


def setup_wifi():
    nic.active(True)
    if not nic.isconnected():
        nic.connect(config["wifi_network"], config["wifi_password"])
        while not nic.isconnected():
            print("Waiting for WiFi")
            sleep(0.5)
        print("WiFi Ready")


def main():
    setup_wifi()
    mqtt = MQTTConnection(config)
    controller = ThermalStoreController(config, mqtt)
    while True:
        mqtt.handle_subscriptions()
        controller.update()
        mqtt.publish_status(controller.status)

        sleep(1)


if __name__ == "__main__":
    main()
