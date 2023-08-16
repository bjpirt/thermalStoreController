from timeout import Timeout
from umqtt.robust import MQTTClient  # type: ignore
import json


class MQTTConnection:
    def __init__(self, config):
        self._client = MQTTClient("thermal_store", config["mqtt_address"], keepalive=100)
        self._client.connect()
        self._client.set_callback(self.handle_message)
        self._client.subscribe("tycoch/thermalstore/cmd")
        self._client.subscribe("tycoch/battery/soc")
        self._battery_soc: int | None = None
        self._soc_timeout = Timeout()
        self._soc_timeout.set(60)

    def handle_message(self, topic, msg):
        decoded_topic = topic.decode()
        decoded_msg = msg.decode()
        try:
            print(f"received {decoded_msg} on {decoded_topic}")
            parsed = json.loads(decoded_msg)
            if decoded_topic == "tycoch/battery/soc":
                self._battery_soc = parsed["value"]
                self._soc_timeout.reset()
                print(f"Set SoC to {self._battery_soc}")
            elif decoded_topic == "tycoch/thermalstore/cmd":
                # Used for settings, manual control, etc
                pass
        except Exception as e:
            print(e)
            return

    def publish_status(self, payload):
        self._client.publish("tycoch/thermalstore/status", json.dumps(payload))

    def handle_subscriptions(self):
        self._client.check_msg()

    @property
    def battery_soc(self) -> int | None:
        return self._battery_soc if not self._soc_timeout.ready else None

    @property
    def battery_soc_error(self):
        return self._soc_timeout.ready or self._battery_soc == None
