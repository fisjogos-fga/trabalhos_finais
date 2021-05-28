from .game import Game
import pyxel
from .pr_modules import global_config as config

def run():
    pyxel.init(config.WIDTH, config.HEIGHT)
    pyxel.mouse(True)
    game = Game()
    pyxel.run(game.update, game.draw)
