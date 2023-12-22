# pylint: disable=unsubscriptable-object

from typing import Union
from .mqtt_gateway import MqttGateway
from lib.timeout import Timeout
try:
    from machine import reset  # type: ignore
    from umqtt.robust import MQTTClient  # type: ignore
except ImportError:
    pass
import json

SOC_TOPIC = "tycoch/battery/soc"
AC_TOPIC = "tycoch/ac"


class MqttGatewayImpl(MqttGateway):
    def __init__(self, config):
        self._config = config
        self._client = MQTTClient("thermal_store", config.mqtt_address, keepalive=100)
        self._client.connect()
        self._client.set_callback(self.handle_message)
        self._client.subscribe(f"{self._config.mqtt_topic_prefix}/set-config/#")
        self._client.subscribe(f"{self._config.mqtt_topic_prefix}/reboot")
        self._client.subscribe(SOC_TOPIC)
        self._client.subscribe(AC_TOPIC)
        self._battery_soc: Union[int, None] = None
        self._ac_power: Union[int, None] = None
        self._soc_timeout = Timeout()
        self._soc_timeout.set(60)
        self._ac_timeout = Timeout()
        self._ac_timeout.set(60)
        self._publish_timeout = Timeout()
        self._publish_timeout.set(config.mqtt_publish_interval)
        self._full_publish_timeout = Timeout()
        self._full_publish_timeout.set(config.mqtt_full_publish_interval)
        self._last_values = {}

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
            elif decoded_topic.startswith(f"{self._config.mqtt_topic_prefix}/set-config/"):
                setting = decoded_topic.replace(
                    f"{self._config.mqtt_topic_prefix}/set-config/", "")
                print(f"Setting '{setting}' to '{parsed['value']}'")
                self._config.set_value(setting, parsed["value"])
                self._config.save()
            elif decoded_topic == f"{self._config.mqtt_topic_prefix}/reboot":
                if parsed["value"] == "reboot":
                    print("Rebooting device")
                    reset()
        except json.decoder.JSONDecodeError as e:
            print(e)
            return

    def update(self, payload):
        self._handle_subscriptions()
        if self._full_publish_timeout.ready:
            self._full_publish_timeout.reset()
            self._last_values = {}

        if self._publish_timeout.ready:
            self._publish_timeout.reset()
            for topic, value in payload.items():
                self._publish(topic, value)
            self._update_config()

    def _update_config(self):
        for topic, value in self._config.get_dict().items():
            self._publish(f"config/{topic}", value)

    def _handle_subscriptions(self):
        self._client.check_msg()

    @property
    def battery_soc(self) -> Union[int, None]:
        return self._battery_soc if not self._soc_timeout.ready else None

    @property
    def battery_soc_error(self):
        return self._soc_timeout.ready or self._battery_soc is None

    @property
    def ac_power(self) -> Union[int, None]:
        return self._ac_power if not self._ac_timeout.ready else None

    @property
    def ac_power_error(self):
        return self._ac_timeout.ready or self._ac_power is None

    def _should_publish(self, topic: str, value) -> bool:
        if topic not in self._last_values or value != self._last_values[topic]:
            self._last_values[topic] = value
            return True
        return False

    def _publish(self, topic: str, value):
        if self._should_publish(topic, value):
            self._client.publish(f"{self._config.mqtt_topic_prefix}/{topic}", json.dumps({"value": value}))
