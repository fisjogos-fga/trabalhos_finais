import pyxel
from constants import WIDTH
from _enum import DifficultyOptions


class Menu:
    def __init__(self):
        self.selected_difficulty = DifficultyOptions.easy
        self.done = False

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        title = "Kill the Ninjas!"
        intro_text = "Choose difficulty and press space"

        pyxel.text(
            WIDTH / 2 - 2 * len(title),
            20,
            title,
            pyxel.COLOR_YELLOW
        )

        initial_y = 60

        offset = 10

        pyxel.text(
            WIDTH / 2 - 2 * len(intro_text),
            initial_y,
            intro_text,
            pyxel.COLOR_YELLOW
        )

        for index, option in enumerate(DifficultyOptions):
            offset += 20
            selection_text = "> " if self.selected_difficulty == option else ""

            name = selection_text + option.name

            pyxel.text(
                WIDTH / 2 - 33 - 5 * len(selection_text),
                initial_y + offset,
                name,
                pyxel.COLOR_YELLOW
            )

    def update(self):
        options = list(DifficultyOptions)
        select_index = options.index(self.selected_difficulty)

        if pyxel.btnp(pyxel.KEY_UP):
            select_index = max(select_index - 1, 0)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            select_index = min(
                select_index + 1,
                len(list(DifficultyOptions)) - 1
            )

        self.selected_difficulty = options[select_index]

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.done = True
