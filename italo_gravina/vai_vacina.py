#
# Jogos de plataforma
#
from random import *

import random
from typing import Callable
from abc import ABC, abstractmethod
import enum
import pyxel
from easymunk import Vec2d, Arbiter, CircleBody, Space, march_string, ShapeFilter,BB
from easymunk import pyxel as phys
from math import copysign

W, H = 256, 256
L = 5000
r = 100
SCENARIO = """
|                                               =
|                                                   =
|                                                       =
|                                                           =
|                                                        =
|                                                  =    =
|                                    =   =   =   ==   =   =   =        
|                                              
|           ====                       
|=============                            
|
|            =  =  =  =  =  =  =  =  =  =  =  =  =                                                           
|            =             =             =        =       =
|     =       
|
|   =           =      =            =            =    =
|                  
|=
|       =        = =             =             = =             =
|               
|    =                                                    =
|       =          =       =         =        =    
|            =                                                =                   
|
|=   =                =     =               =        
|       =             
|
|           =          =           =     =     
|                         
|=
|           =           = =     =       = =    
| =                        
|
|   =      =               =      =    =  
|                         
|=
|                         ==      ==     
|                         
|
|                           ==  ==    
|                           
|                                                  
|                             ==         
|
|X                                                          
|X                              
"""


class ColType(enum.IntEnum):
    PLAYER = 1
    ENEMY = 2
    TARGET = 3


class GameState(enum.IntEnum):
    RUNNING = 1
    GAME_OVER = 2
    HAS_WON = 3


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

class Particles:
    def __init__(self, space):
        self.particles = []
        self.space = space

    def draw(self, camera=pyxel):
        for p in self.particles:
            x, y = p.position
            if random.random() < 0.15:
                camera.rect(x, y, 2, 2, pyxel.COLOR_BLACK)
            else:
                camera.pset(x, y, pyxel.COLOR_BLACK)

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



class Player(GameObject, CircleBody,):
    SPEED = 90
    JUMP_SPEED = 120
    COLOR = pyxel.COLOR_RED
    

    def __init__(self, x, y,space,camera):
        super().__init__(
            radius=7,
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
                camera.blt(x, y, 0, 16,16, sign*16,16, pyxel.COLOR_BLACK)
                
            if self.velocity.y >0:
                camera.blt(x, y, 0, 0,16, sign*16,16, pyxel.COLOR_BLACK)

        else:
            camera.blt(x, y, 0, u,0, sign*16,16, pyxel.COLOR_BLACK)

    def register(self, space, message):
        space.add(self)

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


class Enemy(GameObject, CircleBody):
    SPEED = 90
    
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

    def __init__(self, x, y=H, **kwargs):
        super().__init__(
            radius = 10,
            position=(x, y),
            friction=0.0,
            elasticity=1.0,
            collision_type=ColType.ENEMY,
            **kwargs,
        )
        

    def update(self):
        ...

    def draw(self, camera=pyxel):
        x, y, _right, _top = self.bb
        camera.blt(x, y, 0, 0,112, 16,8, pyxel.COLOR_BLACK)        

    def register(self, space, message):
        space.add(self)

        @space.begin_collision(ColType.PLAYER, ColType.ENEMY)
        def begin(arb: Arbiter):
            shape_a, shape_b = arb.shapes
            if shape_a.collision_type == ColType.PLAYER:
                player, enemy = shape_a, shape_b
            else:
                player, enemy = shape_b, shape_b

            n = arb.normal_from(player)
            if n.y < 0.25:
                space.remove(enemy)
            else:
                message("hit_player", sender=self)

            return True
                

class Game:
    # Cores

    # Outras propriedades
    CAMERA_TOL = Vec2d(W / 2 - 64, H / 2 - 48)
    
    N_INIM = 35

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
        pyxel.load("Brasileiro.pyxres")

        # Cria jogador
        self.player = Player(50, 50,self.space,self.camera)
        self.player.register(self.space, self.message)

        # Cria chão
        
        phys.margin(-L, 0, 2 * 100, 500, elasticity=0, radius=r, color=pyxel.COLOR_BROWN)

        
        for _ in range(150):
            x = random.uniform(-L + 100, L - 100)
            w = random.uniform(100, 1000)
            w_ = random.uniform(100, 1000)
            h = random.uniform(100, 80)
            phys.tri(x, 2, x + w + w_, 2, x + w,2 + h, body_type="static", color=pyxel.COLOR_BROWN)
        

        # Cria cenário
        for line in march_string(
            scenario, "=", scale=8.0, translate=Vec2d(0.0, 48), flip_y=True
        ):
            line = [Vec2d(2 * x, y) for (x, y) in line]
            phys.poly(line, body_type="static", color=pyxel.COLOR_BROWN)

        # Cria sensor para condição de vitória
        phys.rect(
            randint(100,655),
            randint(150,255),
            8,
            8,
            collision_type=ColType.TARGET,
            radius=10,
            sensor=True,
            body_type="static",
        )

        

        # Cria inimigos
        for _ in range(self.N_INIM):
            enemy = Enemy.random(0, 1000, H / 2, H)
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
        pyxel.cls(pyxel.COLOR_CYAN)
        for body in self.space.bodies:
            if isinstance(body, (Player, Enemy)):
                body.draw(self.camera)
            else:
                self.camera.draw(body)
        

        msg = ""
        if self.state is GameState.GAME_OVER:
            msg = "BRASILEIRO MORREU"
        elif self.state is GameState.HAS_WON:
            msg = "BRASILEIRO ACHOU A VACINA! PRECIONE ESC PARA SAIR"

        if msg:
            x = (W - len(msg) * pyxel.FONT_WIDTH) / 2
            pyxel.text(round(x), H // 2, msg, pyxel.COLOR_YELLOW)

    def update(self):

        if self.state is not GameState.GAME_OVER :
            self.player.update()
        vx, vy = self.player.velocity
        self.camera.offset += (vx/20, vy/50 ) 
        self.camera.follow(self.player.position, tol=self.CAMERA_TOL)
        
        self.space.step(1 / 30, 2)



pyxel.init(W, H)
pyxel.mouse(True)
game = Game()
pyxel.run(game.update, game.draw)

