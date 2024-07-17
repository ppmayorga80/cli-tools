"""logout app

Usage:
    tout.py [--accelerate=K] [--progress] <SECONDS>

Arguments:
    <SECONDS>   the number of seconds to wait before logout, use the format
                S or M:S or H:M:S

Options:
    -p, --progress  show a progress bar
    -a,--accelerate=K   speed up the timer [default: 1.0]


Examples:
    tout.py 3601    #1hr + 1 sec
    tout.py 1:12    #1min + 12 sec
    tout.py 0:1:12  #1min + 12 sec
    tout.py 1:2:3   #1hr + 2 min + 3 sec
"""
import os
import re
import time

from docopt import docopt
from tqdm import tqdm


def sec2time(seconds:int)->tuple[int,int,int]:
    s = seconds % 60
    m = (seconds// 60)%60
    h = seconds // 3600
    return h,m,s


def main(**kwargs: dict or list):
    args = docopt(doc=__doc__, **kwargs)
    k = float(args['--accelerate'])

    response = re.findall(r'^(\d+)$', args['<SECONDS>'])
    if response:
        seconds = int(response[0])
    else:
        response = re.findall(r'^(\d+):(\d+)$', args['<SECONDS>'])
        if response:
            a,b = response[0]
            seconds = 60*int(a) + int(b)
        else:
            response = re.findall(r'^(\d+):(\d+):(\d+)$', args['<SECONDS>'])
            if response:
                a, b, c = response[0]
                seconds = 3600 * int(a) + 60*int(b) + int(c)
            else:
               raise ValueError(f"<SECONDS> argument is not valid")

    if not args["--progress"]:
        time.sleep(seconds)
    else:
        h, m, s = sec2time(seconds)
        bh = tqdm(desc="Hours__", total=h, unit="hrs", position=0, leave=False)
        bm = tqdm(desc="Minutes", total=60, unit="min", position=1, leave=False)
        bs = tqdm(desc="Seconds", total=60, unit="sec", position=2, leave=False)

        bh.n = h
        bm.n = m
        bs.n = s
        bh.refresh()
        bm.refresh()
        bs.refresh()

        for x in range(seconds,0,-1):
            time.sleep(1.0 / k)
            h,m,s = sec2time(x-1)
            bh.n = h
            bm.n = m
            bs.n = s
            bh.refresh()
            bm.refresh()
            bs.refresh()


if __name__ == '__main__':
    main()
