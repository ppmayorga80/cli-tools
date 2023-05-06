"""execute the cat command for a cloud file (actually any cloud file) or local file

Usage:
  fscat <FILENAME>

Options:
    <FILENAME>              input filename to be processed (local, cloud)

"""
import smart_open
from docopt import docopt


def cat(filename: str):
    """Cat operation of given filename

    :param filename:
    :type filename:
    :return:
    :rtype:
    """
    with smart_open.open(filename) as fp:
        for line in fp:
            end = "" if str(line).endswith("\n") else "\n"
            print(line, end=end)


def main(**kwargs):
    arguments = docopt(doc=__doc__, **kwargs)

    arg_filename = arguments["<FILENAME>"]
    cat(arg_filename)


if __name__ == '__main__':
    main()
