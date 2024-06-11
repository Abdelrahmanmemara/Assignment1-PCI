from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    # You can change these for different starting weights
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.1
    separation_weight: float = 0.5
    initial_velocity = Vector2(0,0)
    max_velocity = Vector2(1,1)
    # These should be left as is.
    delta_time: float = 0.5                                   # To learn more https://gafferongames.com/post/integration_basics/ 
    mass: int = 20                                            

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig
    
    def change_position(self):
        self.move = self.config.initial_velocity
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        # Retrieving the weights 
        a,c,s = self.config.weights()
        mass = self.config.mass
        # Calculating the Ftotal
        agents = list(self.in_proximity_accuracy())
        agents_total_velocity = Vector2(0,0)
        average_distance = Vector2(0,0)
        average_position = Vector2(0,0)
        
        for agent, dist in agents:
            # For the Allignemnt 
            agents_total_velocity += agent.move
            # For the Separation
            average_distance += Vector2(dist)
            # For the Cohesion
            average_position += agent.pos
            average_position = average_position / len(agents)
            cohesion_force = average_position - self.pos
        if len(agents) > 0:
            # For the allignment 
            average_velocity = agents_total_velocity / len(agents)
            allignment = average_velocity - self.move
            # For the Separation 
            separation = average_distance/ len(agents)
            # For the Cohesion
            cohesion = cohesion_force - self.move

        else:
            # For the allignment 
            allignment = Vector2(0,0)
            # For separation 
            separation = Vector2(0)
            # For the Cohesion
            cohesion = Vector2(1,1)

        ftotal = (a*allignment) + (c*cohesion) + (s*separation) / mass
        # Updating the move 
        self.move = self.move + ftotal 
        if Vector2.length(self.move) < Vector2.length(self.config.max_velocity):
            self.move = self.config.max_velocity.length() * self.move.normalize()
        elif Vector2.length(self.move) > Vector2.length(self.config.max_velocity):
            self.move = self.config.max_velocity.length() * self.move.normalize()  
        self.pos = self.pos + Vector2(self.move*self.config.delta_time) 
    # def average_velocity(self):
    #     agents_velocity = list(self.in_proximity_accuracy())
    #     if len(agents_velocity) > 0:
    #         agents_total_velocity = Vector2(sum(Vector2(agent.move) for agent, _ in agents_velocity))
    #         return agents_total_velocity/ len(agents_velocity)
    #     else:
    #         return Vector2(0,0)
    
    # def average_distance(self):
    #     agents = list(self.in_proximity_accuracy())
    #     if len(agents) > 0:
    #         agents_distance = sum(Vector2(dist) for agent, dist in agents)
    #         return agents_distance/ len(agents)
    #     else:
    #         return 0
    # def find_cohesion_force(self):
    #     agents = list(self.in_proximity_accuracy())
    #     if len(agents) > 0:
    #         average_position = sum(Vector2(agent.pos) for agent, _ in agents) / len(agents)
    #         cohesion_force = average_position - self.pos
    #         return cohesion_force
    #     else:
    #         return self.pos

        #END CODE -----------------


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

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
