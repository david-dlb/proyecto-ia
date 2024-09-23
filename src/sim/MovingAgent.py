from environment import Environment
from sim.Agent import Agent


from abc import ABC
from uuid import uuid4


class MovingAgent(Agent, ABC):
    def __init__(self, position, environment: Environment):
        super().__init__(uuid4(), environment)
        self.position = position