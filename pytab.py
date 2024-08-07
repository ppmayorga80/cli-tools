"""print CSV with rainbow colors using TABULATE

Usage:
  pytab [--colors NAMES]
  pytab [--colors NAMES] <FILENAME>

Arguments:
    <FILENAME>              input filename to be processed (local, cloud) use a single dash to use stdin [default: -]


Options:
    --colors=NAMES          separated color names (separator is a comma without spaces)
                            [default: cyan,yellow,magenta,white,lightred,lightgreen,lightblue]
                            available color names are: red,green,blue,cyan,magenta,yellow,white,black
                            and "light" prefix version of them like "lightred" or "lightcyan"
"""

import sys
from itertools import cycle
from typing import IO, List

import smart_open
import pandas as pd
from docopt import docopt
from tabulate import tabulate

from utils.cprint import cformat

default_color_list = [
    "cyan", "yellow", "magenta", "white", "lightred", "lightgreen", "lightblue"
]


def fs_tabulate(fp: IO, color_list: List[str] = None) -> str:
    """given the input file (as a pointer) and a list of colors (none to take a default list)
    this program gives you the tabulated and colorized version of that table

    :param fp: input file opinter
    :type fp: IO
    :param color_list: list of valid color to iterate on every column
    :type color_list: List[str]
    :return: the tabulated string colorized by columns
    :rtype: str
    """
    color_list = default_color_list if color_list is None else color_list
    df = pd.read_csv(fp)
    columns = df.columns
    values: List[List[str]] = df.values.tolist()

    colored_columns = [
        cformat(column, fg_color=color, style="BRIGHT")
        for color, column in zip(cycle(color_list), columns)
    ]
    colored_values = [[
        cformat(cell, fg_color=color, style="NORMAL")
        for color, cell in zip(cycle(color_list), row)
    ] for row in values]

    text = tabulate(colored_values, headers=colored_columns)
    return text


def main(**kwargs):
    """Entry point"""
    # read parameters
    args = docopt(doc=__doc__, **kwargs)
    # read list of colors
    colors = args["--colors"].split(",")
    filename = args["<FILENAME>"]

    # consider - as a stdin
    if filename is None or filename == "-":
        fp = sys.stdin
    else:
        fp = smart_open.open(filename, "r", encoding="utf8")

    # compute colorized version of tabulate
    fmt = fs_tabulate(fp, color_list=colors)

    # print
    print(fmt)


if __name__ == '__main__':
    main()
