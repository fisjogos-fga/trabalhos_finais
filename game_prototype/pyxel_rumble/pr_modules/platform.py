from easymunk import pyxel as phys
from .global_config import *

class Ground (GameObject):
    def __init__(self):
        self.platform_body = phys.rect(
            x = 0,
            y = 0,
            w = WIDTH - 30,
            h = 48,
            body_type = 'static'
        )
        self.platform_body.collision_type = CollisionType.PLATFORM
        self.platform_body.friction = 1
    
    def update(self):
        ...
    
    def draw(self):
        ...
    
    def register(self, space: Space, message: Callable[[str, "GameObject"], None]):
        space.add(self.platform_body)