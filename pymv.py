"""run the mv command recursivelly with regex
Consider regex groups as:
"^(HE)(.*)(O)$" "\\g<1>LL\\g<3>"
will replace all the followings with "HELLO":
 "HEXXO"
 "HEXXXXXO"


Usage:
  pymv [--apply] [--only-files] [--only-dir] <ROOT> <REGEX> <SUB>

Arguments:
    <ROOT>               root directory to search
    <REGEX>              regex expression to match
    <SUB>                substitution string

Options:
    -a,--apply           use it when you are certain to run the mv
"""
import os
import re
import sys
import smart_open
from tqdm import tqdm
from docopt import docopt
from typing import Optional


def searching_files(root, only_files=True, only_dir=False):
    files_set = []
    dirs_set = []
    for root, dirs, files in tqdm(os.walk(root), desc="# Searching files..."):
        if only_dir:
            for d in dirs:
                dirs_set.append(("dir", os.path.join(root, d)))
        if only_files:
            for f in files:
                files_set.append(("files", os.path.join(root, f)))

    # process in reverse order to avoid issues with renaming dirs
    # process first files and then dirs
    success_set = files_set[::-1] + dirs_set[::-1]
    return success_set


def main(**kwargs):
    args = docopt(doc=__doc__, **kwargs)

    arg_apply = args["--apply"]
    only_files = args["--only-files"]
    only_dir = args["--only-dir"]
    arg_regex = args["<REGEX>"]
    arg_sub = args["<SUB>"]
    arg_root = args["<ROOT>"]

    if (not only_files) and (not only_dir):
        only_files = True
        only_dir = True

    files = searching_files(arg_root, only_dir=only_dir, only_files=only_files)
    regex = re.compile(arg_regex)
    files = [(k, x, regex.sub(arg_sub, x)) for k, x in files]
    files = [(k, x, y) for k, x, y in files if x != y]

    commands = [f"mv \"{x}\" \"{y}\"" for k, x, y in files]
    if not arg_apply:
        print("\n".join(commands))
    else:
        for cmd in tqdm(commands, desc="# Running mv...", total=len(commands)):
            os.system(cmd)


if __name__ == '__main__':
    main()
