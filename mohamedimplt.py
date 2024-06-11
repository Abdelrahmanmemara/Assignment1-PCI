from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random
import numpy as np
import scipy.stats


@deserialize
@dataclass
class Aggregation(Config):
    # You can change these for different starting weights
    # The time elapse to join an aggregation
    number = np.random.normal(loc=0, scale=1)
    transformed_number = scipy.stats.norm.cdf(number)
    Tjoin: float = 0.3 + transformed_number
    # The time elapse to leave an aggregation
    Tleave: float = 0.5 + transformed_number
    delta_time: float = 0.5
    D: int = 50  # Time steps to check for neighbors when still

    def weights(self) -> tuple[float, float, float]:
        return (self.Tjoin, self.Tleave, self.D)


class Cockroach(Agent):
    config: Aggregation
    # The starting state of the agent
    state: str = 'wandering'
    # Timer for state transitions
    timer: int = 0

    def update(self):
        if self.state == 'wandering':
            self.wandering()
            self.joining()

        elif self.state == 'joining':
            self.timer += 1
            self.move_towards_site()
            if self.timer >= self.config.Tjoin * 60:  # Converting seconds to frames
                self.timer = 0
                self.state = 'still'

        elif self.state == 'still':
            self.timer += 1
            if self.timer % self.config.D == 0:
                self.leaving()

        elif self.state == 'leaving':
            self.timer += 1
            self.move_away_from_site()
            if self.timer >= self.config.Tleave * 60:  # Converting seconds to frames
                self.timer = 0
                self.state = 'wandering'

    def wandering(self):
        # Random walk implementation
        if np.random.rand() < 0.1:  # Change direction occasionally
            self.move = Vector2(np.random.uniform(-1, 1), np.random.uniform(-1, 1)).normalize()
        self.pos += self.move * self.config.movement_speed

    def move_towards_site(self):
        # Move towards the site
        site = self.closest_site()
        direction = (site - self.pos).normalize()
        self.pos += direction * self.config.movement_speed

    def move_away_from_site(self):
        # Move away from the site
        site = self.closest_site()
        direction = (self.pos - site).normalize()
        self.pos += direction * self.config.movement_speed

    def joining(self):
        neighbors = list(self.in_proximity_accuracy())
        prob = len(neighbors) / 50  # Adjust threshold as needed
        if prob > np.random.rand():
            self.state = 'joining'

    def leaving(self):
        neighbors = list(self.in_proximity_accuracy())
        prob = len(neighbors) / 50  # Adjust threshold as needed
        if prob < np.random.rand():
            self.state = 'leaving'

    def closest_site(self):
        # Define the positions of the two sites
        sites = [Vector2(100, 100), Vector2(300, 300)]
        closest_site = min(sites, key=lambda site: self.pos.distance_to(site))
        return closest_site


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
