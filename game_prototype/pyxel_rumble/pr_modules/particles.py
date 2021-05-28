import random
import pyxel
from .anim_dog_moveset import *
from .anim_rabbit_moveset import *

class Particles:
    def __init__ (self, space):
        self.particles = []
        self.space = space
        self.duration = 0

    def draw (self, camera=pyxel):
        for p in self.particles:
            x, y = p.position
            camera.pset(x, y, self.get_color(p.duration))

    def update(self):
        for p in self.particles.copy():
            p. velocity = p.velocity.rotated(random.uniform(0, 360))
            p.duration -= 1
            if p.duration <= 0:
                self.particles.remove(p)

    def emmit(self, position, velocity, duration = 10000):
        p= self.space.create_body(
            mass = 0.1, 
            moment= float('inf'), 
            position = position, 
            velocity = velocity
        )
        p.duration = duration
        self.particles.append(p)

    def update_velocity(self, body, gravity, damping, dt):
        body.update_velocity(body, gravity / 100, damping, dt)

    def get_color(self, t):
        if t > 95:
            return pyxel.COLOR_WHITE
        elif t > 65:
            return pyxel.COLOR_GRAY
        elif t > 35:
            return pyxel.COLOR_BLACK
