from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random


@deserialize
@dataclass
class Aggregation(Config):
    # You can change these for different starting weights

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)
    

class Cockroach(Agent):
    config: Aggregation
    # Initial params

class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class AggregationLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: Aggregation
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
