from .network_connection import NetworkConnection
try:
    from network import LAN, PHY_LAN8720  # type: ignore
    from machine import Pin  # type: ignore
except ImportError:
    pass


class Ethernet(NetworkConnection):
    def __init__(self) -> None:
        self._nic = LAN(
            mdc=Pin(23), mdio=Pin(18), power=None, ref_clk_mode=Pin.OUT,
            phy_type=PHY_LAN8720, phy_addr=0, ref_clk=Pin(17),
        )
        super().__init__("Ethernet")

    def connect(self):
        print("Connecting Ethernet")
        self._nic.active(True)

    def disconnect(self):
        print("Disconnecting Ethernet")
        self._nic.active(False)

    @property
    def is_connected(self):
        return self._nic.ifconfig()[0] != "0.0.0.0"

    @property
    def ip(self):
        return self._nic.ifconfig()[0]
