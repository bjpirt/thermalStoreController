from time import sleep
from config import Config
from lib import Timeout
from .network_connection import NetworkConnection
from .ethernet import Ethernet
from .wifi import WiFi


class NetworkManager:
    def __init__(self, config: Config) -> None:
        self._wifi = WiFi(config.wifi_network, config.wifi_password)
        self._ethernet = Ethernet()
        self._selected_interface: NetworkConnection = self._ethernet
        self._connection_timeout = Timeout(10)

    def connect(self):
        self._selected_interface.connect()
        self._connection_timeout.reset()

    def wait_for_connection(self):
        self.connect()
        while not self.is_connected:
            self.update()
            sleep(0.1)
        print(f"Network is connected ({self.type})")

    def update(self):
        if not self.is_connected:
            if self._connection_timeout.ready:
                self._selected_interface.disconnect()

                if self._selected_interface == self._ethernet:
                    self._selected_interface = self._wifi
                else:
                    self._selected_interface = self._ethernet

                print(f"Switching to {self._selected_interface.name}")
                self._selected_interface.connect()
                self._connection_timeout.reset()
        else:
            self._connection_timeout.reset()

    @property
    def is_connected(self):
        return self._selected_interface.is_connected

    @property
    def ip(self):
        return self._selected_interface.ip

    @property
    def type(self):
        return self._selected_interface.name
