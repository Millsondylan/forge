from typing import Any, Sequence

class Dispatcher:
    def __init__(self, policy: str = "round_robin"):
        self.policy = policy

    def route(self, tasks: Sequence[Any], agents: Sequence[Any]):
        if not agents:
            return []
        routed = []
        for i, t in enumerate(tasks):
            routed.append((agents[i % len(agents)], t))
        return routed
