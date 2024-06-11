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
    delta_time: float = 0.5 

    def weights(self) -> tuple[float, float, float]:
        return (self.Tjoin, self.Tleave, self.D)
    

class Cockroach(Agent):
    config: Aggregation
    # The starting state of the agent
    state:str = 'wandering'
    # D times for checking the nr. of neighbors to leave the aggregation.
    D:int = 0

    def update(self):
        # If the agent state is wandering, then we will keep moving randomly and checking if we can join anything.
        if self.state == 'wandering':
            # Move Randomly
            self.change_position()
            # Check if we can join any aggregation
            self.joining()
        # The we are joining an aggregation
        if self.state == 'joining':
            # If we can join an aggregation we can not stop straight away we move a little and then stop
            self.pos += self.move * self.config.Tjoin
            # We then change the posiiton to still
            self.state = 'still'
        
        if self.state == 'still':
            # We apply the still() function which freezes the movement of the agent, and allows to move it specific to the instructions in the assignment.
            self.D += 1
            self.still(self.D)
            # The nr of iterations in which it was frozen
            if self.D == 50:
                # We set the agents iterations back to zero once it moves again
                self.D = 0
        if self.state == 'leaving':
            # If it is leaving it has to move for some time until it can be wandering again.
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
        # D times for checking the nr. of neighbors to leave the aggregation.
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
