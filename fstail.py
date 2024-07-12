"""execute a tail command for a given cloud file (actually any cloud file) or local file

Usage:
  fstail [-n LINES] <FILENAME>

Options:
    -n LINES                set the limit of tail-lines to be processed [default: 10], should be a positive value.
    <FILENAME>              input filename to be processed (local or cloud)
"""
from typing import Dict, List, Type

import smart_open
from docopt import docopt
from tqdm import tqdm


def str2num(text: str, default=None, class_type: Type = int):
    val = default
    try:
        val = class_type(eval(text))
    except TypeError:
        pass
    except NameError:
        pass
    return val


def tail(filename: str, n: int = 10):
    """prints the tail-lines (default 10) of the given file `filename`

    :param filename: the local or cloud file
    :type filename: str
    :param n: the number of lines to be printed (default=10)
    :type n: int
    :return: nothing
    :rtype: None
    """
    # use a buffer to save the last `n` lines
    lines = []
    with smart_open.open(filename) as fp:
        # A. read the file line by line
        for line in tqdm(fp, desc="reading...", leave=False):
            # A.1 delete the first element to maintain only the last `n` lines
            if len(lines) == n:
                del lines[0]
            # A.2 add the last processed line
            lines.append(line)

        # B. print the output
        for line in lines:
            end = "" if str(line).endswith("\n") else "\n"
            print(line, end=end)


def main(**kwargs: Dict or List):
    """Entry point for fstail

    :param kwargs: if provided, is a list of parameters by docopt, otherwise, docopt will take them from sys.argv
    :type kwargs: Dict or List
    :return:
    :rtype:
    """
    arguments = docopt(doc=__doc__, **kwargs)

    arg_filename = arguments["<FILENAME>"]
    arg_n = arguments["-n"]
    n = str2num(arg_n, default=None, class_type=int)
    if n is None or n < 1:
        raise ValueError("-n N must be an integer number greater than 0")

    tail(arg_filename, n)


if __name__ == '__main__':
    main()
