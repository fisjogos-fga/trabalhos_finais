import pyxel 

#IDLE
def dog_moveset_anim_idle (camera, x, y, sign):
    # numero de frames contados de todas as animações de idle
    abana = [0 for _ in range(0, 10, 1)]
    abana_pisca = [1 for _ in range(0, 10, 1)]
    pisca = [2 for _ in range(0, 9, 1)]
    parado = [-1 for _ in range(0, 20, 1)]
    # sequência pré-definida
    anim = abana + parado + pisca + parado + abana + abana_pisca
    anim_counter = int(pyxel.frame_count) % len(anim)

    #animação
    idle_anim_selected = anim[anim_counter]
    if (idle_anim_selected in [0, 1]):
        # abana rabo (0), abana rabo e pisca (1)
        idx = int(pyxel.frame_count//2) % 6
        u = 16 * idx
        v = 16 * idle_anim_selected
        camera.blt(x, y, 0, u, v, sign * 16, 16, pyxel.COLOR_GREEN)
    elif (idle_anim_selected == 2):
        # só pisca o olho (2)
        idx = int(pyxel.frame_count//3) % 3
        u = 16 * idx
        v = 16 * idle_anim_selected
        camera.blt(x, y, 0, u, v, sign * 16, 16, pyxel.COLOR_GREEN)
    elif (idle_anim_selected == -1):
        # parado (-1)
        camera.blt(x, y, 0, 0, 0, sign * 16, 16, pyxel.COLOR_GREEN)
    else:
        pass

# WALK
def dog_moveset_anim_walk (camera, x, y, sign):
    # numero de frames contados de todas as animações de andar
    anda = [3 for _ in range(0, 8, 1)]
    # sequência pré-definida
    anim = anda
    anim_counter = int(pyxel.frame_count) % len(anim)
    
    # andando (3)
    walk_anim_selected = anim[anim_counter]
    idx = int(pyxel.frame_count//2) % 5
    u = 16 * idx
    v = 16 * walk_anim_selected
    camera.blt(x, y, 0, u, v, sign * 16, 16, pyxel.COLOR_GREEN)

#JUMP
def dog_moveset_init_jump (camera, x, y, sign):
    jump_anim_selected = 4
    idx = 0
    u = 16 * idx
    v = 16 * jump_anim_selected
    camera.blt(x, y, 0, u, v, sign * 16, 16, pyxel.COLOR_GREEN)

def dog_moveset_in_the_air_jump (camera, x, y, sign):
    jump_anim_selected = 4
    idx = 1
    u = 16 * idx
    v = 16 * jump_anim_selected
    camera.blt(x, y, 0, u, v, sign * 16, 16, pyxel.COLOR_GREEN)

def dog_moveset_falling_jump (camera, x, y, sign):
    jump_anim_selected = 4
    idx = 2
    u = 16 * idx
    v = 16 * jump_anim_selected
    camera.blt(x, y, 0, u, v, sign * 16, 16, pyxel.COLOR_GREEN)