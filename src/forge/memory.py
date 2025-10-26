class Memory:
    def __init__(self):
        self.state: dict[str, object] = {}

    def get(self, key: str, default=None):
        return self.state.get(key, default)

    def set(self, key: str, value):
        self.state[key] = value
