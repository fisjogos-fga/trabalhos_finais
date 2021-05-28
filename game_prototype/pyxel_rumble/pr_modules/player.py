import pyxel
import random
from easymunk import Vec2d, PolyBody, Arbiter
from .global_config import GameObject, CollisionType, WIDTH, HEIGHT, FPS
from .anim_dog_moveset import *
from .anim_rabbit_moveset import *
from .sound import *
from .particles import *

class Player (GameObject, PolyBody):
    SPEED = 120
    JUMP_SPEED = 70
    COLOR = pyxel.COLOR_RED
    NUMBER_JUMPS = 3
    DAMAGE_PERCENTAGE = 0

    def __init__(self, x, y, animal, controls, space):
        
        #poly generation
        if (animal == 'dog'):
            poly_vertices = [(2,0), (2,10), (15,10), (15,0)]
        elif (animal == 'rabbit'):
            poly_vertices = [(5,0), (5,7), (15,7), (15,0)]
        else:
            pass
        
        super().__init__(
            mass = 50,
            position = (x,y),
            vertices = poly_vertices,
            elasticity=0.0,
            friction = 1,
            collision_type=CollisionType.PLAYER,
            color = pyxel.COLOR_YELLOW            
        )

        if (animal == 'dog'):
            self.collision_type=CollisionType.PLAYER
        elif (animal == 'rabbit'):
            self.collision_type=CollisionType.PLAYER_2
        else:
            pass

        self.CONTROLS = []
        if (controls == 'WASD'):
            self.CONTROLS = [pyxel.KEY_A, pyxel.KEY_D, pyxel.KEY_W, pyxel.KEY_S]
        elif (controls == 'ArrowKeys'):
            self.CONTROLS = [pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_UP, pyxel.KEY_DOWN]
        else:
            pass
        self.animal = animal
        self.can_jump = False
        self.remaining_jumps = self.NUMBER_JUMPS
        self.particles = Particles(space)

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
        #ESQUERDA E DIREITA
        if pyxel.btn(self.CONTROLS[0]):
            if self.can_jump and self.remaining_jumps > 0:
                v = Vec2d(-self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(-self.SPEED / 2, v.y)
            sfx_player_walk()

        elif pyxel.btn(self.CONTROLS[1]):
            if self.can_jump and self.remaining_jumps > 0:
                v = Vec2d(+self.SPEED, v.y)
            elif v.x <= 0:
                v = Vec2d(+self.SPEED / 2, v.y)
            sfx_player_walk()
        else:
            r = 0.5 if self.can_jump else 1.0
            v = Vec2d(v.x * r, v.y)

        #PULO E DESCER RÁPIDO
        if (pyxel.btnp(self.CONTROLS[2])
            and self.can_jump and self.remaining_jumps > 0 ):
            v = Vec2d(v.x, self.JUMP_SPEED)
            self.remaining_jumps-=1
            sfx_sound_player_jump()
            
        elif(pyxel.btnp(self.CONTROLS[3])
            and self.remaining_jumps < self.NUMBER_JUMPS):
            v = Vec2d(v.x, -self.JUMP_SPEED)

        self.velocity = v

    def draw(self, camera=pyxel):
        vx = self.velocity.x
        vy = self.velocity.y

        x, y, _right, _top = self.bb
        sign = 1 if vx >= 0 else -1
        # u altera horizontalmente a posição nos assets, v altera verticalmente
        
        is_moving = False if ((abs(round(vx, 3)) == 0) and abs(round(vy, 3) == 0)) else True

        rise_threshold = 0.5
        fall_threshold = -0.01
        is_jumping = True if (round(vy, 3) >= rise_threshold)  else False
        
        is_in_the_air = True if (round(vy, 3) < rise_threshold and
                                 round(vy, 3) >= fall_threshold)  else False
        is_falling = True if (round(vy, 3) < fall_threshold) else False

        is_walking = True if (abs(round(vx, 3)) > 0 and 
                             (abs(round(vy, 3)) == 0) and 
                             (pyxel.btn(self.CONTROLS[0]) or pyxel.btn(self.CONTROLS[1]))) else False
        
        # ficar parado (idle)

        if (is_moving == False):
            if(self.animal == 'dog'):
                dog_moveset_anim_idle(camera, x ,y, sign)
            if(self.animal == 'rabbit'):
                rabbit_moveset_anim_idle(camera, x ,y, sign)

        else:
            if(is_walking):
                if(self.animal == 'dog'):
                    dog_moveset_anim_walk(camera, x, y, sign)
                if(self.animal == 'rabbit'):
                    rabbit_moveset_anim_walk(camera, x, y, sign)
            elif(is_jumping):
                self.particles.draw(self.particles.space.camera)
                if(self.animal == 'dog'):
                    dog_moveset_init_jump(camera, x, y, sign)
                if(self.animal == 'rabbit'):
                    rabbit_moveset_init_jump(camera, x, y, sign)
            elif(is_in_the_air):
                if(self.animal == 'dog'):
                    dog_moveset_in_the_air_jump (camera, x, y, sign)
                if(self.animal == 'rabbit'):
                    rabbit_moveset_in_the_air_jump(camera, x, y, sign)
            elif(is_falling):
                if(self.animal == 'dog'):
                    dog_moveset_falling_jump (camera, x, y ,sign)
                if(self.animal == 'rabbit'):
                    rabbit_moveset_falling_jump(camera, x, y, sign)
            else:
                pass

    def register(self, space, message):
        space.add(self)
        
        # para poder pular de novo
        @space.post_solve_collision(CollisionType.PLAYER, CollisionType.PLATFORM)
        def _col_start(arb: Arbiter):

            n = arb.normal_from(self)
            self.can_jump = n.y <= -0.5
            self.remaining_jumps = self.NUMBER_JUMPS
            self.particles.emmit(self.position, self.velocity)

        # para garantir que o jogador pula
        @space.separate_collision(CollisionType.PLAYER, CollisionType.PLATFORM)
        def _col_end(arb: Arbiter):
            self.can_jump = False if self.remaining_jumps == 0 else True
            self.particles.emmit(self.position, self.velocity)

       
        # para analisar colisão entre jogadores (PLAYER 2 TRAVA DEMAIS)
        @space.post_solve_collision(CollisionType.PLAYER, CollisionType.PLAYER)
        def _col_start(arb: Arbiter):
            print('\n\n\n\OOF\n\n\n')

