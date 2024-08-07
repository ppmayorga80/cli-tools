"""execute the head command for a cloud file (actually any cloud file) or local file

Usage:
  pyhead [-n LINES]
  pyhead [-n LINES] <FILENAME>

Options:
    -n LINES                set the limit of head-lines to be processed [default: 10], should be a positive value.
    <FILENAME>              input filename to be processed (local or cloud)
"""
import sys
from typing import Dict, List, Type, IO

import smart_open
from docopt import docopt


def str2num(text: str, default=None, class_type: Type = int):
    val = default
    try:
        val = class_type(eval(text))
    except TypeError:
        pass
    except NameError:
        pass
    return val


def head(fp: IO, n: int = 10):
    """prints the head-lines (default 10) of the given file `filename`

    :param filename: the local or cloud file
    :type filename: str
    :param n: the number of lines to be printed (default=10)
    :type n: int
    :return: nothing
    :rtype: None
    """
    # open the file and only walk over the first n lines or when the file ends
    for _, line in zip(range(n), fp):
        # end = "" if str(line).endswith("\n") else "\n"
        print(line, end="")


def main(**kwargs: Dict or List):
    """entry point for pyhead program

    :param kwargs: if defined, contains a list of parameters parsed by docopt
                   for example argv=['-n','5']
                   otherwise docopt will take it from sys.argv
    :type kwargs: Dict or List
    :return: nothing
    :rtype: None
    """
    arguments = docopt(doc=__doc__, **kwargs)

    arg_filename = arguments["<FILENAME>"]
    arg_n = arguments["-n"]
    n = str2num(arg_n, default=None, class_type=int)
    if n is None or n < 1:
        raise ValueError("-n N must be an integer number greater than 0")

    fp = smart_open.smart_open(arg_filename, "r") if arg_filename is not None else sys.stdin
    head(fp, n)


if __name__ == '__main__':
    main()
