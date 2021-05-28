
#
# Jogos de plataforma
#
import random
from typing import Callable
from abc import ABC, abstractmethod
import enum
from easymunk import Body as BodyShape
from easymunk import Poly
import pyxel
from easymunk import Vec2d, Arbiter, CircleBody, Space, march_string, ShapeFilter,BB, Body
from easymunk import pyxel as phys

WIDTH, HEIGHT = 256, 196
SCENARIO = """
|
|
|
|
|                                              =
|                                              ==
|                     ===                      ===
|                                              ====
|            ===   ===             ===         =====
|                                  ===
|=====    ===                      ===
|X
|X
"""
HUNTED = 0

class ColType(enum.IntEnum):
    PLAYER = 1
    ENEMY = 2
    TARGET = 3


class GameState(enum.IntEnum):
    RUNNING = 1
    GAME_OVER = 2
    HAS_WON = 3


class BadToy(ABC):
    @abstractmethod
    def update(self):
        ...
    
    @abstractmethod
    def draw(self):
        ...

    @abstractmethod
    def register(self, space: Space, message: Callable[[str, "BadToy"], None,]):
        space.add(self)
        
        
        @space.begin_collision(ColType.PLAYER, ColType.ENEMY)
        
        def begin(arb: Arbiter, normal= 0):
            
            shape_a, shape_b = arb.shapes
            if shape_a.collision_type == ColType.PLAYER:
                player, badtoy = shape_a, shape_b
            else:
                player, badtoy = shape_b, shape_b

            n = arb.normal_from(player)
            if n.y < normal:
                space.remove(badtoy)
                print("o player bateu no brinquedo do mal")
                global HUNTED
                HUNTED += 1
                
            else:
                message("hit_player", sender=self)
                print("bateu no player")

            return True

class Particles:
    def __init__(self, space):
        self.particles = []
        self.space = space

    def draw(self, camera=pyxel):
        for p in self.particles.copy():
            x, y = p.position
            if random.random() < 0.15:
                camera.rect(x, y, 3, 3, pyxel.COLOR_WHITE)
            else:
                camera.pset(x, y, pyxel.COLOR_WHITE)

    def update(self):
        for p in self.particles.copy():
            p.velocity = p.velocity.rotated(random.uniform(-5, 5)) 
            p.duration -= 1
            if p.duration <= 0:
                self.particles.remove(p)
                self.space.remove(p)
    def emmit(self, position, velocity):
        p = self.space.create_circle(
            radius=1,
            mass=0.1,
            moment=float("inf"),
            position=position,
            velocity=velocity,
            filter=ShapeFilter(group=1),
        )
        p.duration = 20-random.uniform(0,5) 
        p.velocity_func = self.update_velocity
        self.particles.append(p)

    def update_velocity(self, body, gravity, damping, dt):
        body.update_velocity(body, -gravity / 2, 0.99, dt)



class Player( CircleBody,):
    SPEED = 90
    JUMP_SPEED = 120
    COLOR = pyxel.COLOR_RED
    

    def __init__(self, x, y,space,camera):
        super().__init__(
            radius=4,
            position=(x, y),
            elasticity=0.0,
            collision_type=ColType.PLAYER,
            filter = ShapeFilter(group = 1)
        )
        self.can_jump = False
        self.particles = Particles(space)
        self.camera =camera
        
    

    def update(self,):
        v = self.velocity
        mass = self.mass
        F = mass * 200
        self.force += Vec2d(0, -mass * 200)

        if pyxel.btn(pyxel.KEY_LEFT):
            if self.can_jump:
                v = Vec2d(-self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(-self.SPEED / 2 / 2, v.y)
        elif pyxel.btn(pyxel.KEY_RIGHT):
            if self.can_jump:
                v = Vec2d(+self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(+self.SPEED / 2, v.y)
        else:
            r = 0.5 if self.can_jump else 1.0
            v = Vec2d(v.x * r, v.y)

        if self.can_jump and pyxel.btnp(pyxel.KEY_UP):
            v = Vec2d(v.x, self.JUMP_SPEED)
            for _ in range(4):
                self.particles.emmit(position = (self.position.x + random.uniform(-4,8),self.position.y), velocity = (5,-40))
           

        self.velocity = v
        self.particles.update()

    def draw(self, camera=pyxel):
        x, y, _right, _top = self.bb
        sign = -1 if self.velocity.x >= 0 else 1
        

        idx = int(self.position.x / 5) % 3
        u = 16 * idx

        self.particles.draw(self.camera)
              
        if not self.can_jump:
            if self.velocity.y <0 :
                camera.blt(x, y, 0, 16,16, sign*16,16, pyxel.COLOR_NAVY)
                
            if self.velocity.y >0:
                camera.blt(x, y, 0, 0,16, sign*16,16, pyxel.COLOR_NAVY)

        else:
            camera.blt(x, y, 0, u,0, sign*16,16, pyxel.COLOR_NAVY)

    def register(self, space, message):
        space.add(self)
        print("player add no space")

        @space.post_solve_collision(ColType.PLAYER, ...)
        def _col_start(arb: Arbiter):
            n = arb.normal_from(self)
            self.can_jump = n.y <= -0.5

        @space.separate_collision(ColType.PLAYER, ...)
        def _col_end(arb: Arbiter):
            self.can_jump = False

        @space.begin_collision(ColType.PLAYER, ColType.TARGET)
        def _game_end(arb: Arbiter):
            message("hit_target", sender=self)
            return False


class Enemy(BadToy, CircleBody):
    SPEED = 90
    OSSOSHAPE = [(0,0),(16,0),(16,8),(0,8)]
    @staticmethod
    def random(xmin, xmax, ymin, ymax):
        vx = random.uniform(-Enemy.SPEED / 3, Enemy.SPEED / 3)
        vy = random.uniform(0, Enemy.SPEED / 3)
        return Enemy(
            x=random.uniform(xmin + 16, xmax - 16),
            y=random.uniform(ymin + 8, ymax - 8),
            velocity=(vx, vy),
            angular_velocity=random.uniform(-360, 360),
        )

    def __init__(self, x, y, **kwargs):
        super().__init__(
            # shape= self.OSSOSHAPE,
            radius = 8,
            position=(x, y),
            friction=0.0,
            elasticity=1.0,
            collision_type=ColType.ENEMY,
            **kwargs,
        )
        self.shape.filter =ShapeFilter(group = 2)

    def update(self):
        ...

    def draw(self, camera=pyxel):
        x, y, _right, _top = self.bb
        camera.blt(x, y, 0, 0,112, 16,8, pyxel.COLOR_NAVY)        

    def register(self, space, message):
        BadToy.register(self,space, message)
        
class Dinossauro(BadToy, BodyShape):
    SPEED = 80
    DINOVERT = [(0,0),(16,0),(16,15),(12,15),(0,4)]

    def __init__(self, a, b,camera,**kwargs):
        super().__init__(
            mass= 100000,
            moment= float("inf"),
            position=(a, 50),
            
            **kwargs,
        )
        self.shape = Poly(self.DINOVERT,0,body= self,collision_type = ColType.ENEMY,)
        self.shape.filter =ShapeFilter(group = 2)
        self.a = a
        self.b = b
        self.camera =camera
        self.sentido = 0

    def update(self):
        v = self.velocity 
        mass = self.mass
        F = mass * 200
        self.force += Vec2d(0, -F)
        
        if (self.position.x <= self.a):
            self.sentido = 0
        if (self.position.x >= self.b):
            self.sentido = 1
        if (self.sentido == 0):
            v = Vec2d(+self.SPEED, 0)
            
        if (self.sentido == 1 ):
            v = Vec2d(-self.SPEED, 0)
        
        self.velocity = v

    def draw(self, camera=pyxel):
        x, y, _right, _top = self.bb
        
        sign = -1 if self.velocity.x >= 0 else 1

        idx = int(self.position.x / 5) % 3
        
        u = 32 + (16 * idx)
        
        camera.blt(x, y, 0, u,112, -sign*16,16, pyxel.COLOR_NAVY)

    def register(self, space, message):
        BadToy.register(self,space, message)
        
class Fase1:
    # Cores

    # Outras propriedades
    CAMERA_TOL = Vec2d(WIDTH / 2 - 64, HEIGHT / 2 - 48)
    N_ENEMIES = 10

    def __init__(self, scenario=SCENARIO):
        self.camera = phys.Camera(flip_y=True)
        self.space = phys.space(
            gravity=(0, -25),
            wireframe=True,
            camera=self.camera,
            elasticity=1.0,
        )
        
        # Inicializa o jogo
        self.state = GameState.RUNNING
        pyxel.load("Kinder_Hunter.pyxres")

        # Cria jogador
        self.player = Player(50, 50,self.space,self.camera)
        self.player.register(self.space, self.message)

        # Cria dinossauro
        self.dinossauros = []
        for i in range (3):
            part = Dinossauro(200*(i+1),200*(i+2),camera =self.camera)
            part.register(self.space,self.message)
            self.dinossauros.append(part)

        # Cria chão
        floor = phys.rect(0, 0, 1000, 48, body_type="static",col= pyxel.COLOR_BLACK)

        # Cria cenário
        for line in march_string(
            scenario, "=", scale=6.0, translate=Vec2d(0.0, 48), flip_y=True
        ):
            line = [Vec2d(2 * x, y) for (x, y) in line]
            phys.poly(line, body_type="static", color=pyxel.COLOR_PEACH)

        # Cria sensor para condição de vitória
        phys.rect(
            1000 - 16,
            48,
            16,
            16,
            collision_type=ColType.TARGET,
            sensor=True,
            body_type="static",
        )

        # Cria margens
        phys.margin(0, 0, 1000, HEIGHT)

        # Cria inimigos
        for _ in range(self.N_ENEMIES):
            enemy = Enemy.random(0, 1000, HEIGHT / 2, HEIGHT)
            enemy.register(self.space, self.message)

    def message(self, msg, sender):
        fn = getattr(self, f'handle_{msg}', None)
        if fn is None:
            print(f'Mensagem desconhecida: "{msg} ({sender})')
        else:
            fn(sender)

    def handle_hit_player(self, sender):
        self.state = GameState.GAME_OVER
        

    def handle_hit_target(self, sender):
        self.state = GameState.HAS_WON

    def draw(self):
        global HUNTED
        b = str(HUNTED)
        a = pyxel.FONT_WIDTH * 8
        pyxel.cls(pyxel.COLOR_NAVY)
        pyxel.text(50,10,"HUNTED: ", pyxel.COLOR_WHITE )
        pyxel.text( a + 50, 10, b, pyxel.COLOR_WHITE)
        for body in self.space.bodies:
            if isinstance(body, (Player, Enemy, Dinossauro)):
                body.draw(self.camera)
            else:
                self.camera.draw(body)
        

        msg = ""
        if self.state is GameState.GAME_OVER:
            msg = "hit_player"
            pyxel.cls(pyxel.COLOR_BLACK)
            x = (WIDTH - 9 * pyxel.FONT_WIDTH) / 2
            pyxel.text(round(x), HEIGHT // 2, "GAME OVER", pyxel.COLOR_YELLOW)
            
        elif self.state is GameState.HAS_WON:
            msg = "hit_target"
            pyxel.cls(pyxel.COLOR_PINK)
            x = (WIDTH - 11 * pyxel.FONT_WIDTH) / 2
            pyxel.text(round(x), HEIGHT // 2, "MANDOU BEM!", pyxel.COLOR_BLACK)


    def update(self):
        
        if self.state is GameState.RUNNING:
            self.player.update()
            for item in self.dinossauros.copy():
                item.update()
            self.space.step(1 / 30, 2)
       
    
        vx, vy = self.player.velocity
        self.camera.offset += (vx/20, vy/50 ) 
        self.camera.follow(self.player.position, tol=self.CAMERA_TOL)
        
        



pyxel.init(WIDTH, HEIGHT)
pyxel.mouse(True)
game1 = Fase1()
pyxel.run(game1.update, game1.draw)

