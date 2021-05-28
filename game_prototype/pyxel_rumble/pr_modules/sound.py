import pyxel
import random

def sfx_sound_player_jump():
    return pyxel.play(ch=3, snd=0, loop=False)

def sfx_player_ball_score():
    return pyxel.play(ch=3, snd=1, loop=False)

def sfx_player_walk():
    snd_select = random.uniform(2,3)
    return pyxel.play(ch=3, snd=snd_select, loop=False)

def sfx_ball_touch_floor():
    return pyxel.play(ch=3, snd=4, loop=False)

def music_bgm():
    return pyxel.playm(0, loop=True)