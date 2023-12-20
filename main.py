from hardware_gateway_impl import HardwareGatewayImpl
from mqtt_gateway_impl import MqttGatewayImpl
from time import sleep
import network  # type: ignore
import machine  # type: ignore
from config import Config
from occupancy_impl import OccupancyImpl
from thermal_store_controller import ThermalStoreController


def setup_wifi(config):
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    if not nic.isconnected():
        nic.connect(config.wifi_network, config.wifi_password)
        while not nic.isconnected():
            print("Waiting for WiFi")
            sleep(0.5)
        print("WiFi Ready")


def setup_ethernet(config):
    nic = network.LAN(
        mdc=machine.Pin(23),
        mdio=machine.Pin(18),
        power=None, phy_type=network.PHY_LAN8720, phy_addr=0, ref_clk=machine.Pin(17),
        ref_clk_mode=machine.Pin.OUT)
    nic.active(True)
    while nic.ifconfig()[0] == "0.0.0.0":
        print("Waiting for Ethernet")
        sleep(0.5)
    print("Ethernet Ready")
    ifconfig = nic.ifconfig()
    print(f"IP: {ifconfig[0]}")


def main():
    config = Config()
    setup_wifi(config)
    # setup_ethernet(config)
    hardware = HardwareGatewayImpl()
    mqtt = MqttGatewayImpl(config)
    occupancy = OccupancyImpl(mqtt, config)
    controller = ThermalStoreController(config, mqtt, hardware, occupancy)
    while True:
        mqtt.handle_subscriptions()
        controller.update()
        mqtt.publish_status(controller.status)

        sleep(1)


if __name__ == "__main__":
    main()
