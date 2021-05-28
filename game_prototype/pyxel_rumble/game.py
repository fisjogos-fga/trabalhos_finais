from .pr_modules.platform import Ground
from .pr_modules.obj_ball import Ball
from .pr_modules.player import Player
from .pr_modules.global_config import *
import pyxel
from easymunk import Vec2d
from easymunk import pyxel as phys
from .pr_modules.sound import music_bgm

class Game:

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
        pyxel.load("pr_resources/assets1.pyxres")

        pyxel.cls(BACKGROUND_COLOR)
        
        # Cria jogadores
        self.player1 = Player(50, 50, 'dog', 'ArrowKeys', self.space)
        self.player1.register(self.space, self.message)
        
        #self.player2 = Player(80, 50, 'rabbit', 'WASD')
        #self.player2.register(self.space, self.message)

        self.ball = Ball(50, 150, self.space)
        self.ball.register(self.space, self.message)
        # Cria chão
        f = Ground()

        # Cria margens
        phys.margin(0, 0, WIDTH - 30, HEIGHT,
            elasticity = 1,
            friction = 1)

        # Toca música
        music_bgm()

    def message(self, msg, sender):
        fn = getattr(self, f'handle_{msg}', None)
        if fn is None:
            print(f'Mensagem desconhecida: "{msg} ({sender})')
        else:
            fn(sender)

    def draw(self):
        
        pyxel.cls(BACKGROUND_COLOR)

    
        for body in self.space.bodies:
            if isinstance(body, (Player)):
                body.draw(self.camera)
            else:
                self.camera.draw(body)

        # Desenha texto informativo
        pyxel.text(10, 5, "Setas para controlar o personagem (ele tem 3 pulos)\nR para resetar", pyxel.COLOR_YELLOW)
        info_text = "Posicao: (" + str(round(self.player1.position[0], 3)) + ", " + str(round(self.player1.position[1], 3)) + ")\n" +                    "Velocidade: (" + str(round(self.player1.velocity.x, 3)) + ", " + str(round(self.player1.velocity.y, 3)) + ")\n" + "Pulos Restantes: " + str(self.player1.remaining_jumps) + "\nScore: " + str(self.ball.SCORE)
        pyxel.text(10, 30, info_text, pyxel.COLOR_YELLOW)

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
            self.space.step(1 / FPS, 2)
        self.player1.update()
        #self.player2.update()
        self.ball.update()
        self.camera.follow(self.player1.position, tol=self.CAMERA_TOL)
