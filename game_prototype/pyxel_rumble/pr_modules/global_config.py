import enum
from typing import Callable
from abc import ABC, abstractmethod
from easymunk import Space
import pyxel

#game window
WIDTH, HEIGHT = 256, 196
FPS = 30
BACKGROUND_COLOR = pyxel.COLOR_BLACK
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
    PLAYER_2 = 2
    BALL = 3
    PLATFORM = 4

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