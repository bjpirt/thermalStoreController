class NetworkConnection:
    def __init__(self, name) -> None:
        self.name = name

    def connect(self):
        pass

    def disconnect(self):
        pass

    @property
    def is_connected(self):
        pass

    @property
    def ip(self):
        pass
