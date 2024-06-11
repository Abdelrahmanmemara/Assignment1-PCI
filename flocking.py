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
    alignment = Vector2(0,0)
    separation = Vector2(0)
    cohesion = Vector2(1,1)

    MAX_VELOCITY = Vector2(1,1)

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        
        # Retrieve neighbors within the radius R
        neighbors = list(self.in_proximity_accuracy())
        
        # weights
        a,c,s = self.config.weights()
        mass = self.config.mass
        delta_time = self.config.delta_time
        wind_force = self.config.wind_speed * self.config.wind_direction

        # calculations 
        average_velocity = Vector2(0,0)        
        average_pos = Vector2(0,0)
        average_distance = Vector2(0,0)
        for neighbor, dist in neighbors:               # loop to find average position and average velocity 
            average_velocity += neighbor.move
            average_pos += neighbor.pos
            average_distance += Vector2(self.pos - neighbor.pos)

        # updations
        if len(neighbors) > 0:           
            average_velocity /= len(neighbors)                  # alignment     
            self.alignment = average_velocity - self.move       

            self.separation = average_distance/len(neighbors)               # separation

            average_pos /= len(neighbors)               # cohesion
            cohesion_force = average_pos - self.pos
            self.cohesion = cohesion_force - self.move

            f_total = (self.alignment*a + self.separation*s + self.cohesion*c) / mass    # f_total
            f_total += wind_force  # Add wind force
            
            self.move += f_total                        # velocity 

            if Vector2.length(self.move) < Vector2.length(self.MAX_VELOCITY):
                self.move = self.MAX_VELOCITY.length() * self.move.normalize()
            elif Vector2.length(self.move) > Vector2.length(self.MAX_VELOCITY):
                self.move = self.MAX_VELOCITY.length() * self.move.normalize()  
            self.pos = self.pos + Vector2(self.move*delta_time)


    def get_wind_effect(self) -> Vector2:
        wind_direction = self.config.wind_direction
        wind_speed = self.config.wind_speed

        # Check if bird is in the path of the wind
        bird_direction = self.move.normalize()
        dot_product = bird_direction.dot(wind_direction)
        
        # Assuming birds within a 45 degree angle of the wind direction are affected
        if dot_product > 0.5:
            return wind_direction * wind_speed
        else:
            return Vector2(0, 0)

        #END CODE -----------------


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

(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .run()
)
