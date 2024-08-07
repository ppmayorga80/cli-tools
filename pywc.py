"""execute the wc command for a cloud file (actually any cloud file) or local file

Usage:
  pywc [--jsonl] [-L|-c|-l|-w]
  pywc [--jsonl] [-L|-c|-l|-w] <FILENAME>

Arguments:
    <FILENAME>              input filename to be processed (local, cloud)

Options:
    -L              write the longest length of the lines
    -c              write the total number of bytes (default)
    -l              write the total number of lines
    -w              write the total number of words
    -j,--jsonl      read jsonl file, i.e. avoid empty lines
"""
import re
import sys

import smart_open
from docopt import docopt
from typing import Optional, IO


def wc_longest_line(fp: IO, is_jsonl: bool = False) -> str:
    """WC operation of given filename"""
    max_length = 0
    for line_k in fp:
        # avoid empty lines only if a jsonl flag is active
        if is_jsonl and not line_k.strip():
            continue
        length = len(line_k) - (1 if line_k.endswith("\n") else 0)
        max_length = max(max_length, length)
    return max_length


def wc_total_bytes(fp: IO, is_jsonl: bool = False):
    """WC operation of given filename"""
    total = 0
    for line_k in fp:
        # avoid empty lines only if a jsonl flag is active
        if is_jsonl and not line_k.strip():
            continue
        total += len(line_k)
    return total


def wc_total_lines(fp: IO, is_jsonl: bool = False):
    """WC operation of given filename"""
    total = 0
    for line_k in fp:
        # avoid empty lines only if a jsonl flag is active
        if is_jsonl and not line_k.strip():
            continue
        total += 1
    return total


def wc_total_words(fp: IO, is_jsonl: bool = False):
    """WC operation of given filename"""
    regex = re.compile(r"\b\w+\b")
    total = 0
    for line_k in fp:
        # avoid empty lines only if a jsonl flag is active
        if is_jsonl and not line_k.strip():
            continue
        response = regex.findall(line_k)
        total += len(response)
    return total


def main(**kwargs):
    args = docopt(doc=__doc__, **kwargs)

    fp = smart_open.smart_open(args['<FILENAME>'], 'r') if args['<FILENAME>'] is not None else sys.stdin

    if args["-L"]:
        response = wc_longest_line(fp, is_jsonl=args["--jsonl"])
    elif args["-c"]:
        response = wc_total_bytes(fp, is_jsonl=args["--jsonl"])
    elif args["-l"]:
        response = wc_total_lines(fp, is_jsonl=args["--jsonl"])
    elif args["-w"]:
        response = wc_total_words(fp, is_jsonl=args["--jsonl"])
    else:
        # default option
        response = wc_total_bytes(fp, is_jsonl=args["--jsonl"])

    print(response)


if __name__ == '__main__':
    main()
