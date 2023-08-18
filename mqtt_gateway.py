class MqttGateway:
    def publish_status(self, payload):
        pass

    def handle_subscriptions(self):
        pass

    @property
    def battery_soc(self) -> int | None:
        pass

    @property
    def battery_soc_error(self):
        pass

    @property
    def ac_power(self) -> int | None:
        pass

    @property
    def ac_power_error(self):
        pass
