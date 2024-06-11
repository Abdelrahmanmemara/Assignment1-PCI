from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random
import numpy as np
import scipy


@deserialize
@dataclass
class Aggregation(Config):
    # You can change these for different starting weights
    # The time elapse to join an aggregation
    number = np.random.normal(loc=0, scale=1)
    transformed_number = scipy.stats.norm.cdf(number)
    Tjoin:float = 0.3 + transformed_number
    # The time elapse to leave an
    Tleave:float = 0.5 + transformed_number
    # D times for checking the nr. of neighbors to leave the aggregation.
    D:int = 0
    delta_time: float = 0.5 

    def weights(self) -> tuple[float, float, float]:
        return (self.Tjoin, self.Tleave, self.D)
    

class Cockroach(Agent):
    config: Aggregation




class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class AggregationLive(Simulation):
    config: Aggregation


(
    AggregationLive(
        Aggregation(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Cockroach, images=["images/bird.png"])
    .run()
)
