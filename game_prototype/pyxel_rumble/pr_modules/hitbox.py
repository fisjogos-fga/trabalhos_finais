from easymunk import BB
from easymunk.linalg.vec2d import Vec2d
from easymunk import Body, BB

class Hitbox ():

    def __init__(self, x, y, hitbox_type, damage_percentage, knockback_angle, mass, knockback_intensity = 0.1) -> None:
        self.hitbox_type = hitbox_type
        self.knockback_angle = knockback_angle % 360 # será que, ao invés de usar Vec2d, eu n uso o formato polar n? mais fácil. Pq é intensidade e o ângulo. Ou posso achar os valores de Vec2d usando [cos(angulo), sin(angulo)]. Mais fácil ainda. Aí é só multiplicar pela intensidade e pela porcentagem de dano
        self.knockback = knockback_intensity * damage_percentage * mass
        # vou usar bodies invisíveis com BB pra fazer as hitboxes. Assim, posso deletar os "bodies" que são hitboxes dentro de X frames, com configurações específicas de knockback. Aí, configuro isso na classe moveset, que é filha de dog, que é filha de character. (como que vamos ligar character com player???)

    def update (self):
        pass

    def register(self):
        pass

    def draw(self):
        pass