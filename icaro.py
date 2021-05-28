from easymunk import Vec2d, Arbiter, Body, Vec2d, ShapeFilter, pyxel as phys
import pyxel
import random

FPS = 30
WIDTH, HEIGHT = 256, 196
SCREEN = Vec2d(WIDTH, HEIGHT)


class Particles:
    def __init__(self, space, gravity, damping=None):
        self.particles = []
        self.space = space
        self.gravity = gravity
        self.damping = damping if damping is not None else 0.99

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
            filter=ShapeFilter(group=1),
        )
        p.duration = 105 - random.expovariate(1 / 10)
        p.velocity_func = self.update_velocity
        self.particles.append(p)

    def update_velocity(
        self, body, gravity, damping, dt
    ):  # damping =1, gravidade mais prox de 0
        body.update_velocity(body, self.gravity / 2, self.damping, dt)

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
# MOON LANDER (SISTEMA DE PARTÍCULAS) com explosao e asteroides :)
#
class Game:
    PLAYER_SHAPE = [(0, 6), (-3, -3), (3, -3)]
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
    ASTEROID_COL_TYPE = 4
    MAX_IMPULSE = 30
    MAX_FUEL = 30
    MIN_FUEL = 0

    def __init__(self):
        self.space = space = phys.space(
            gravity=self.GRAVITY,
            camera=phys.Camera(flip_y=True),
            friction=1,
        )
        self.landed = False
        self.victory = False
        self.fuel = self.MAX_FUEL

        # Cria jogador
        self.player = space.create_poly(
            self.PLAYER_SHAPE,
            mass=1,
            moment=2,
            position=SCREEN / 2,
            friction=1.0,
            collision_type=self.PLAYER_COL_TYPE,
            filter=ShapeFilter(group=1),
            color=pyxel.COLOR_GRAY,
        )
        self.particles = Particles(space, self.GRAVITY, 0.99)
        self.explosion_particles = Particles(space, self.GRAVITY / 3, 0.98)

        self.asteroids = []

        # Cria base
        dx = random.uniform(-WIDTH, WIDTH)
        # dx = 0
        self.base = space.create_box(
            self.BASE_SHAPE,
            position=self.player.position + (dx, -0.45 * HEIGHT),
            friction=20.0,
            collision_type=self.BASE_COL_TYPE,
            body_type=Body.STATIC,
            color=pyxel.COLOR_YELLOW,
        )

        # Cria chão
        shape = list(self.base.shapes)[0]
        bb = shape.cache_bb()
        self.make_floor(bb.right, bb.bottom, self.FLOOR_STEP, self.FLOOR_DY)
        self.make_floor(bb.left, bb.bottom, -self.FLOOR_STEP, self.FLOOR_DY)

        # Escuta colisões entre base/chão e jogador
        space.collision_handler(
            self.PLAYER_COL_TYPE, 
            self.BASE_COL_TYPE, 
            post_solve=self.on_land_collision
        )
        self.space.collision_handler(
            self.PLAYER_COL_TYPE,
            self.FLOOR_COL_TYPE,
            post_solve=self.on_floor_collision,
        )
        
        # Escuta colisões entre jogador e asteroide
        self.space.collision_handler(
            self.PLAYER_COL_TYPE,
            self.ASTEROID_COL_TYPE,
            post_solve=self.on_asteroid_collision,
        )

        self.space.collision_handler(
            self.ASTEROID_COL_TYPE,
            self.FLOOR_COL_TYPE,
            post_solve=self.on_asteroid_floor_base_collision,
        )

        self.space.collision_handler(
            self.ASTEROID_COL_TYPE,
            self.BASE_COL_TYPE,
            post_solve=self.on_asteroid_floor_base_collision,
        )

    def should_explode(self, arb):
        return self.fuel > self.MIN_FUEL and not (
            arb.total_impulse.length < self.MAX_IMPULSE
        )

    def explode(self, position):
        for _ in range(120):
            self.explosion_particles.emmit(
                position=position,
                velocity=Vec2d(random.uniform(20, 30), 0).rotated(
                    random.uniform(-150, 160)
                ),
            )
        self.space.remove(self.player.shape, self.player)

    def on_floor_collision(self, arb: Arbiter):
        self.landed = True
        self.victory = False
        if self.should_explode(arb):
            self.explode(arb.contact_point_set.points[0].point_b)
        return True

    def on_land_collision(self, arb: Arbiter):
        if self.should_explode(arb):
            self.victory = False
            self.explode(arb.contact_point_set.points[0].point_b)
        else:
            self.victory = True
            self.landed = True

    def on_asteroid_collision(self, arb: Arbiter):
        self.landed = True
        self.victory = False
        self.explode(arb.contact_point_set.points[0].point_b)
        return True

    def on_asteroid_floor_base_collision(self, arb: Arbiter):
        if len(self.asteroids) > 0 and arb.is_first_contact:
            self.space.remove(arb.shapes[0])
        return True

    def make_floor(self, x, y, step, dy):
        body = self.space.static_body

        a = Vec2d(x, y)
        for _ in range(self.FLOOR_N):
            b = a + (step, random.uniform(-dy, dy))
            body.create_segment(a, b, 1, collision_type=self.FLOOR_COL_TYPE)
            a = b

    def _update_movimentation(self):
        if not self.landed and self.fuel > self.MIN_FUEL:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.player.angular_velocity = self.ANGULAR_VELOCITY
            elif pyxel.btn(pyxel.KEY_RIGHT):
                self.player.angular_velocity = -self.ANGULAR_VELOCITY
            else:
                self.player.angular_velocity = 0.0

            if pyxel.btn(pyxel.KEY_UP):
                self.player.apply_force_at_local_point(4 * self.THRUST)
                if self.fuel > self.MIN_FUEL:
                    self.fuel -= 0.1
                    for _ in range(1):
                        self.particles.emmit(
                            position=self.player.local_to_world(
                                (random.uniform(-2, 2), -3)
                            ),
                            velocity=-random.uniform(30, 40)
                            * self.player.rotation_vector.perpendicular(),
                        )

    def _update_spawn_asteroids(self):
        if random.random() > 1 / 10:
            return False
        dx = random.uniform(-WIDTH, WIDTH)
        for _ in range(1):
            asteroid = self.space.create_circle(
                radius=random.uniform(5, 8),
                mass=10,
                position=self.player.position + (dx, HEIGHT),
                collision_type=self.ASTEROID_COL_TYPE,
                body_type=Body.DYNAMIC,
                color=pyxel.COLOR_YELLOW,
            )
        self.asteroids.append(asteroid)
        return True

    def update(self):
        if not self.victory:
            self._update_movimentation()
            self._update_spawn_asteroids()
        dt = 1 / FPS
        self.particles.update()
        self.explosion_particles.update()
        self.space.step(dt, sub_steps=4)
        self.space.camera.follow(self.player.position)

    def draw(self):
        pyxel.cls(0)
        camera = self.space.camera
        camera.draw(self.space.static_body)
        camera.draw(self.base)
        camera.draw(self.player)
        self.particles.draw(camera)
        self.explosion_particles.draw(camera)

        msg = "PARABÉNS!"

        if self.landed and not self.victory:
            msg = "PERDEU! :("
        if self.fuel > self.MIN_FUEL and not self.landed or self.victory:
            msg = f"Fuel: {round(self.fuel, 2)}"

        for asteroid in self.asteroids:
            camera.draw(asteroid)

        x = WIDTH / 2 - len(msg) * pyxel.FONT_WIDTH / 2
        pyxel.text(x, HEIGHT // 2 - 20, msg, pyxel.COLOR_RED)


game = Game()
pyxel.init(WIDTH, HEIGHT, fps=FPS)
pyxel.mouse(True)
pyxel.run(game.update, game.draw)