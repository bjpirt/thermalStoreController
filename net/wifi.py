from .network_connection import NetworkConnection
try:
    from network import WLAN, STA_IF  # type: ignore
except ImportError:
    pass


class WiFi(NetworkConnection):
    def __init__(self, ssid: str, password: str) -> None:
        self._ssid = ssid
        self._password = password
        self._nic = WLAN(STA_IF)
        super().__init__("WiFi")

    def connect(self):
        print(f"Connecting WiFi [{self._ssid}]")
        self._nic.active(True)
        if not self.is_connected:
            self._nic.connect(self._ssid, self._password)

    def disconnect(self):
        print("Disconnecting WiFi")
        self._nic.active(False)

    @property
    def is_connected(self):
        return self._nic.isconnected()

    @property
    def ip(self):
        return self._nic.ifconfig()[0]
