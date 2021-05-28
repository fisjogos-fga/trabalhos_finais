import pyxel
from pymunk import Body, Circle, Vec2d

from constants import HEIGHT, PLAYER_COLLISION_TYPE
from ball_gun import BallGun


class Player:
    BALL_RADIUS = 8
    SPEED = 50
    ORIENTATION_LEFT = 1
    ORIENTATION_RIGHT = -1
    IMAGE_SIZE = BALL_RADIUS * 2
    TOTAL_HIT_POINTS = 4
    INITIAL_POSITION = (0, HEIGHT - 10)
    BLINKING_TIME = 50

    def __init__(self):
        body = Body(1.0, 1.0)
        shape = Circle(body, self.BALL_RADIUS)

        body.position = self.INITIAL_POSITION
        body.reference = self

        shape.collision_type = PLAYER_COLLISION_TYPE
        shape.elasticity = 0.0

        self.orientation = self.ORIENTATION_RIGHT

        self.body = body
        self.shape = shape

        self.ball_gun = BallGun()

        self.hit_points = self.TOTAL_HIT_POINTS

        self.jumping = False

        self.blinking = False

        self.ticks = 0

    def enter_space(self, space):
        space.add(self.body, self.shape)
        self.space = space

        self.ball_gun.enter_space(space)

    @property
    def position(self):
        return self.body.position

    def blink(self):
        if self.blinking:
            return

        self.blinking = True

    def move(self, camera_pos):
        body = self.body
        vx, vy = body.velocity
        px, py = body.position

        sx, sy = camera_pos

        if vy == 0.0:
            self.jumping = False

        if py > HEIGHT + sy:
            self.hit_points -= 1
            body.position = self.INITIAL_POSITION

        if not self.jumping and pyxel.btn(pyxel.KEY_UP):
            body.velocity = (vx, -1.8 * self.SPEED)
            self.jumping = True

        elif pyxel.btn(pyxel.KEY_LEFT):
            self.orientation = self.ORIENTATION_LEFT
            body.velocity = (-self.SPEED, vy)
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.orientation = self.ORIENTATION_RIGHT
            body.velocity = (self.SPEED, vy)
        else:
            body.velocity = (0, vy)

    def shoot(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.ball_gun.fire(self.body.position, self.orientation)

        self.ball_gun.update()

    def update(self, camera_pos):
        self.move(camera_pos)
        self.shoot()

        if self.blinking:
            self.ticks += 1
            if self.ticks >= self.BLINKING_TIME:
                self.ticks = 0
                self.blinking = False

    def draw(self, shift):
        shape = self.shape

        bb = shape.bb

        x, y, _, _ = bb

        player_position = Vec2d(x, y) - shift

        image_page_index = 0
        image_width = self.orientation * self.IMAGE_SIZE
        image_heigth = self.IMAGE_SIZE
        transparent_color = pyxel.COLOR_YELLOW

        image_quantity = 4
        animation_speed = 2

        image_index = int(
            self.body.position.x // animation_speed
        ) % image_quantity

        image_u = 0 if self.jumping else self.IMAGE_SIZE * image_index
        image_position = (image_u, self.IMAGE_SIZE)

        if not self.blinking or (self.blinking and self.ticks % 2 == 0):
            pyxel.blt(
                *player_position,
                image_page_index,
                *image_position,
                image_width,
                image_heigth,
                transparent_color
            )

        self.ball_gun.draw(shift)
