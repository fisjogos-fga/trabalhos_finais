from easymunk import Vec2d, Arbiter, Body, Vec2d, ShapeFilter, pyxel as phys
import pyxel
import random
from math import sqrt, sin

FPS = 60
WIDTH, HEIGHT = 256, 196
SCREEN = Vec2d(WIDTH, HEIGHT)


class Particles:
    def __init__(self, space):
        self.particles = []
        self.space = space

    def draw(self, camera=pyxel):
        for p in self.particles:
            x, y = p.position
            if random.random() < 0.15:
                camera.rect(x, y, 2, 2, self.get_color(p.duration))
            else:
                camera.pset(x, y, self.get_color(p.duration))

    def update(self):
        for p in self.particles.copy():
            p.velocity = p.velocity.rotated(random.uniform(-5, 5))
            p.duration -= 1
            if p.duration <= 0:
                self.particles.remove(p)
                p.detach()

    def emmit(self, position, velocity):
        p = self.space.create_circle(
            radius=1,
            mass=0.1,
            moment=float("inf"),
            position=position,
            velocity=velocity,
            # filter=ShapeFilter(group=1),
        )
        p.duration = 105 - random.expovariate(1 / 10)
        p.velocity_func = self.update_velocity
        self.particles.append(p)

    def update_velocity(self, body, gravity, damping, dt):
        body.update_velocity(body, gravity / 2, 0.999, dt)
        # ax = random.uniform(-50, 50)
        # ay = random.uniform(-50, 50)
        # eta = 1
        # body.velocity += eta * Vec2d(ax, ay) * sqrt(dt)

        acc = Vec2d(200 * sin(body.duration / 10), 0)
        body.velocity += acc * dt

        vmax = 50
        if body.velocity.length > vmax:
            body.velocity = vmax * body.velocity.normalized()

    def get_color(self, t):
        if t > 95:
            return pyxel.COLOR_WHITE
        elif t > 80:
            return pyxel.COLOR_YELLOW
        elif t > 65:
            return pyxel.COLOR_RED
        elif t > 40:
            return pyxel.COLOR_PURPLE
        elif t > 25:
            return pyxel.COLOR_BROWN
        else:
            return pyxel.COLOR_GRAY


#
# MOON LANDER (SISTEMA DE PARTÍCULAS)
#
class Game:
    PLAYER_SHAPE = [(0, 6), (-3, -3), (+3, -3)]
    BASE_SHAPE = (25, 5)
    PLAYER_SPEED = 90
    PLAYER_COLOR = pyxel.COLOR_PINK
    BASE_COLOR = pyxel.COLOR_ORANGE
    GRAVITY = Vec2d(0, -25)
    THRUST = -3 * GRAVITY
    ANGULAR_VELOCITY = 180
    FLOOR_STEP = 30
    FLOOR_DY = 15
    FLOOR_N = 42
    PLAYER_COL_TYPE = 1
    BASE_COL_TYPE = 2
    FLOOR_COL_TYPE = 3
    MAX_IMPULSE = 30
    PROB_CREATE_ASTEROID = 1 / 120

    def __init__(self):
        self.space = space = phys.space(
            gravity=self.GRAVITY,
            camera=phys.Camera(flip_y=True),
            friction=1,
        )
        self.landed = False
        self.victory = False

        # Cria jogador
        self.player = space.create_poly(
            self.PLAYER_SHAPE,
            mass=1,
            moment=2,
            position=SCREEN / 2,
            friction=1.0,
            collision_type=self.PLAYER_COL_TYPE,
            filter=ShapeFilter(group=1),
        )
        self.particles = Particles(space)
        self.asteroids = []
        self.bombs = []

        # Cria base
        dx = random.uniform(-WIDTH, WIDTH)
        self.base = space.create_box(
            self.BASE_SHAPE,
            position=self.player.position + (dx, -0.45 * HEIGHT),
            friction=1.0,
            collision_type=self.BASE_COL_TYPE,
            body_type=Body.STATIC,
        )

        # Cria chão
        shape = list(self.base.shapes)[0]
        bb = shape.cache_bb()
        self.targets = []
        self.make_floor(bb.right, bb.bottom, self.FLOOR_STEP, self.FLOOR_DY)
        self.make_floor(bb.left, bb.bottom, -self.FLOOR_STEP, self.FLOOR_DY)

        # Escuta colisões entre base/chão e jogador
        space.collision_handler(
            self.PLAYER_COL_TYPE, self.BASE_COL_TYPE, post_solve=self.on_land
        )
        self.space.collision_handler(
            self.PLAYER_COL_TYPE, self.FLOOR_COL_TYPE, begin=self.on_collision
        )

    def on_collision(self, arb: Arbiter):
        self.landed = True
        self.victory = False
        return True

    def on_land(self, arb: Arbiter):
        if not self.landed:
            self.victory = arb.total_impulse.length < self.MAX_IMPULSE
        self.landed = True

    def make_floor(self, x, y, step, dy):
        body = self.space.static_body

        a = Vec2d(x, y)
        for _ in range(self.FLOOR_N):
            b = a + (step, random.uniform(-dy, dy))
            body.create_segment(a, b, 1, collision_type=self.FLOOR_COL_TYPE)
            a = b
            if random.random() < 0.25:
                target = self.space.create_circle(
                    20, position=(a + b) / 2, body_type="static"
                )
                self.targets.append(target)

    def drop_bomb(self):
        position = self.player.local_to_world((0, -4))
        vel = self.player.rotation_vector.rotated(-90) * 120
        bomb = self.space.create_circle(
            2, position, color=pyxel.COLOR_RED, velocity=vel
        )
        self.bombs.append(bomb)

    def update(self):
        if not self.landed:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.player.angular_velocity = +self.ANGULAR_VELOCITY
            elif pyxel.btn(pyxel.KEY_RIGHT):
                self.player.angular_velocity = -self.ANGULAR_VELOCITY
            else:
                self.player.angular_velocity = 0.0

            if pyxel.btn(pyxel.KEY_UP):
                self.player.apply_force_at_local_point(4 * self.THRUST)

                # for _ in range(2):
                self.particles.emmit(
                    position=self.player.local_to_world((random.uniform(-2, 2), -3)),
                    velocity=-random.uniform(50, 90)
                    * self.player.rotation_vector.perpendicular(),
                )

            if pyxel.btnp(pyxel.KEY_SPACE):
                self.drop_bomb()

        self.update_asteroids()
        self.update_bombs()

        dt = 1 / FPS
        self.particles.update()
        self.space.step(dt, sub_steps=4)
        self.space.camera.follow(self.player.position)

    def update_bombs(self):
        ...

    def update_asteroids(self):
        if random.random() < self.PROB_CREATE_ASTEROID:
            self.create_asteroid()

        new_asteroids = []
        for asteroid in self.asteroids:
            asteroid.life -= 1
            if asteroid.life <= 0:
                asteroid.detach()
            else:
                new_asteroids.append(asteroid)
                
        self.asteroids = new_asteroids

    def create_asteroid(self):
        pos = self.player.position + Vec2d(0, 50)
        size = 10
        points = []

        for _ in range(10):
            dx = random.uniform(-size, size)
            dy = random.uniform(-size, size)
            points.append(pos + (dx, dy))

        asteroid = self.space.create_poly(points)
        asteroid.life = 240
        self.asteroids.append(asteroid)

    def draw(self):
        pyxel.cls(0)
        camera = self.space.camera
        camera.draw(self.space.static_body)
        camera.draw(self.base)
        self.particles.draw(camera)
        camera.draw(self.player)

        for asteroid in self.asteroids:
            camera.drawb(asteroid)

        for target in self.targets:
            camera.drawb(target)

        for bomb in self.bombs:
            camera.drawb(bomb)

        if self.landed:
            msg = "PARABENS!" if self.victory else "PERDEU :("
            x = WIDTH / 2 - len(msg) * pyxel.FONT_WIDTH / 2
            pyxel.text(x, HEIGHT // 2 - 20, msg, pyxel.COLOR_RED)


game = Game()
pyxel.init(WIDTH, HEIGHT, fps=FPS)
pyxel.mouse(True)
pyxel.run(game.update, game.draw)