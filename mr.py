"""r.py

Usage:
    r.py [--dt=N] [--mouse] [--system] [--path=PATH]

Options:
    -t,--dt=N             the elapsed time in seconds [default: 10.0]
    -m,--mouse         move the mouse in a random fashion
    -s,--system        move the mouse and use the keyboard to interact with the system
    --path=PATH        the initial path to start the search for python code [default: ~]
"""

import os
import time
import random

from typing import Union

import pyautogui as pg
from docopt import docopt


class SystemState:
    DEFAULT_IDLE_DT = 10.0
    SX = 50.0
    SY = 50.0

    def __init__(self, idle_dt=DEFAULT_IDLE_DT):
        self.x = 0
        self.y = 0
        self.t = 0

        self.x0 = 0
        self.y0 = 0
        self.t0 = 0

        self.idle_dt = idle_dt

        self.update()

    @classmethod
    def get_mouse_xy_and_time(cls):
        x, y = pg.position()
        t = time.perf_counter()
        return x, y, t

    def update(self):
        self.x, self.y, self.t = self.get_mouse_xy_and_time()

    def update_0(self, update_t: bool = True):
        self.x0, self.y0, t0 = self.get_mouse_xy_and_time()
        if update_t:
            self.t0 = t0

    def is_idle(self) -> bool:
        self.update()

        dt = self.t - self.t0
        if self.x == self.x0 and self.y == self.y0:
            if dt > self.idle_dt:
                self.update_0()
                return True
        else:
            self.update_0()
        return False

    def mouse_interaction(self):
        w, h = pg.size()
        while True:
            dx = round(random.normalvariate(0.0, self.SX))
            dy = round(random.normalvariate(0.0, self.SY))

            x = self.x + dx
            y = self.y + dy

            if (dx != 0 or dy != 0) and 0 < x < w and 0 < y < h:
                break

        t = random.uniform(0.061, 0.161)
        pg.moveRel(dx, dy, duration=t)

    def select_random_app(self, n: int = 10):
        pg.keyDown("alt")
        for _ in range(random.randint(1, n)):
            pg.press(keys="tab")
            pg.sleep(0.4)
        pg.keyUp("alt")

    def system_interation(self):
        x, y, _ = self.get_mouse_xy_and_time()

        option_list = random.choices(["mouse", "system", "hotkey"], [1, 8, 3])
        option = option_list[0]

        if option == "mouse":
            # try to display menu with right click, move through the items and exit
            pg.rightClick(x=x, y=y, duration=0.1)
            for _ in range(int(random.uniform(5, 20))):
                key_name = random.choices(["down", "up", "left", "right"], [3, 1, 1, 1])
                time.sleep(0.1)
                pg.press(keys=key_name[0])

            time.sleep(0.1)
            pg.press("escape")

        elif option == "system":
            # randomly interact with opened windows
            # pg.leftClick(x=x, y=y, duration=0.1)
            self.select_random_app()

            for _ in range(int(random.uniform(5, 20))):
                key_name = random.choices(["pagedown", "pageup", "up", "down", "left", "right", "home", "end"],
                                          [1, 1, 3, 3, 3, 3, 1, 1])
                time.sleep(0.2)
                pg.press(keys=key_name[0])

        elif option == "hotkey":
            # 1. select a random application
            self.select_random_app()

            # 2. apply a random set of key combinations
            possible_keys = random.choices([
                ["ctrl", "tab"],
                ["ctrl", "win", "u"],
                ["ctrl", "win", "i"],
                ["ctrl", "win", "j"],
                ["ctrl", "win", "k"],
                ["ctrl", "win", "enter"],
                ["ctrl", "win", "e"],
                ["ctrl", "win", "r"],
                ["ctrl", "win", "t"],
                ["ctrl", "win", "d"],
                ["ctrl", "win", "f"],
                ["ctrl", "win", "g"],
            ],
                [
                    35, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5
                ]
            )
            key_combination = possible_keys[0]
            pg.hotkey(*key_combination)


def get_files_iterator(path: str):
    for root, dirs, files in os.walk(path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext == ".py":
                filename = os.path.join(root, file)
                yield filename
        for d in dirs:
            sub_path = os.path.join(root, d)
            get_files_iterator(path=sub_path)


def main(**kwargs: Union[dict, list]):
    """Entry point for the program

    :param kwargs: if provided, is a list of parameters by docopt, otherwise, docopt will take them from sys.argv
    :type kwargs: Dict or List
    """
    args = docopt(doc=__doc__, **kwargs)
    dt = float(args["--dt"])
    path = args["--path"].replace("~", os.environ["HOME"])

    system_state = SystemState(idle_dt=dt)
    for filename in get_files_iterator(path):
        # open the file and read th
        with open(filename) as fp:
            for raw_line in fp.readlines():
                line = raw_line[:-1] if raw_line.endswith("\n") else raw_line
                print(line)
                time.sleep(0.05)

                if system_state.is_idle():
                    if args["--mouse"]:
                        system_state.mouse_interaction()
                    if args["--system"]:
                        system_state.system_interation()


if __name__ == "__main__":
    main()
