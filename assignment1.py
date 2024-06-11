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
    delta_time: float = 0.5 
    threshold:float = 0.005

    def weights(self) -> tuple[float, float, float]:
        return (self.Tjoin, self.Tleave, self.D)
    

class Cockroach(Agent):
    config: Aggregation
    state:str = 'wandering'
    D:int = 0

    def update(self):

        if self.state == 'wandering':
            self.change_position()
            self.joining()
        if self.state == 'joining':
            print('yes')
            self.pos += self.move * self.config.Tjoin
            self.state = 'still'
        if self.state == 'still':
            self.still(self.D)
            self.D += 1
        if self.state == 'leaving':
            self.pos += self.move * self.config.Tleave
            self.state = 'wandering'
                
    def change_position(self):
        return super().change_position()
    
    def joining(self):
        neighbors = list(self.in_proximity_accuracy())
        prob = len(neighbors) / 50
        if prob > np.random.rand():
            self.state= 'joining'
    def still(self, D):
        self.freeze_movement()
        if D == 50:
            neighbors = list(self.in_proximity_accuracy())
            prob = len(neighbors) / 50
            if prob < np.random.rand():
                self.continue_movement()
                self.state = 'leaving'




class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()



(
    Simulation(
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
