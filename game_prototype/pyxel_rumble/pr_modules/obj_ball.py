import random
import pyxel
import random
from easymunk import Vec2d, CircleBody, Arbiter
from .global_config import GameObject, CollisionType
from .particles import *
from .sound import sfx_ball_touch_floor, sfx_player_ball_score

class Ball (GameObject, CircleBody):
    def __init__(self, x, y, space):
        self.INIT_X, self.INIT_Y = x, y
        super().__init__(
            radius=4,
            position=(x, y),
            elasticity=1.0,
            collision_type=CollisionType.BALL,
            color = pyxel.COLOR_LIGHTBLUE
        )
        self.SCORE = 0
        self.DAMAGE_PERCENTAGE = 0
        self.particles = Particles(space)

    def update (self):
        v = self.velocity
        mass = self.mass
        F = mass * 200
        self.force += Vec2d(0, -mass * 200)

        if pyxel.btnp(pyxel.KEY_R):
            self.particles.emmit(self.position, self.velocity)
            self.position = (self.INIT_X, self.INIT_Y)
            v = Vec2d(0,0)
        self.velocity = v
        
        

    def draw (self):
        self.particles.draw(self.particles.space.camera, pyxel.COLOR_RED)
        pyxel.circ(
            self.position[0], 
            self.position[1], 
            self.radius, 
            self.color)
    
    def register (self, space, message):
        space.add(self)
        @space.post_solve_collision(CollisionType.BALL, CollisionType.PLAYER)
        def _col_start(arb: Arbiter):
            sfx_player_ball_score()
            self.SCORE += 1
            self.DAMAGE_PERCENTAGE += 1
            self.velocity = (random.uniform(-2, 2)*self.DAMAGE_PERCENTAGE, 100 + 2 * self.DAMAGE_PERCENTAGE)
            
        @space.post_solve_collision(CollisionType.BALL, CollisionType.PLATFORM)
        def _col_start(arb: Arbiter):
            sfx_ball_touch_floor()
            self.SCORE = 0
            self.DAMAGE_PERCENTAGE = 0
            self.velocity = (0, 100 + 2 * self.DAMAGE_PERCENTAGE)