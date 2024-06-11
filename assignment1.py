from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random


@deserialize
@dataclass
class FlockingConfig(Config):
    # You can change these for different starting weights
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    # These should be left as is.
    delta_time: float = 0.5                                   # To learn more https://gafferongames.com/post/integration_basics/ 
    mass: int = 20             

    wind_speed: float = 0.0  # Magnitude of wind speed
    wind_direction: Vector2 = Vector2(1, 0)  # Direction of wind                               

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)
    

class Bird(Agent):
    config: FlockingConfig
    # Initial params

class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig
    wind_update_interval = 100                      # frames per second ---- ADJUST THIS
    wind_frame_counter = 0

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def update_wind(self):                          # function for stage 2 to update wind
        self.wind_frame_counter += 1
        if self.wind_frame_counter >= self.wind_update_interval:
            # Update wind speed and direction
            self.config.wind_speed = random.uniform(0.0, 1.0)  # Update wind speed randomly
            self.config.wind_direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()  # Update wind direction randomly
            self.wind_frame_counter = 0

    def before_update(self):
        super().before_update()
        self.update_wind()                  # update wind

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")