"""execute the cat command for a cloud file (actually any cloud file) or local file

Usage:
  fscat [--offset=A] [--limit=N] <FILENAME>

Arguments:
    <FILENAME>              input filename to be processed (local, cloud)

Options:
    -o,--offset=A           start reading from line A [default: 0]
    -n,--limit=N            only reads up to N lines

"""
import smart_open
from docopt import docopt
from typing import Optional


def cat(filename: str, offset:int=0, limit:Optional[int]=None):
    """Cat operation of given filename"""
    with smart_open.open(filename) as fp:
        for k,line_k in enumerate(fp):
            if k<offset:
                continue
            if limit and k>=offset+limit:
                break
            end = "" if str(line_k).endswith("\n") else "\n"
            print(line_k, end=end)


def main(**kwargs):
    arguments = docopt(doc=__doc__, **kwargs)

    arg_filename = arguments["<FILENAME>"]
    arg_offset = int(arguments["--offset"])
    arg_limit = int(arguments["--limit"]) if arguments["--limit"] else None
    cat(arg_filename, offset=arg_offset, limit=arg_limit)


if __name__ == '__main__':
    main()
