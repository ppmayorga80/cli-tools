"""r.py

Usage:
    r.py [--dt=N] [--path=PATH]

Options:
    --dt=N             the elapsed time in seconds [default: 10.0]
    --path=PATH        the initial path to start the search for python code [default: ~]
"""

import os
import time
import random

from typing import Union

import pyautogui as pg
from docopt import docopt

class MousePos:

    DEFAULT_IDLE_DT = 10.0
    SX=50.0
    SY=50.0

    def __init__(self, idle_dt=DEFAULT_IDLE_DT):
        self.x = 0
        self.y = 0
        self.t = 0

        self.x0 = 0
        self.y0 = 0
        self.t0 = 0

        self.idle_dt = idle_dt

        self.update()

    def get_xyt(self):
        x,y = pg.position()
        t = time.perf_counter()
        return x,y,t
    def update(self):
        self.x, self.y, self.t = self.get_xyt()


    def update_0(self, update_t:bool=True):
        self.x0, self.y0, t0 = self.get_xyt()
        if update_t:
            self.t0 = t0


    def is_idle(self)->bool:
        self.update()
        
        dt = self.t - self.t0
        if self.x==self.x0 and self.y==self.y0:
            if dt > self.idle_dt:
                self.update_0()            
                return True
        else:
            self.update_0()            
        return False

    def move(self):
        w,h = pg.size()
        dx,dy = 0,0
        while True:
            dx=round(random.normalvariate(0.0,self.SX))
            dy=round(random.normalvariate(0.0,self.SY))

            x = self.x + dx
            y = self.y + dy

            if (dx!=0 or dy!=0) and x>0 and x<w and y>0 and y<h:
                break

        t=random.uniform(0.061,0.161)
        print(f"moving by ({dx},{dy}) in {t}")

        pg.moveRel(dx,dy,duration=t)


def get_files(path:str):
    for root, dirs, files in os.walk(path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext==".py":
                filename = os.path.join(root, file)
                yield filename
        for d in dirs:
            sub_path = os.path.join(root,d)
            get_files(path=sub_path)

def main(**kwargs: Union[dict,list]):
    """Entry point for fstail

    :param kwargs: if provided, is a list of parameters by docopt, otherwise, docopt will take them from sys.argv
    :type kwargs: Dict or List
    :return:
    :rtype:
    """
    args = docopt(doc=__doc__, **kwargs)
    dt = float(args["--dt"])
    path = args["--path"].replace("~",os.environ["HOME"])

    mouse = MousePos(idle_dt=dt)
    for x in get_files(path):
        with open(x) as fp:
            for raw_line in fp.readlines():
                line = raw_line[:-1] if raw_line.endswith("\n") else raw_line
                print(line)
                time.sleep(0.05)

                if mouse.is_idle():
                    mouse.move()



if __name__ == "__main__":
    main()
