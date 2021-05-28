
from pymunk.arbiter import Arbiter
from pymunk.vec2d import Vec2d
import pyxel
import random
from pymunk import Space, Body, Circle, Poly, Segment, Vec2d, BB, ShapeFilter

FPS = 30
WIDTH, HEIGHT = 256, 196
SCREEN = Vec2d(WIDTH, HEIGHT)


#
# MOON LANDER
#

class Particles:
    def __init__(self, space):
        self.particles = []
        self.space = space

    def draw(self, shift):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def emmit(self, position, velocity):
        raise NotImplementedError


class ExplosionParticles(Particles):
    DURATION = 30

    def draw(self, player_position, shift):
        for p in self.particles:
            if p.duration == self.DURATION:
                # Não desenha se a duração da partícula ainda não
                # foi descontada em pelo menos 1.
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
        s.filter = ShapeFilter(1)

        self.particles.append(p)

        self.space.add(p, s)


class FuelParticles(Particles):
    def draw(self, shift):
        for p in self.particles:
            x, y = p.position - shift
            if random.random() < 0.15:
                pyxel.rect(x, y, 2, 2, self.get_color(p.duration))
            else:
                pyxel.pset(x, y, self.get_color(p.duration))

    def update(self):
        for p in self.particles.copy():
            p.velocity = p.velocity.rotated(random.uniform(-5, 5)) 
            p.duration -= 1
            if p.duration <= 0:
                self.particles.remove(p)

    def emmit(self, position, velocity):
        p = Body(0.1, float("inf"))
        p.position = position
        p.velocity = velocity
        p.duration = 105 - random.expovariate(1 / 10)
        p.velocity_func = self.update_velocity
        self.particles.append(p)

        s = Circle(p, 1)
        s.filter = ShapeFilter(group=1)

        self.space.add(p, s)
        

    def update_velocity(self, body, gravity, damping, dt):
        body.update_velocity(body, -gravity / 2, 0.99, dt)

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
    PLAYER_SIZE = 2
    PLAYER_SHAPE = [
        (0, -2 * PLAYER_SIZE),
        (-PLAYER_SIZE, PLAYER_SIZE),
        (PLAYER_SIZE, PLAYER_SIZE)
    ]
    BASE_SHAPE = (20, 4)
    PLAYER_SPEED = 90
    PLAYER_COLOR = pyxel.COLOR_PINK
    BASE_COLOR = pyxel.COLOR_ORANGE 
    GRAVITY = Vec2d(0, 25)
    THRUST = -3 * GRAVITY
    ANGULAR_VELOCITY = 5
    FLOOR_STEP = 30
    FLOOR_DY = 15
    FLOOR_N = 42
    PLAYER_COL_TYPE = 1
    BASE_COL_TYPE = 2
    FLOOR_COL_TYPE = 3
    MAX_IMPULSE = 30

    def __init__(self):
        self.space = Space()
        self.space.gravity = self.GRAVITY
        self.camera_pos = Vec2d(0, 0)
        self.landed = False
        self.victory = False

        # Cria jogador
        self.player = Body(1, 2, body_type=Body.DYNAMIC)
        self.player.position = SCREEN / 2

        shape = Poly(self.player, self.PLAYER_SHAPE)
        shape.friction = 1.0
        shape.collision_type = self.PLAYER_COL_TYPE
        shape.filter = ShapeFilter(group=1)
        self.space.add(self.player, shape)

        # Cria partículas
        self.fuel_particles = FuelParticles(self.space)
        self.explosion_particles = ExplosionParticles(self.space)

        # Cria base
        dx = random.uniform(-WIDTH, WIDTH)
        self.base = Body(body_type=Body.STATIC)
        self.base.position = self.player.position + (dx, 0.45 * HEIGHT)

        shape = Poly.create_box(self.base, self.BASE_SHAPE)
        shape.friction = 1.0
        shape.collision_type = self.BASE_COL_TYPE
        self.space.add(self.base, shape)

        # Cria chão
        shape = list(self.base.shapes)[0]
        bb = shape.cache_bb()
        self.make_floor(bb.right, bb.bottom, self.FLOOR_STEP, self.FLOOR_DY)
        self.make_floor(bb.left, bb.bottom, -self.FLOOR_STEP, self.FLOOR_DY)

        # Escuta colisões entre base/chão e jogador
        handler = self.space.add_collision_handler(
            self.PLAYER_COL_TYPE,
            self.BASE_COL_TYPE
        )
        handler.post_solve = self.on_land

        handler = self.space.add_collision_handler(
            self.PLAYER_COL_TYPE,
            self.FLOOR_COL_TYPE
        )
        handler.begin = self.on_collision

    def emmit_explosion_particles(self):
        if not self.landed:
            for _ in range(8):
                self.explosion_particles.emmit(..., ...)

    def on_collision(self, arb: Arbiter, space, data):
        self.emmit_explosion_particles()

        self.landed = True
        self.victory = False
        return True

    def on_land(self, arb: Arbiter, space, data):
        if not self.landed:
            self.victory = arb.total_impulse.length < self.MAX_IMPULSE
            if not self.victory:
                self.emmit_explosion_particles()

        self.landed = True
        
    def make_floor(self, x, y, step, dy):
        body = self.space.static_body
        
        a = Vec2d(x, y)
        for _ in range(self.FLOOR_N):
            b = a + (step, random.uniform(-dy, dy))
            shape = Segment(body, a, b, 2)
            shape.collision_type = self.FLOOR_COL_TYPE
            self.space.add(shape)
            a = b

    def update(self):
        if not self.landed:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.player.angular_velocity = -self.ANGULAR_VELOCITY
            elif pyxel.btn(pyxel.KEY_RIGHT):
                self.player.angular_velocity = +self.ANGULAR_VELOCITY
            else:
                self.player.angular_velocity = 0.0
            
            if pyxel.btn(pyxel.KEY_UP):
                self.player.force += self.THRUST.rotated(self.player.angle)

                p_shape = list(self.player.shapes)[0]

                for _ in range(2):
                    self.fuel_particles.emmit(
                        position=self.player.local_to_world(
                            (
                                p_shape.get_vertices()[0][0] + self.PLAYER_SIZE,
                                p_shape.get_vertices()[0][1]
                            )
                        ),
                        velocity=-random.uniform(50, 90) *
                                  self.player.rotation_vector.perpendicular(),
                    )

        dt = 1 / FPS
        self.fuel_particles.update()
        self.explosion_particles.update()
        self.space.step(dt)
        self.camera_pos = self.player.position - SCREEN / 2

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        shift = self.camera_pos

        # Desenha o jogador
        transform = self.player.local_to_world
        shape = list(self.player.shapes)[0]
        a, b, c = [transform(v) - shift for v in shape.get_vertices()]
        pyxel.tri(*a, *b, *c, self.PLAYER_COLOR)

        # Desenha as partículas
        self.fuel_particles.draw(shift)
        # Mandamos a posição do jogador no draw porque é a
        # posição mais atual dele
        self.explosion_particles.draw(self.player.position, shift)

        # Desenha a base
        bb: BB = list(self.base.shapes)[0].bb
        x, y = (bb.left, bb.bottom) - shift
        pyxel.rect(x, y, *self.BASE_SHAPE, self.BASE_COLOR)

        # Desenha projéteis
        for shape in self.space.shapes:
            # if isinstance(shape, Circle):
            #     x, y = shape.body.position - shift
            #     r = shape.radius
            #     pyxel.circ(x, y, r, pyxel.COLOR_RED)
            if isinstance(shape, Segment):
                transform = lambda v: shape.body.local_to_world(v) - shift
                a, b = map(transform, (shape.a, shape.b))
                pyxel.line(*a, *b, pyxel.COLOR_WHITE)

        if self.landed:
            msg = "SUCESSO!" if self.victory else "DERROTA..."
            x = WIDTH / 2 - len(msg) * pyxel.FONT_WIDTH / 2
            pyxel.text(x, HEIGHT // 2 - 20, msg, pyxel.COLOR_RED)


game = Game()
pyxel.init(WIDTH, HEIGHT, fps=FPS)
pyxel.mouse(True)
pyxel.run(game.update, game.draw)