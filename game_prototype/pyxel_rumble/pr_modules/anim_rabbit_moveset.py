import pyxel 

#IDLE
def rabbit_moveset_anim_idle (camera, x, y, sign):
    # numero de frames contados de todas as animações de idle
    mexe = [0 for _ in range(0, 15, 1)]
    pisca = [1 for _ in range(0, 10, 1)]
    parado = [-1 for _ in range(0, 20, 1)]
    # sequência pré-definida
    anim = mexe + pisca + parado + parado + pisca + parado + parado + pisca
    anim_counter = int(pyxel.frame_count) % len(anim)

    #animação
    idle_anim_selected = anim[anim_counter]
    if (idle_anim_selected in [0]):
        # mexe
        idx = int(pyxel.frame_count//6) % 2
        u = 16 * idx
        v = 16 * idle_anim_selected
        camera.blt(x, y, 1, u, v, sign * 16, 16, pyxel.COLOR_GREEN)
    elif (idle_anim_selected == 1):
        # só pisca o olho (2)
        idx = int(pyxel.frame_count//3) % 3
        u = 16 * idx
        v = 16 * idle_anim_selected
        camera.blt(x, y, 1, u, v, sign * 16, 16, pyxel.COLOR_GREEN)
    elif (idle_anim_selected == -1):
        # parado (-1)
        camera.blt(x, y, 1, 0, 0, sign * 16, 16, pyxel.COLOR_GREEN)
    else:
        pass

# WALK
def rabbit_moveset_anim_walk (camera, x, y, sign):
    # numero de frames contados de todas as animações de andar
    anda = [2 for _ in range(0, 6, 1)]
    # sequência pré-definida
    anim = anda
    anim_counter = int(pyxel.frame_count) % len(anim)
    
    # andando (2)
    walk_anim_selected = anim[anim_counter]
    idx = int(pyxel.frame_count//2) % 6
    u = 16 * idx
    v = 16 * walk_anim_selected
    camera.blt(x, y, 1, u, v, sign * 16, 16, pyxel.COLOR_GREEN)

#JUMP
def rabbit_moveset_init_jump (camera, x, y, sign):
    jump_anim_selected = 3
    idx = 0
    u = 16 * idx
    v = 16 * jump_anim_selected
    camera.blt(x, y, 1, u, v, sign * 16, 16, pyxel.COLOR_GREEN)

def rabbit_moveset_in_the_air_jump (camera, x, y, sign):
    jump_anim_selected = 3
    idx = 1
    u = 16 * idx
    v = 16 * jump_anim_selected
    camera.blt(x, y, 1, u, v, sign * 16, 16, pyxel.COLOR_GREEN)

def rabbit_moveset_falling_jump (camera, x, y, sign):
    jump_anim_selected = 3
    idx = 2
    u = 16 * idx
    v = 16 * jump_anim_selected
    camera.blt(x, y, 1, u, v, sign * 16, 16, pyxel.COLOR_GREEN)