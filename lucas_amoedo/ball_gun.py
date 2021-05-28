import pyxel
from pymunk import Body, Circle, Vec2d
from bullet import Bullet
from constants import BULLET_COLLISION_TYPE


class BallGun:
    RADIUS = 2
    POWER = 270
    BULLET_DURATION = 30

    def __init__(self):
        self.bullets = []

    def enter_space(self, space):
        self.space = space

    def fire(self, position, orientation):
        body = Body(body_type=Body.DYNAMIC)
        shape = Circle(body, self.RADIUS)

        shape.friction = 0.5
        shape.density = 0.1
        shape.collision_type = BULLET_COLLISION_TYPE

        body.position = position

        self.space.add(body, shape)

        self.bullets.append(
            Bullet(body, shape, 0)
        )

        self.__apply_impulse(body, orientation)

    def __apply_impulse(self, body, orientation):
        impulse = Vec2d(-orientation, 0) * self.POWER

        body.apply_impulse_at_world_point(impulse, body.position)

    def update(self):
        for bullet in self.bullets.copy():
            bullet.tick += 1

            if bullet.tick >= self.BULLET_DURATION:
                self.space.remove(bullet.body, bullet.shape)
                self.bullets.remove(bullet)

    def draw(self, shift):
        for bullet in self.bullets:
            body = bullet.body
            shape = bullet.shape

            pos = body.position - shift

            pyxel.circ(
                *pos,
                shape.radius,
                pyxel.COLOR_RED
            )
