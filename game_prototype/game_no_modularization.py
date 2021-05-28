import enum
from typing import Callable
from abc import ABC, abstractmethod
import pyxel
from easymunk import Vec2d, Arbiter, CircleBody, Space, march_string
from easymunk import pyxel as phys


#game window
WIDTH, HEIGHT = 256, 196

SCENARIO = """
|
|
|
|
|
|
|
| 
|
|
|X
|X
|===============
"""

class GameState (enum.IntEnum):
    MENU = 1
    CHAR_SELECT = 2
    GAMEPLAY = 3
    RESULTS = 4
    
class CollisionType(enum.IntEnum):
    PLAYER = 1
    PLATFORM = 2

class HitboxType(enum.IntEnum):
    HURTBOX = 0
    ATTACK = 1 # longo e curto alcance
    SHIELD = 2

class GameObject(ABC):
    @abstractmethod
    def update(self):
        ...
    
    @abstractmethod
    def draw(self):
        ...

    @abstractmethod
    def register(self, space: Space, message: Callable[[str, "GameObject"], None]):
        ...

#=================================================

class Player (GameObject, CircleBody):
    SPEED = 90
    JUMP_SPEED = 120
    COLOR = pyxel.COLOR_RED
    NUMBER_JUMPS = 2

    def __init__(self, x, y):
        super().__init__(
            radius=4,
            position=(x, y),
            elasticity=0.1,
            collision_type=CollisionType.PLAYER,
        )
        self.can_jump = False
        self.remaining_jumps = self.NUMBER_JUMPS

    def update(self):
        v = self.velocity
        mass = self.mass
        F = mass * 200
        self.force += Vec2d(0, -mass * 200)

        # Resetar o jogador
        if pyxel.btnp(pyxel.KEY_R):
            self.body.position = (WIDTH/2, HEIGHT/2)
            v = Vec2d(0,0)
        
        # Controles
        if pyxel.btn(pyxel.KEY_LEFT):
            if self.can_jump and self.remaining_jumps > 0:
                v = Vec2d(-self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(-self.SPEED / 2, v.y)
        elif pyxel.btn(pyxel.KEY_RIGHT):
            if self.can_jump and self.remaining_jumps > 0:
                v = Vec2d(+self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(+self.SPEED / 2, v.y)
        else:
            r = 0.5 if self.can_jump else 1.0
            v = Vec2d(v.x * r, v.y)

        if (pyxel.btnp(pyxel.KEY_UP)
            and self.can_jump and self.remaining_jumps > 0 ):
            v = Vec2d(v.x, self.JUMP_SPEED)
            self.remaining_jumps-=1
        elif(pyxel.btnp(pyxel.KEY_DOWN)
            and self.remaining_jumps < self.NUMBER_JUMPS):
            v = Vec2d(v.x, -self.JUMP_SPEED)

        self.velocity = v

    def draw(self, camera=pyxel):
        x, y, _right, _top = self.bb
        sign = 1 if self.velocity.x >= 0 else -1

        idx = int(self.position.x / 2) % 3
        u = 8 * idx
        camera.blt(x, y, 0, u, 0, sign * 8, 8, pyxel.COLOR_YELLOW)

    def register(self, space, message):
        space.add(self)

        @space.post_solve_collision(CollisionType.PLAYER, ...)
        def _col_start(arb: Arbiter):
            n = arb.normal_from(self)
            self.can_jump = n.y <= -0.5
            self.remaining_jumps = self.NUMBER_JUMPS

        @space.separate_collision(CollisionType.PLAYER, ...)
        def _col_end(arb: Arbiter):
            self.can_jump = False if self.remaining_jumps == 0 else True

#=================================================

class Game:
    # Cores
    
    # Outras propriedades
    CAMERA_TOL = Vec2d(WIDTH / 2 - 64, HEIGHT / 2 - 48)
    N_ENEMIES = 20

    def __init__(self, scenario=SCENARIO):
        self.paused = False
        self.camera = phys.Camera(flip_y=True)
        self.space = phys.space(
            gravity=(0, -25),
            wireframe=True,
            camera=self.camera,
            elasticity=1.0,
        )

        # Inicializa o jogo
        self.state = GameState.GAMEPLAY
        pyxel.load("resources/assets.pyxres")

        pyxel.cls(pyxel.COLOR_LIGHTBLUE)

        # Cria jogador
        self.player = Player(50, 50)
        self.player.register(self.space, self.message)

        # Cria chão
        f = phys.rect(0, 0, 1000, 48, body_type="static")

        # Cria margens
        phys.margin(0, 0, 1000, HEIGHT)

    def message(self, msg, sender):
        fn = getattr(self, f'handle_{msg}', None)
        if fn is None:
            print(f'Mensagem desconhecida: "{msg} ({sender})')
        else:
            fn(sender)

    def draw(self):
        pyxel.cls(pyxel.COLOR_LIGHTBLUE)
        for body in self.space.bodies:
            if isinstance(body, (Player)):
                body.draw(self.camera)
            else:
                self.camera.draw(body)

        # Desenha texto informativo
        pyxel.text(5, 5, "Setas para controlar o personagem (ele tem 3 pulos)\nR para resetar", pyxel.COLOR_BLACK)
        info_text = "Posicao: (" + str(round(self.player.position[0], 3)) + ", " + str(round(self.player.position[1], 3)) + ")\n" +                    "Velocidade: (" + str(round(self.player.velocity.x, 3)) + ", " + str(round(self.player.velocity.y, 3)) + ")\n" + "Pulos Restantes: " + str(self.player.remaining_jumps)
        pyxel.text(5, 30, info_text, pyxel.COLOR_BLACK)

        msg = ""
        if self.paused:
            msg = 'PAUSED'

        if msg:
            x = (WIDTH - len(msg) * pyxel.FONT_WIDTH) / 2
            pyxel.text(round(x), HEIGHT // 2, msg, pyxel.COLOR_RED)
    def handle_hit_player(self, sender):
        self.state = GameState.GAMEPLAY

    def handle_hit_target(self, sender):
        self.state = GameState.GAMEPLAY

    def update(self):

        if (pyxel.btnp(pyxel.KEY_P)):
            self.paused = False if self.paused else True
        if not self.paused:
            self.space.step(1 / 30, 2)
        self.player.update()
        self.camera.follow(self.player.position, tol=self.CAMERA_TOL)

#=================================================

pyxel.init(WIDTH, HEIGHT)
pyxel.mouse(True)
game = Game()
pyxel.run(game.update, game.draw)