from typing import Union


class MqttGateway:
    def publish_status(self, payload):
        pass

    def conect(self):
        pass

    @property
    def battery_soc(self) -> Union[int, None]:  # pylint: disable=unsubscriptable-object
        pass

    @property
    def battery_soc_error(self):
        pass

    @property
    def ac_power(self) -> Union[int, None]:  # pylint: disable=unsubscriptable-object
        pass

    @property
    def ac_power_error(self):
        pass
