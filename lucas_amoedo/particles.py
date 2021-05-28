import pyxel
import random
from pymunk import Body, Circle, ShapeFilter

from constants import PARTICLE_COLLISION_TYPE


class ExplosionParticles:
    DURATION = 30

    def __init__(self):
        self.particles = []
        self.done = False
        self.emitting = False

    def enter_space(self, space):
        self.space = space

    def draw(self, player_position, shift):
        for p in self.particles:
            if p.duration == self.DURATION:
                continue

            s = list(p.shapes)[0]
            p.position = player_position
            pos = p.position - shift + p.offset
            r = self.get_radius(s.radius, p.duration)
            c = self.get_color(p.duration)
            pyxel.circ(*pos, r, c)

    def get_color(self, duration):
        if duration > self.DURATION / 2:
            return pyxel.COLOR_YELLOW
        elif duration > self.DURATION / 3:
            return pyxel.COLOR_ORANGE
        else:
            return pyxel.COLOR_RED

    def get_radius(self, radius, duration):
        sizes = [1, 1.5, 2, 2.5, 3, 3.5, 4]
        sizes.reverse()
        for size in sizes:
            if duration <= self.DURATION / size:
                return size * radius

    def update(self):
        for i, p in enumerate(self.particles.copy()):
            if i == 0:
                p.duration -= 1
            else:
                _p = self.particles[i-1]
                if _p.duration <= self.DURATION * 0.666:
                    p.duration -= 1

            if p.duration <= 0:
                self.particles.remove(p)
                s = list(p.shapes)[0]
                self.space.remove(p, s)

        if not self.particles and self.emitting:
            self.done = True
            self.emitting = False

    def update_velocity(self, body, gravity, dumping, dt):
        body.update_velocity(body, (0, 0), 0, dt)

    def emmit(self, position, velocity):
        p = Body(1, float("inf"))
        p.duration = self.DURATION
        p.velocity_func = self.update_velocity
        dx = 6
        dy = 6
        p.offset = (random.uniform(-dx, dx), random.uniform(-dy, dy))

        s = Circle(p, 3)
        s.filter = ShapeFilter(PARTICLE_COLLISION_TYPE)

        self.particles.append(p)

        self.space.add(p, s)

        self.emitting = True
