"""execute the cat command for a cloud file (actually any cloud file) or local file

Usage:
  pycat [--jsonl] [--offset=A] [--limit=N] <FILENAME>
  pycat [--jsonl] [--offset=A] [--limit=N]

Arguments:
    <FILENAME>              input filename to be processed (local, cloud)

Options:
    -o A, --offset=A           start reading from line A [default: 0]
    -l N, --limit=N            only reads up to N lines
    -j, --jsonl                read a jsonl file, i.e. avoid empty lines
"""
import sys

import smart_open
from docopt import docopt
from typing import Optional


def cat(filename: Optional[str], offset: int = 0, limit: Optional[int] = None, is_jsonl: bool = False):
    """Cat operation of given filename"""
    if filename is None:
        fp = sys.stdin
    else:
        fp = smart_open.open(filename)

    for k, line_k in enumerate(fp):
        if k < offset:
            continue
        if limit and k >= offset + limit:
            break
        # avoid empty lines only if a jsonl flag is active
        if is_jsonl and not line_k.strip():
            continue
        end = "" if str(line_k).endswith("\n") else "\n"
        print(line_k, end=end)

    fp.close()


def main(**kwargs):
    args = docopt(doc=__doc__, **kwargs)

    arg_filename = args["<FILENAME>"]
    arg_offset = int(args["--offset"])
    arg_limit = int(args["--limit"]) if args["--limit"] else None
    cat(arg_filename, offset=arg_offset, limit=arg_limit, is_jsonl=args["--jsonl"])


if __name__ == '__main__':
    main()
