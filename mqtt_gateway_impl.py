from mqtt_gateway import MqttGateway
from timeout import Timeout
from umqtt.robust import MQTTClient  # type: ignore
import json

SOC_TOPIC = "tycoch/battery/soc"
CMD_TOPIC = "tycoch/thermalstore/cmd"
AC_TOPIC = "tycoch/ac"
STATUS_TOPIC = "tycoch/thermalstore/status"


class MqttGatewayImpl(MqttGateway):
    def __init__(self, config):
        self._client = MQTTClient("thermal_store", config["mqtt_address"], keepalive=100)
        self._client.connect()
        self._client.set_callback(self.handle_message)
        self._client.subscribe(CMD_TOPIC)
        self._client.subscribe(SOC_TOPIC)
        self._client.subscribe(AC_TOPIC)
        self._battery_soc: int | None = None
        self._ac_power: int | None = None
        self._soc_timeout = Timeout()
        self._soc_timeout.set(60)
        self._ac_timeout = Timeout()
        self._ac_timeout.set(60)

    def handle_message(self, topic, msg):
        decoded_topic = topic.decode()
        decoded_msg = msg.decode()
        try:
            print(f"received {decoded_msg} on {decoded_topic}")
            parsed = json.loads(decoded_msg)
            if decoded_topic == SOC_TOPIC:
                self._battery_soc = parsed["value"]
                self._soc_timeout.reset()
                print(f"Set SoC to {self._battery_soc}")
            if decoded_topic == AC_TOPIC:
                self._ac_power = parsed["value"]
                self._ac_timeout.reset()
                print(f"Set AC level to {self._ac_power}")
            elif decoded_topic == CMD_TOPIC:
                # Used for settings, manual control, etc
                pass
        except Exception as e:
            print(e)
            return

    def publish_status(self, payload):
        self._client.publish(STATUS_TOPIC, json.dumps(payload))

    def handle_subscriptions(self):
        self._client.check_msg()

    @property
    def battery_soc(self) -> int | None:
        return self._battery_soc if not self._soc_timeout.ready else None

    @property
    def battery_soc_error(self):
        return self._soc_timeout.ready or self._battery_soc == None

    @property
    def ac_power(self) -> int | None:
        return self._ac_power if not self._ac_timeout.ready else None

    @property
    def ac_power_error(self):
        return self._ac_timeout.ready or self._ac_power == None
